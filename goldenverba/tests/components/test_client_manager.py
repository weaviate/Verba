"""
test_client_manager.py
======================
Unit tests for ClientManager.

Strategy: instantiate a real ClientManager, then replace self.manager with a
MagicMock so no real Weaviate connections are opened. WeaviateAsyncClient
instances in the pool are also MagicMocks with AsyncMock.is_ready().

Groups:
  1. hash_credentials      — deterministic, credential-isolated hashing
  2. get_or_create_lock    — idempotent lock creation
  3. connect               — cache hit, cache miss, env-var fallback
  4. disconnect            — closes all pooled clients
  5. clean_up              — evicts stale-by-time and unhealthy clients
"""

import asyncio
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from goldenverba.components.client_manager import ClientManager
from goldenverba.server.types import Credentials


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _creds(deployment="Weaviate", url="https://example.weaviate.network", key="secret"):
    return Credentials(deployment=deployment, url=url, key=key)


def _mock_weaviate_client(ready=True):
    client = MagicMock()
    client.is_ready = AsyncMock(return_value=ready)
    return client


@pytest.fixture
def cm():
    """ClientManager with VerbaManager replaced by a MagicMock."""
    manager = ClientManager()
    manager.manager = MagicMock()
    return manager


# ---------------------------------------------------------------------------
# 1. hash_credentials
# ---------------------------------------------------------------------------


class TestHashCredentials:
    def test_same_credentials_produce_same_hash(self, cm):
        creds = _creds()
        assert cm.hash_credentials(creds) == cm.hash_credentials(creds)

    def test_different_url_produces_different_hash(self, cm):
        a = _creds(url="https://a.example.com")
        b = _creds(url="https://b.example.com")
        assert cm.hash_credentials(a) != cm.hash_credentials(b)

    def test_different_key_produces_different_hash(self, cm):
        a = _creds(key="key-a")
        b = _creds(key="key-b")
        assert cm.hash_credentials(a) != cm.hash_credentials(b)

    def test_different_deployment_produces_different_hash(self, cm):
        a = _creds(deployment="Weaviate")
        b = _creds(deployment="Docker")
        assert cm.hash_credentials(a) != cm.hash_credentials(b)

    def test_hash_is_64_char_hex(self, cm):
        h = cm.hash_credentials(_creds())
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# 2. get_or_create_lock
# ---------------------------------------------------------------------------


class TestGetOrCreateLock:
    def test_returns_asyncio_lock(self, cm):
        lock = cm.get_or_create_lock("abc")
        assert isinstance(lock, asyncio.Lock)

    def test_same_key_returns_same_lock(self, cm):
        lock1 = cm.get_or_create_lock("abc")
        lock2 = cm.get_or_create_lock("abc")
        assert lock1 is lock2

    def test_different_keys_return_different_locks(self, cm):
        lock1 = cm.get_or_create_lock("abc")
        lock2 = cm.get_or_create_lock("xyz")
        assert lock1 is not lock2


# ---------------------------------------------------------------------------
# 3. connect
# ---------------------------------------------------------------------------


class TestConnect:
    @pytest.mark.asyncio
    async def test_cache_miss_opens_new_connection(self, cm):
        fake_client = _mock_weaviate_client()
        cm.manager.connect = AsyncMock(return_value=fake_client)
        creds = _creds()

        result = await cm.connect(creds)

        assert result is fake_client
        cm.manager.connect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cache_hit_returns_existing_client(self, cm):
        fake_client = _mock_weaviate_client()
        cm.manager.connect = AsyncMock(return_value=fake_client)
        creds = _creds()

        # First call stores it; second call should reuse.
        first = await cm.connect(creds)
        second = await cm.connect(creds)

        assert first is second
        # manager.connect only called once despite two cm.connect calls
        cm.manager.connect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_different_credentials_open_separate_connections(self, cm):
        client_a = _mock_weaviate_client()
        client_b = _mock_weaviate_client()
        cm.manager.connect = AsyncMock(side_effect=[client_a, client_b])

        result_a = await cm.connect(_creds(key="key-a"))
        result_b = await cm.connect(_creds(key="key-b"))

        assert result_a is client_a
        assert result_b is client_b
        assert cm.manager.connect.await_count == 2

    @pytest.mark.asyncio
    async def test_env_var_fallback_when_empty_credentials(self, cm):
        fake_client = _mock_weaviate_client()
        cm.manager.connect = AsyncMock(return_value=fake_client)
        empty_creds = _creds(url="", key="")

        with patch.dict(os.environ, {
            "WEAVIATE_URL_VERBA": "https://env.weaviate.network",
            "WEAVIATE_API_KEY_VERBA": "env-key",
        }):
            await cm.connect(empty_creds)

        # The credentials passed to manager.connect should use the env values.
        called_creds = cm.manager.connect.call_args.args[0]
        assert called_creds.url == "https://env.weaviate.network"
        assert called_creds.key == "env-key"

    @pytest.mark.asyncio
    async def test_connect_does_not_mutate_caller_credentials(self, cm):
        cm.manager.connect = AsyncMock(return_value=_mock_weaviate_client())
        original_url = ""
        creds = _creds(url=original_url, key="")

        with patch.dict(os.environ, {"WEAVIATE_URL_VERBA": "https://env.example.com"}):
            await cm.connect(creds)

        # Caller's object should be unchanged.
        assert creds.url == original_url


# ---------------------------------------------------------------------------
# 4. disconnect
# ---------------------------------------------------------------------------


class TestDisconnect:
    @pytest.mark.asyncio
    async def test_disconnects_all_clients(self, cm):
        client_a = _mock_weaviate_client()
        client_b = _mock_weaviate_client()
        cm.manager.disconnect = AsyncMock()
        cm.clients = {
            "hash-a": {"client": client_a, "timestamp": datetime.now()},
            "hash-b": {"client": client_b, "timestamp": datetime.now()},
        }

        await cm.disconnect()

        assert cm.manager.disconnect.await_count == 2
        disconnected = {call.args[0] for call in cm.manager.disconnect.call_args_list}
        assert client_a in disconnected
        assert client_b in disconnected

    @pytest.mark.asyncio
    async def test_disconnect_with_empty_pool_is_a_noop(self, cm):
        cm.manager.disconnect = AsyncMock()
        await cm.disconnect()
        cm.manager.disconnect.assert_not_called()


# ---------------------------------------------------------------------------
# 5. clean_up
# ---------------------------------------------------------------------------


class TestCleanUp:
    @pytest.mark.asyncio
    async def test_removes_stale_client_by_time(self, cm):
        stale_client = _mock_weaviate_client(ready=True)
        cm.manager.disconnect = AsyncMock()
        old_timestamp = datetime.now() - timedelta(minutes=cm.max_time + 1)
        cm.clients = {
            "stale": {"client": stale_client, "timestamp": old_timestamp},
        }

        await cm.clean_up()

        assert "stale" not in cm.clients
        cm.manager.disconnect.assert_awaited_once_with(stale_client)

    @pytest.mark.asyncio
    async def test_removes_unhealthy_client(self, cm):
        unhealthy_client = _mock_weaviate_client(ready=False)
        cm.manager.disconnect = AsyncMock()
        cm.clients = {
            "unhealthy": {"client": unhealthy_client, "timestamp": datetime.now()},
        }

        await cm.clean_up()

        assert "unhealthy" not in cm.clients
        cm.manager.disconnect.assert_awaited_once_with(unhealthy_client)

    @pytest.mark.asyncio
    async def test_keeps_fresh_healthy_client(self, cm):
        healthy_client = _mock_weaviate_client(ready=True)
        cm.manager.disconnect = AsyncMock()
        cm.clients = {
            "healthy": {"client": healthy_client, "timestamp": datetime.now()},
        }

        await cm.clean_up()

        assert "healthy" in cm.clients
        cm.manager.disconnect.assert_not_called()

    @pytest.mark.asyncio
    async def test_mixed_pool_only_removes_bad_clients(self, cm):
        good_client = _mock_weaviate_client(ready=True)
        bad_client = _mock_weaviate_client(ready=False)
        cm.manager.disconnect = AsyncMock()
        cm.clients = {
            "good": {"client": good_client, "timestamp": datetime.now()},
            "bad": {"client": bad_client, "timestamp": datetime.now()},
        }

        await cm.clean_up()

        assert "good" in cm.clients
        assert "bad" not in cm.clients
        cm.manager.disconnect.assert_awaited_once_with(bad_client)

    @pytest.mark.asyncio
    async def test_empty_pool_clean_up_is_a_noop(self, cm):
        cm.manager.disconnect = AsyncMock()
        await cm.clean_up()
        cm.manager.disconnect.assert_not_called()
