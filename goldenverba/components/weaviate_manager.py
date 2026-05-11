"""
weaviate_manager.py
===================
Low-level Weaviate client wrapper for Verba.

Owns all direct interactions with the Weaviate async client: connections,
collection management, document/chunk CRUD, vector queries, suggestions,
and configuration storage.

Collection layout
-----------------
VERBA_DOCUMENTS          — one record per imported file (title, meta, labels)
VERBA_CONFIGURATION      — three records: RAG config, theme config, user config
VERBA_SUGGESTIONS        — autocomplete query history
VERBA_Embedding_<model>  — one collection per embedder model (chunks + vectors)
VERBA_Cache_<model>      — semantic-cache entries per embedder model

Deployment modes
----------------
"Weaviate" — Weaviate Cloud (URL + API key required)
"Docker"   — local Docker Compose instance (default host: localhost or WEAVIATE_HOST env var)
"Custom"   — any reachable Weaviate instance with optional auth
"""

from wasabi import msg

import weaviate
from weaviate.client import WeaviateAsyncClient
from weaviate.classes.query import Filter, Sort, MetadataQuery
from weaviate.collections.classes.data import DataObject
from weaviate.classes.aggregate import GroupByAggregate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from weaviate.classes.config import Property, DataType

import os
import asyncio
import json
import re
from datetime import datetime

from sklearn.decomposition import PCA

from goldenverba.components.document import Document


class WeaviateManager:
    """Low-level Weaviate client wrapper. See module docstring for full details."""

    # Shared timeout config applied to all connection types.
    # stream=300 covers long-running streaming generation responses.
    _TIMEOUT = AdditionalConfig(
        timeout=Timeout(init=60, query=300, insert=300, stream=300)
    )

    # Property schemas for each named collection.
    # Defined here so verify_collection can create collections with the correct
    # schema on first use — without needing callers to pass properties manually.
    _DOCUMENT_PROPERTIES = [
        Property(name="title", data_type=DataType.TEXT),
        Property(name="content", data_type=DataType.TEXT),
        Property(name="extension", data_type=DataType.TEXT),
        Property(name="fileSize", data_type=DataType.NUMBER),
        Property(name="labels", data_type=DataType.TEXT_ARRAY),
        Property(name="source", data_type=DataType.TEXT),
        Property(name="meta", data_type=DataType.TEXT),
        Property(name="metadata", data_type=DataType.TEXT),
    ]
    _CONFIG_PROPERTIES = [
        Property(name="config", data_type=DataType.TEXT),
    ]
    _SUGGESTION_PROPERTIES = [
        Property(name="query", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.TEXT),
    ]
    _CHUNK_PROPERTIES = [
        Property(name="content", data_type=DataType.TEXT),
        Property(name="chunk_id", data_type=DataType.INT),
        Property(name="doc_uuid", data_type=DataType.TEXT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="pca", data_type=DataType.NUMBER_ARRAY),
        Property(name="start_i", data_type=DataType.INT),
        Property(name="end_i", data_type=DataType.INT),
        Property(name="content_without_overlap", data_type=DataType.TEXT),
        Property(name="labels", data_type=DataType.TEXT_ARRAY),
    ]

    def __init__(self):
        self.document_collection_name = "VERBA_DOCUMENTS"
        self.config_collection_name = "VERBA_CONFIGURATION"
        self.suggestion_collection_name = "VERBA_SUGGESTIONS"

        # Maps embedder model name → Weaviate collection name.
        # Populated lazily on first use of each embedder.
        self.embedding_table: dict[str, str] = {}

        # Separate table for cache collections so verify_cache_collection and
        # verify_embedding_collection never clobber each other's entries.
        self.cache_table: dict[str, str] = {}

        # Per-client set of collection names already confirmed to exist.
        # Avoids a network round-trip on every operation; keyed by id(client).
        self._verified_collections: dict[int, set[str]] = {}

    # -------------------------------------------------------------------------
    # Connection factories
    # -------------------------------------------------------------------------

    def connect_to_cluster(self, w_url: str, w_key: str) -> WeaviateAsyncClient:
        """Connect to Weaviate Cloud. Both URL and API key are required."""
        if not w_url or not w_key:
            raise Exception("No URL or API Key provided")
        msg.info(f"Connecting to Weaviate Cluster {w_url} with Auth")
        return weaviate.use_async_with_weaviate_cloud(
            cluster_url=w_url,
            auth_credentials=Auth.api_key(w_key),
            additional_config=self._TIMEOUT,
        )

    def connect_to_docker(self, host: str = "localhost") -> WeaviateAsyncClient:
        """
        Connect to a local Weaviate Docker instance.

        Host defaults to localhost for local dev. In Docker Compose the service
        name ("weaviate") is resolved by Docker DNS, so pass that explicitly.
        Falls back to the WEAVIATE_HOST env var if set and no host is given.
        """
        resolved_host = host or os.environ.get("WEAVIATE_HOST", "localhost")
        msg.info(f"Connecting to Weaviate Docker at {resolved_host}")
        return weaviate.use_async_with_local(
            host=resolved_host,
            additional_config=self._TIMEOUT,
        )

    def connect_to_custom(
        self, host: str, w_key: str, port: str
    ) -> WeaviateAsyncClient:
        """Connect to any reachable Weaviate instance with optional API key auth."""
        if not host:
            raise Exception("No Host URL provided")
        msg.info(f"Connecting to Weaviate Custom at {host}:{port}")
        kwargs = dict(
            host=host,
            port=int(port),
            skip_init_checks=True,
            additional_config=self._TIMEOUT,
        )
        if w_key:
            kwargs["auth_credentials"] = Auth.api_key(w_key)
        return weaviate.use_async_with_local(**kwargs)

    async def connect(
        self, deployment: str, weaviateURL: str, weaviateAPIKey: str, port: str = "8080"
    ) -> WeaviateAsyncClient:
        """
        Create and connect a WeaviateAsyncClient for the given deployment type.

        Supported deployments:
          "Weaviate" — Weaviate Cloud (WEAVIATE_URL_VERBA / WEAVIATE_API_KEY_VERBA)
          "Docker"   — local Docker instance (WEAVIATE_HOST or localhost:8080)
          "Custom"   — user-supplied host + optional API key

        Raises on any connection failure so ClientManager can surface the error.
        """
        try:
            if deployment == "Weaviate":
                # Fall back to env vars if the frontend sent empty strings.
                weaviateURL = weaviateURL or os.environ.get("WEAVIATE_URL_VERBA", "")
                weaviateAPIKey = weaviateAPIKey or os.environ.get(
                    "WEAVIATE_API_KEY_VERBA", ""
                )
                client = self.connect_to_cluster(weaviateURL, weaviateAPIKey)
            elif deployment == "Docker":
                # In Docker Compose the Weaviate container is reachable as "weaviate".
                # For local dev (outside Compose) localhost is correct.
                client = self.connect_to_docker(
                    os.environ.get("WEAVIATE_HOST", "weaviate")
                )
            elif deployment == "Custom":
                client = self.connect_to_custom(weaviateURL, weaviateAPIKey, port)
            else:
                raise Exception(f"Invalid deployment type: {deployment!r}")

            await client.connect()
            if await client.is_ready():
                msg.good("Successfully Connected to Weaviate")
                return client

            return None

        except Exception as e:
            msg.fail(f"Couldn't connect to Weaviate, check your URL/API KEY: {str(e)}")
            raise Exception(
                f"Couldn't connect to Weaviate, check your URL/API KEY: {str(e)}"
            )

    async def disconnect(self, client: WeaviateAsyncClient):
        """Close the client connection and free gRPC resources."""
        try:
            await client.close()
            # Discard the per-client collection cache so a future reconnect
            # starts fresh (collections may have changed while disconnected).
            self._verified_collections.pop(id(client), None)
            return True
        except Exception as e:
            msg.fail(f"Couldn't disconnect Weaviate: {str(e)}")
            return False

    # -------------------------------------------------------------------------
    # Cluster metadata
    # -------------------------------------------------------------------------

    async def get_metadata(self, client: WeaviateAsyncClient):
        """Return node info and per-collection object counts for the status page."""
        # Node Information
        nodes = await client.cluster.nodes(output="verbose")
        node_payload = {"node_count": 0, "weaviate_version": "", "nodes": []}
        for node in nodes:
            node_payload["nodes"].append(
                {
                    "status": node.status,
                    "shards": len(node.shards),
                    "version": node.version,
                    "name": node.name,
                }
            )
        node_payload["node_count"] = len(nodes)
        node_payload["weaviate_version"] = nodes[0].version

        # Collection Information
        collections = await client.collections.list_all()
        collection_payload = {"collection_count": 0, "collections": []}
        for collection_name in collections:
            collection_objects = await client.collections.use(collection_name).length()
            collection_payload["collections"].append(
                {"name": collection_name, "count": collection_objects}
            )
        collection_payload["collections"].sort(key=lambda x: x["count"], reverse=True)
        collection_payload["collection_count"] = len(collections)

        return node_payload, collection_payload

    # -------------------------------------------------------------------------
    # Collection management
    # -------------------------------------------------------------------------

    async def verify_collection(
        self, client: WeaviateAsyncClient, collection_name: str
    ) -> bool:
        """
        Ensure a collection exists with the correct schema, creating it if needed.

        Results are cached per client so the exists() network call only happens
        once per collection per connection lifetime — not on every operation.

        The schema (property list) is determined automatically from the collection
        name so callers never need to pass schema details.
        """
        client_id = id(client)
        verified = self._verified_collections.setdefault(client_id, set())
        if collection_name in verified:
            return True

        if not await client.collections.exists(collection_name):
            msg.info(f"Collection {collection_name!r} does not exist, creating it.")
            properties = self._schema_for(collection_name)
            await client.collections.create(
                name=collection_name,
                properties=properties,
            )

        verified.add(collection_name)
        return True

    def _schema_for(self, collection_name: str) -> list[Property]:
        """Return the property list for a given collection name."""
        if collection_name == self.document_collection_name:
            return self._DOCUMENT_PROPERTIES
        if collection_name == self.config_collection_name:
            return self._CONFIG_PROPERTIES
        if collection_name == self.suggestion_collection_name:
            return self._SUGGESTION_PROPERTIES
        if collection_name.startswith("VERBA_Embedding_"):
            return self._CHUNK_PROPERTIES
        # Cache collections and any unknown names: no predefined properties.
        return []

    async def verify_embedding_collection(
        self, client: WeaviateAsyncClient, embedder: str
    ) -> bool:
        """Ensure the chunk+vector collection for `embedder` exists, creating it if needed."""
        if embedder not in self.embedding_table:
            self.embedding_table[embedder] = "VERBA_Embedding_" + re.sub(
                r"[^a-zA-Z0-9]", "_", embedder
            )
            return await self.verify_collection(client, self.embedding_table[embedder])
        else:
            return True

    async def verify_cache_collection(
        self, client: WeaviateAsyncClient, embedder: str
    ) -> bool:
        """Ensure the semantic-cache collection for `embedder` exists, creating it if needed."""
        # Use a separate cache_table so this never collides with embedding_table entries
        if embedder not in self.cache_table:
            self.cache_table[embedder] = "VERBA_Cache_" + re.sub(
                r"[^a-zA-Z0-9]", "_", embedder
            )
            return await self.verify_collection(client, self.cache_table[embedder])
        else:
            return True

    async def verify_embedding_collections(
        self, client: WeaviateAsyncClient, environment_variables, libraries
    ):
        # Import here to avoid circular imports (managers.py defines `embedders` at module level)
        from goldenverba.components.embedding.embedding_manager import embedders

        for embedder in embedders:
            if embedder.check_available(environment_variables, libraries):
                if "Model" in embedder.config:
                    for _embedder in embedder.config["Model"].values:
                        self.embedding_table[_embedder] = "VERBA_Embedding_" + re.sub(
                            r"[^a-zA-Z0-9]", "_", _embedder
                        )
                        await self.verify_collection(
                            client, self.embedding_table[_embedder]
                        )

    async def verify_collections(
        self, client: WeaviateAsyncClient, environment_variables, libraries
    ):
        await self.verify_collection(client, self.document_collection_name)
        await self.verify_collection(client, self.suggestion_collection_name)
        await self.verify_collection(client, self.config_collection_name)
        await self.verify_embedding_collections(
            client, environment_variables, libraries
        )
        return True

    # -------------------------------------------------------------------------
    # Configuration storage (RAG config, theme, user prefs)
    # -------------------------------------------------------------------------

    async def get_config(self, client: WeaviateAsyncClient, uuid: str) -> dict:
        if await self.verify_collection(client, self.config_collection_name):
            config_collection = client.collections.use(self.config_collection_name)
            if await config_collection.data.exists(uuid):
                config = await config_collection.query.fetch_object_by_id(uuid)
                return json.loads(config.properties["config"])
            else:
                return None

    async def set_config(self, client: WeaviateAsyncClient, uuid: str, config: dict):
        if await self.verify_collection(client, self.config_collection_name):
            config_collection = client.collections.use(self.config_collection_name)
            if await config_collection.data.exists(uuid):
                if await config_collection.data.delete_by_id(uuid):
                    await config_collection.data.insert(
                        properties={"config": json.dumps(config)}, uuid=uuid
                    )
            else:
                await config_collection.data.insert(
                    properties={"config": json.dumps(config)}, uuid=uuid
                )

    async def reset_config(self, client: WeaviateAsyncClient, uuid: str):
        if await self.verify_collection(client, self.config_collection_name):
            config_collection = client.collections.use(self.config_collection_name)
            if await config_collection.data.exists(uuid):
                await config_collection.data.delete_by_id(uuid)

    # -------------------------------------------------------------------------
    # Document import
    # -------------------------------------------------------------------------

    async def import_document(
        self, client: WeaviateAsyncClient, document: Document, embedder: str
    ):
        """
        Write a vectorized Document to Weaviate.

        Inserts the document record, then batch-inserts all chunks with their
        vectors. Verifies chunk count after insertion and rolls back both the
        document and chunks if there's a mismatch.
        """
        if await self.verify_collection(
            client, self.document_collection_name
        ) and await self.verify_embedding_collection(client, embedder):
            document_collection = client.collections.use(self.document_collection_name)
            embedder_collection = client.collections.use(self.embedding_table[embedder])

            ### Import Document
            document_obj = Document.to_json(document)
            doc_uuid = await document_collection.data.insert(document_obj)

            chunk_ids = []

            try:
                for chunk in document.chunks:
                    chunk.doc_uuid = doc_uuid
                    chunk.labels = document.labels
                    chunk.title = document.title

                chunk_response = await embedder_collection.data.insert_many(
                    [
                        DataObject(properties=chunk.to_json(), vector=chunk.vector)
                        for chunk in document.chunks
                    ]
                )
                chunk_ids = [
                    chunk_response.uuids[uuid] for uuid in chunk_response.uuids
                ]

                if chunk_response.has_errors:
                    raise Exception(
                        f"Failed to ingest chunks into Weaviate: {chunk_response.errors}"
                    )

                if doc_uuid and chunk_response:
                    response = await embedder_collection.aggregate.over_all(
                        filters=Filter.by_property("doc_uuid").equal(doc_uuid),
                        total_count=True,
                    )
                    if response.total_count != len(document.chunks):
                        await document_collection.data.delete_by_id(doc_uuid)
                        for _id in chunk_ids:
                            await embedder_collection.data.delete_by_id(_id)
                        raise Exception(
                            f"Chunk Mismatch detected after importing: Imported:{response.total_count} | Existing: {len(document.chunks)}"
                        )

            except Exception as e:
                if doc_uuid:
                    await self.delete_document(client, doc_uuid)
                raise Exception(f"Chunk import failed with : {str(e)}")

    # -------------------------------------------------------------------------
    # Document CRUD
    # -------------------------------------------------------------------------

    async def exist_document_name(
        self, client: WeaviateAsyncClient, name: str
    ) -> str | None:
        """
        Return the UUID of an existing document with the given title, or None.

        A single filtered query suffices — the prior aggregate.over_all() that
        checked total_count was an extra round-trip that gained nothing.
        """
        if await self.verify_collection(client, self.document_collection_name):
            document_collection = client.collections.use(self.document_collection_name)
            documents = await document_collection.query.fetch_objects(
                filters=Filter.by_property("title").equal(name),
                limit=1,
            )
            if documents.objects:
                return documents.objects[0].uuid
            return None

    async def delete_document(self, client: WeaviateAsyncClient, uuid: str):
        if await self.verify_collection(client, self.document_collection_name):
            document_collection = client.collections.use(self.document_collection_name)

            if not await document_collection.data.exists(uuid):
                return

            document_obj = await document_collection.query.fetch_object_by_id(uuid)
            meta_raw = document_obj.properties.get("meta")
            if not meta_raw:
                await document_collection.data.delete_by_id(uuid)
                return
            try:
                embedding_config = json.loads(meta_raw)["Embedder"]
                embedder = embedding_config["config"]["Model"]["value"]
            except (json.JSONDecodeError, KeyError):
                # meta is malformed or missing Embedder key — delete the document
                # record but skip trying to clean up chunks we can't identify
                await document_collection.data.delete_by_id(uuid)
                return

            if await self.verify_embedding_collection(client, embedder):
                if await document_collection.data.delete_by_id(uuid):
                    embedder_collection = client.collections.use(
                        self.embedding_table[embedder]
                    )
                    await embedder_collection.data.delete_many(
                        where=Filter.by_property("doc_uuid").equal(uuid)
                    )

    async def delete_all_documents(self, client: WeaviateAsyncClient):
        """
        Delete all documents and their associated chunks.

        Collects all UUIDs first, then fires all deletes concurrently via
        asyncio.gather() instead of processing them one by one.
        """
        if await self.verify_collection(client, self.document_collection_name):
            document_collection = client.collections.use(self.document_collection_name)
            all_uuids = [
                str(item.uuid) async for item in document_collection.iterator()
            ]
            await asyncio.gather(
                *[self.delete_document(client, uuid) for uuid in all_uuids],
                return_exceptions=True,
            )

    async def delete_all_configs(self, client: WeaviateAsyncClient):
        if await self.verify_collection(client, self.config_collection_name):
            config_collection = client.collections.use(self.config_collection_name)
            async for item in config_collection.iterator():
                await config_collection.data.delete_by_id(item.uuid)

    async def delete_all(self, client: WeaviateAsyncClient):
        node_payload, collection_payload = await self.get_metadata(client)
        for collection in collection_payload["collections"]:
            if "VERBA" in collection["name"]:
                await client.collections.delete(collection["name"])

    async def get_documents(
        self,
        client: WeaviateAsyncClient,
        query: str,
        pageSize: int,
        page: int,
        labels: list[str],
        properties: list[str] = None,
    ) -> list[dict]:
        if await self.verify_collection(client, self.document_collection_name):
            offset = pageSize * (page - 1)
            document_collection = client.collections.use(self.document_collection_name)

            if len(labels) > 0:
                filter = Filter.by_property("labels").contains_all(labels)
            else:
                filter = None

            response = await document_collection.aggregate.over_all(
                total_count=True, filters=filter
            )

            if response.total_count == 0:
                return [], 0

            total_count = response.total_count

            if query == "":
                total_count = response.total_count
                response = await document_collection.query.fetch_objects(
                    limit=pageSize,
                    offset=offset,
                    return_properties=properties,
                    sort=Sort.by_property("title", ascending=True),
                    filters=filter,
                )
            else:
                response = await document_collection.query.bm25(
                    query=query,
                    limit=pageSize,
                    offset=offset,
                    filters=filter,
                    return_properties=properties,
                )

            return [
                {
                    "title": doc.properties["title"],
                    "uuid": str(doc.uuid),
                    "labels": doc.properties["labels"],
                }
                for doc in response.objects
            ], total_count

    async def get_document(
        self, client: WeaviateAsyncClient, uuid: str, properties: list[str] = None
    ) -> list[dict]:
        if await self.verify_collection(client, self.document_collection_name):
            document_collection = client.collections.use(self.document_collection_name)

            if await document_collection.data.exists(uuid):
                response = await document_collection.query.fetch_object_by_id(
                    uuid, return_properties=properties
                )
                return response.properties
            else:
                msg.warn(f"Document not found ({uuid})")
                return None

    # -------------------------------------------------------------------------
    # Labels
    # -------------------------------------------------------------------------

    async def get_labels(self, client: WeaviateAsyncClient) -> list[str]:
        if await self.verify_collection(client, self.document_collection_name):
            document_collection = client.collections.use(self.document_collection_name)
            aggregation = await document_collection.aggregate.over_all(
                group_by=GroupByAggregate(prop="labels"), total_count=True
            )
            return [
                aggregation_group.grouped_by.value
                for aggregation_group in aggregation.groups
            ]

    # -------------------------------------------------------------------------
    # Chunk retrieval
    # -------------------------------------------------------------------------

    async def get_chunk(
        self, client: WeaviateAsyncClient, uuid: str, embedder: str
    ) -> list[dict]:
        if await self.verify_embedding_collection(client, embedder):
            embedder_collection = client.collections.use(self.embedding_table[embedder])
            if await embedder_collection.data.exists(uuid):
                response = await embedder_collection.query.fetch_object_by_id(uuid)
                response.properties["doc_uuid"] = str(response.properties["doc_uuid"])
                return response.properties
            else:
                return None

    async def get_chunks(
        self, client: WeaviateAsyncClient, uuid: str, page: int, pageSize: int
    ) -> list[dict]:

        if await self.verify_collection(client, self.document_collection_name):

            offset = pageSize * (page - 1)

            document = await self.get_document(client, uuid, properties=["meta"])
            if document is None:
                return []

            embedding_config = json.loads(document.get("meta"))["Embedder"]
            embedder = embedding_config["config"]["Model"]["value"]

            if await self.verify_embedding_collection(client, embedder):
                embedder_collection = client.collections.use(
                    self.embedding_table[embedder]
                )

                weaviate_chunks = await embedder_collection.query.fetch_objects(
                    filters=Filter.by_property("doc_uuid").equal(uuid),
                    limit=pageSize,
                    offset=offset,
                    sort=Sort.by_property("chunk_id", ascending=True),
                )
                chunks = [obj.properties for obj in weaviate_chunks.objects]
                for chunk in chunks:
                    chunk["doc_uuid"] = str(chunk["doc_uuid"])
                return chunks

    async def get_vectors(
        self, client: WeaviateAsyncClient, uuid: str, showAll: bool
    ) -> dict:

        document = await self.get_document(client, uuid, properties=["meta", "title"])

        if document is None:
            return None

        embedding_config = json.loads(document.get("meta"))["Embedder"]
        embedder = embedding_config["config"]["Model"]["value"]

        if await self.verify_embedding_collection(client, embedder):
            embedder_collection = client.collections.use(self.embedding_table[embedder])

            if not showAll:
                batch_size = 250
                all_chunks = []
                offset = 0

                while True:
                    weaviate_chunks = await embedder_collection.query.fetch_objects(
                        filters=Filter.by_property("doc_uuid").equal(uuid),
                        limit=batch_size,
                        offset=offset,
                        return_properties=["chunk_id", "pca"],
                        include_vector=True,
                    )

                    all_chunks.extend(weaviate_chunks.objects)

                    if len(weaviate_chunks.objects) < batch_size:
                        break

                    offset += batch_size

                dimensions = len(all_chunks[0].vector["default"])

                chunks = [
                    {
                        "vector": {"x": pca[0], "y": pca[1], "z": pca[2]},
                        "uuid": str(item.uuid),
                        "chunk_id": item.properties["chunk_id"],
                    }
                    for item in all_chunks
                    if (pca := item.properties["pca"]) is not None
                ]
                return {
                    "embedder": embedder,
                    "dimensions": dimensions,
                    "groups": [{"name": document["title"], "chunks": chunks}],
                }

            # Generate PCA for all embeddings
            else:
                # First pass: stream all items into memory
                all_items = []
                dimensions = 0
                async for item in embedder_collection.iterator(include_vector=True):
                    all_items.append(item)
                    dimensions = len(item.vector["default"])

                if not all_items:
                    return {"embedder": embedder, "dimensions": 0, "groups": []}

                # Batch-fetch all unique documents concurrently instead of one
                # sequential get_document() call per unique doc_uuid inside the loop
                unique_doc_uuids = list(
                    {str(item.properties["doc_uuid"]) for item in all_items}
                )
                doc_results = await asyncio.gather(
                    *[
                        self.get_document(client, doc_uuid, properties=["title"])
                        for doc_uuid in unique_doc_uuids
                    ],
                    return_exceptions=True,
                )
                vector_map = {
                    doc_uuid: {"name": doc["title"], "chunks": []}
                    for doc_uuid, doc in zip(unique_doc_uuids, doc_results)
                    if doc and not isinstance(doc, Exception)
                }

                # Second pass: collect vectors for successfully-fetched documents
                vector_list, vector_ids, vector_chunk_uuids, vector_chunk_ids = (
                    [],
                    [],
                    [],
                    [],
                )
                for item in all_items:
                    doc_uuid = str(item.properties["doc_uuid"])
                    if doc_uuid not in vector_map:
                        continue
                    vector_list.append(item.vector["default"])
                    vector_ids.append(doc_uuid)
                    vector_chunk_uuids.append(item.uuid)
                    vector_chunk_ids.append(item.properties["chunk_id"])

                if len(vector_ids) > 3:
                    pca = PCA(n_components=3)
                    generated_pca_embeddings = pca.fit_transform(vector_list)
                    pca_embeddings = [
                        pca_.tolist() for pca_ in generated_pca_embeddings
                    ]

                    for pca_embedding, _uuid, _chunk_uuid, _chunk_id in zip(
                        pca_embeddings,
                        vector_ids,
                        vector_chunk_uuids,
                        vector_chunk_ids,
                    ):
                        vector_map[_uuid]["chunks"].append(
                            {
                                "vector": {
                                    "x": pca_embedding[0],
                                    "y": pca_embedding[1],
                                    "z": pca_embedding[2],
                                },
                                "uuid": str(_chunk_uuid),
                                "chunk_id": _chunk_id,
                            }
                        )

                    return {
                        "embedder": embedder,
                        "dimensions": dimensions,
                        "groups": list(vector_map.values()),
                    }
                else:
                    return {
                        "embedder": embedder,
                        "dimensions": dimensions,
                        "groups": [],
                    }

        return None

    async def get_chunk_by_ids(
        self, client: WeaviateAsyncClient, embedder: str, doc_uuid: str, ids: list[int]
    ):
        """Fetch specific chunks by their sequential chunk_id values within a document."""
        if await self.verify_embedding_collection(client, embedder):
            embedder_collection = client.collections.use(self.embedding_table[embedder])
            try:
                weaviate_chunks = await embedder_collection.query.fetch_objects(
                    filters=(
                        Filter.by_property("doc_uuid").equal(str(doc_uuid))
                        & Filter.by_property("chunk_id").contains_any(list(ids))
                    ),
                    sort=Sort.by_property("chunk_id", ascending=True),
                )
                return weaviate_chunks.objects
            except Exception as e:
                msg.fail(f"Failed to fetch chunks: {str(e)}")
                raise e

    async def hybrid_chunks(
        self,
        client: WeaviateAsyncClient,
        embedder: str,
        query: str,
        vector: list[float],
        limit_mode: str,
        limit: int,
        labels: list[str],
        document_uuids: list[str],
    ):
        """
        Run a hybrid (BM25 + vector) search over the embedder's chunk collection.

        limit_mode="Autocut" uses Weaviate's auto_limit (stops at a natural
        relevance cutoff); otherwise a hard limit is applied.
        Filters are ANDed together — labels AND document_uuids if both are given.
        """
        if await self.verify_embedding_collection(client, embedder):
            embedder_collection = client.collections.use(self.embedding_table[embedder])

            filters = []

            if labels:
                filters.append(Filter.by_property("labels").contains_all(labels))

            if document_uuids:
                filters.append(
                    Filter.by_property("doc_uuid").contains_any(document_uuids)
                )

            if filters:
                apply_filters = filters[0]
                for filter in filters[1:]:
                    apply_filters = apply_filters & filter
            else:
                apply_filters = None

            if limit_mode == "Autocut":
                chunks = await embedder_collection.query.hybrid(
                    query=query,
                    vector=vector,
                    alpha=0.5,
                    auto_limit=limit,
                    return_metadata=MetadataQuery(score=True, explain_score=False),
                    filters=apply_filters,
                )
            else:
                chunks = await embedder_collection.query.hybrid(
                    query=query,
                    vector=vector,
                    alpha=0.5,
                    limit=limit,
                    return_metadata=MetadataQuery(score=True, explain_score=False),
                    filters=apply_filters,
                )

            return chunks.objects

    # -------------------------------------------------------------------------
    # Suggestions
    # -------------------------------------------------------------------------

    async def add_suggestion(self, client: WeaviateAsyncClient, query: str):
        """Store a query as an autocomplete suggestion (deduplicates by exact match)."""
        if await self.verify_collection(client, self.suggestion_collection_name):
            suggestion_collection = client.collections.use(
                self.suggestion_collection_name
            )
            # One query suffices — if the collection is empty the filter returns 0
            # results regardless, so a prior aggregate.over_all() is redundant.
            existing = await suggestion_collection.query.fetch_objects(
                filters=Filter.by_property("query").equal(query)
            )
            if len(existing.objects) > 0:
                return
            await suggestion_collection.data.insert(
                {"query": query, "timestamp": datetime.now().isoformat()}
            )

    async def retrieve_suggestions(
        self, client: WeaviateAsyncClient, query: str, limit: int
    ):
        if await self.verify_collection(client, self.suggestion_collection_name):
            suggestion_collection = client.collections.use(
                self.suggestion_collection_name
            )
            suggestions = await suggestion_collection.query.bm25(
                query=query, limit=limit
            )
            return_suggestions = [
                {
                    "query": suggestion.properties["query"],
                    "timestamp": suggestion.properties["timestamp"],
                    "uuid": str(suggestion.uuid),
                }
                for suggestion in suggestions.objects
            ]
            return return_suggestions

    async def retrieve_all_suggestions(
        self, client: WeaviateAsyncClient, page: int, pageSize: int
    ):
        if await self.verify_collection(client, self.suggestion_collection_name):
            suggestion_collection = client.collections.use(
                self.suggestion_collection_name
            )
            offset = pageSize * (page - 1)
            suggestions = await suggestion_collection.query.fetch_objects(
                limit=pageSize,
                offset=offset,
                sort=Sort.by_property("timestamp", ascending=False),
            )
            aggregation = await suggestion_collection.aggregate.over_all(
                total_count=True
            )
            return_suggestions = [
                {
                    "query": suggestion.properties["query"],
                    "timestamp": suggestion.properties["timestamp"],
                    "uuid": str(suggestion.uuid),
                }
                for suggestion in suggestions.objects
            ]
            return return_suggestions, aggregation.total_count

    async def delete_suggestions(self, client: WeaviateAsyncClient, uuid: str):
        if await self.verify_collection(client, self.suggestion_collection_name):
            suggestion_collection = client.collections.use(
                self.suggestion_collection_name
            )
            await suggestion_collection.data.delete_by_id(uuid)

    async def delete_all_suggestions(self, client: WeaviateAsyncClient):
        if await self.verify_collection(client, self.suggestion_collection_name):
            await client.collections.delete(self.suggestion_collection_name)

    # -------------------------------------------------------------------------
    # Metadata / counts
    # -------------------------------------------------------------------------

    async def get_datacount(
        self, client: WeaviateAsyncClient, embedder: str, document_uuids: list[str] = []
    ) -> int:
        if await self.verify_embedding_collection(client, embedder):
            embedder_collection = client.collections.use(self.embedding_table[embedder])

            if document_uuids:
                filters = Filter.by_property("doc_uuid").contains_any(document_uuids)
            else:
                filters = None
            try:
                response = await embedder_collection.aggregate.over_all(
                    filters=filters,
                    group_by=GroupByAggregate(prop="doc_uuid"),
                    total_count=True,
                )
                return len(response.groups)
            except Exception as e:
                msg.fail(f"Failed to retrieve data count: {str(e)}")
                return 0

    async def get_chunk_count(
        self, client: WeaviateAsyncClient, embedder: str, doc_uuid: str
    ) -> int:
        if await self.verify_embedding_collection(client, embedder):
            embedder_collection = client.collections.use(self.embedding_table[embedder])
            response = await embedder_collection.aggregate.over_all(
                filters=Filter.by_property("doc_uuid").equal(doc_uuid),
                group_by=GroupByAggregate(prop="doc_uuid"),
                total_count=True,
            )
            if response.groups:
                return response.groups[0].total_count
            else:
                return 0
