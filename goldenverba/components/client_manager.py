"""
client_manager.py
=================
Connection pool for Weaviate clients, isolated from VerbaManager so each module
stays focused on a single responsibility.

  ClientManager — maps hashed credentials → live WeaviateAsyncClient.
                  Concurrent requests with the same credentials share one connection.
                  A per-credential asyncio.Lock prevents duplicate connections
                  from opening in a race condition.

Stale connections (idle > max_time minutes, or no longer responsive) are evicted
by clean_up(), which the /api/health endpoint triggers periodically.
"""

import os
import asyncio
import hashlib
from datetime import datetime

from wasabi import msg
from weaviate.client import WeaviateAsyncClient

from goldenverba.server.types import Credentials
from goldenverba.components.verba_manager import VerbaManager


class ClientManager:
    """
    Connection pool for Weaviate clients.

    Each unique set of credentials (deployment + URL + API key) maps to one
    live WeaviateAsyncClient. The internal VerbaManager instance handles
    the actual connection logic and all pipeline operations.
    """

    def __init__(self) -> None:
        # {cred_hash: {"client": WeaviateAsyncClient, "timestamp": datetime}}
        self.clients: dict[str, dict] = {}
        self.manager: VerbaManager = VerbaManager()
        self.max_time: int = 10  # minutes before an idle client is evicted
        self.locks: dict[str, asyncio.Lock] = {}

    def hash_credentials(self, credentials: Credentials) -> str:
        """Stable cache key derived from credentials; never stored or logged."""
        cred_string = f"{credentials.deployment}:{credentials.url}:{credentials.key}"
        return hashlib.sha256(cred_string.encode()).hexdigest()

    def get_or_create_lock(self, cred_hash: str) -> asyncio.Lock:
        """
        Return the per-credential lock, creating it if needed.
        dict.setdefault() is atomic for dict operations, preventing a race where
        two coroutines both see the key absent and create separate locks.
        """
        self.locks.setdefault(cred_hash, asyncio.Lock())
        return self.locks[cred_hash]

    def heartbeat(self):
        """Log the current connected-client count (debug aid)."""
        msg.info(f"{len(self.clients)} clients connected")
        for cred_hash, client in self.clients.items():
            msg.info(f"Client {cred_hash} connected at {client['timestamp']}")

    async def connect(
        self, credentials: Credentials, port: str = "8080"
    ) -> WeaviateAsyncClient:
        """
        Return a live WeaviateAsyncClient for the given credentials.

        Returns an existing cached client if one exists; otherwise opens a new
        connection under the per-credential lock to prevent duplicates.
        Falls back to WEAVIATE_URL_VERBA / WEAVIATE_API_KEY_VERBA env vars when
        the caller passes empty credentials (default deployment mode).
        """
        # Work on a copy so we never mutate the caller's object.
        _credentials = credentials.model_copy()

        if not _credentials.url and not _credentials.key:
            _credentials.url = os.environ.get("WEAVIATE_URL_VERBA", "")
            _credentials.key = os.environ.get("WEAVIATE_API_KEY_VERBA", "")

        cred_hash = self.hash_credentials(_credentials)

        lock = self.get_or_create_lock(cred_hash)
        async with lock:
            if cred_hash in self.clients:
                msg.info("Found existing Client")
                return self.clients[cred_hash]["client"]
            else:
                msg.warn("Connecting new Client")
                client = await self.manager.connect(_credentials, port)
                self.clients[cred_hash] = {
                    "client": client,
                    "timestamp": datetime.now(),
                }
                return client

    async def disconnect(self):
        """Gracefully close all cached connections."""
        msg.warn("Disconnecting Clients!")
        # Snapshot keys to avoid mutating the dict during iteration.
        for cred_hash in list(self.clients.keys()):
            await self.manager.disconnect(self.clients[cred_hash]["client"])

    async def clean_up(self):
        """
        Evict stale clients: those idle longer than max_time minutes, or whose
        Weaviate connection is no longer healthy. Called by the /api/health endpoint.
        """
        msg.info("Cleaning Clients Cache")
        current_time = datetime.now()
        clients_to_remove = []

        # Snapshot to avoid RuntimeError if the dict changes concurrently.
        for cred_hash, client_data in list(self.clients.items()):
            time_difference = current_time - client_data["timestamp"]
            if time_difference.total_seconds() / 60 > self.max_time:
                clients_to_remove.append(cred_hash)
                continue
            client: WeaviateAsyncClient = client_data["client"]
            if not await client.is_ready():
                clients_to_remove.append(cred_hash)

        for cred_hash in clients_to_remove:
            if cred_hash in self.clients:
                await self.manager.disconnect(self.clients[cred_hash]["client"])
                del self.clients[cred_hash]
                msg.warn(f"Removed client: {cred_hash}")

        msg.info(f"Cleaned up {len(clients_to_remove)} clients")
        self.heartbeat()
