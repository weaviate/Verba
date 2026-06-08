"""
Integration tests for WeaviateManager.

These tests require a live Weaviate instance. They are skipped automatically
when the required environment variables are not set, so they are safe to run
in any CI environment — they only execute when a real instance is available.

How to run locally
------------------
# Against a local Docker instance (docker compose up -d weaviate):
    pytest goldenverba/tests/weaviate/ -v

# Against Weaviate Cloud:
    WEAVIATE_TEST_URL=https://my-cluster.weaviate.network \\
    WEAVIATE_TEST_KEY=my-api-key \\
    pytest goldenverba/tests/weaviate/ -v

Environment variables
---------------------
WEAVIATE_TEST_URL   — cluster URL for Weaviate Cloud. When absent the tests
                      connect to a local Docker instance at localhost:8080.
WEAVIATE_TEST_KEY   — API key. Required when WEAVIATE_TEST_URL is set.
                      Optional for unauthenticated local instances.
"""

import os
import pytest
import pytest_asyncio

# All async tests in this module share a single event loop so that
# module-scoped fixtures (manager, client) remain connected between tests.
pytestmark = pytest.mark.asyncio(loop_scope="module")

from goldenverba.components.weaviate_manager import WeaviateManager
from goldenverba.components.document import Document
from goldenverba.components.chunk import Chunk

# ---------------------------------------------------------------------------
# Skip condition
# ---------------------------------------------------------------------------

# Tests are opt-in: they only run when WEAVIATE_TEST_URL (cloud) or
# WEAVIATE_INTEGRATION=1 (local Docker) is explicitly set.
# This ensures they are safely skipped in CI and local dev by default.
_CLOUD_URL = os.environ.get("WEAVIATE_TEST_URL", "")
_CLOUD_KEY = os.environ.get("WEAVIATE_TEST_KEY", "")
_LOCAL = os.environ.get("WEAVIATE_INTEGRATION", "").lower() in ("1", "true", "yes")

_ENABLED = bool(_CLOUD_URL or _LOCAL)

requires_weaviate = pytest.mark.skipif(
    not _ENABLED,
    reason=(
        "Integration tests are opt-in. To run against a local Docker instance: "
        "WEAVIATE_INTEGRATION=1 pytest goldenverba/tests/weaviate/ "
        "To run against Weaviate Cloud: "
        "WEAVIATE_TEST_URL=<url> WEAVIATE_TEST_KEY=<key> pytest goldenverba/tests/weaviate/"
    ),
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Use a dedicated collection prefix so tests never touch real Verba data.
_TEST_PREFIX = "VERBA_TEST_"


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def manager():
    """A WeaviateManager with test-namespaced collection names."""
    wm = WeaviateManager()
    # Redirect all collection names to test-specific names so we never
    # interfere with real Verba data in a shared Weaviate instance.
    wm.document_collection_name = _TEST_PREFIX + "DOCUMENTS"
    wm.config_collection_name = _TEST_PREFIX + "CONFIGURATION"
    wm.suggestion_collection_name = _TEST_PREFIX + "SUGGESTIONS"
    return wm


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def client(manager):
    """
    A live WeaviateAsyncClient.

    Connects to Weaviate Cloud if WEAVIATE_TEST_URL is set, otherwise
    falls back to a local Docker instance at localhost:8080.
    """
    if _CLOUD_URL:
        if not _CLOUD_KEY:
            pytest.skip("WEAVIATE_TEST_URL is set but WEAVIATE_TEST_KEY is missing")
        c = await manager.connect(
            deployment="Weaviate",
            weaviateURL=_CLOUD_URL,
            weaviateAPIKey=_CLOUD_KEY,
        )
    else:
        # Local Docker: WEAVIATE_HOST defaults to localhost for tests.
        # (In Docker Compose it would be "weaviate", but tests run on the host.)
        c = await manager.connect(
            deployment="Custom",
            weaviateURL=os.environ.get("WEAVIATE_HOST", "localhost"),
            weaviateAPIKey="",
            port=os.environ.get("WEAVIATE_PORT", "8080"),
        )
    yield c
    # Teardown: delete every test collection we created so the instance is clean.
    for name in list(await c.collections.list_all()):
        if name.startswith(_TEST_PREFIX):
            await c.collections.delete(name)
    await manager.disconnect(c)


@pytest_asyncio.fixture(autouse=True, loop_scope="module")
async def clean_collections(manager, client):
    """
    Before each test: purge all test collections so tests start from a
    known-empty state without depending on execution order.
    """
    for name in list(await client.collections.list_all()):
        if name.startswith(_TEST_PREFIX):
            await client.collections.delete(name)
    # Clear the manager's collection verification cache so it re-creates them.
    manager._verified_collections.clear()
    manager.embedding_table.clear()
    manager.cache_table.clear()
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEST_EMBEDDER = "test-embedder-model"


def make_document(title: str = "Test Doc", n_chunks: int = 3) -> Document:
    doc = Document(title=title, content="Hello world", labels=["test"])
    for i in range(n_chunks):
        chunk = Chunk(
            content=f"chunk {i}",
            chunk_id=i,
            start_i=i * 10,
            end_i=i * 10 + 9,
        )
        chunk.vector = [0.1 * (i + 1)] * 4  # tiny fake vector
        chunk.pca = [0.0, 0.0, 0.0]
        chunk.title = title
        chunk.labels = ["test"]
        doc.chunks.append(chunk)
    return doc


# ---------------------------------------------------------------------------
# Connection tests
# ---------------------------------------------------------------------------


@requires_weaviate
class TestConnection:
    async def test_client_is_ready(self, client):
        assert await client.is_ready()

    async def test_invalid_deployment_raises(self, manager):
        with pytest.raises(Exception, match="Invalid deployment type"):
            await manager.connect(
                deployment="NonExistent",
                weaviateURL="",
                weaviateAPIKey="",
            )

    async def test_cloud_missing_key_raises(self, manager):
        with pytest.raises(Exception):
            await manager.connect(
                deployment="Weaviate",
                weaviateURL="https://example.weaviate.network",
                weaviateAPIKey="",  # empty — should raise
            )


# ---------------------------------------------------------------------------
# Collection management
# ---------------------------------------------------------------------------


@requires_weaviate
class TestCollections:
    async def test_verify_collection_creates_if_absent(self, manager, client):
        name = _TEST_PREFIX + "NEWCOL"
        assert not await client.collections.exists(name)
        result = await manager.verify_collection(client, name)
        assert result is True
        assert await client.collections.exists(name)

    async def test_verify_collection_caches_result(self, manager, client):
        name = _TEST_PREFIX + "CACHED"
        await manager.verify_collection(client, name)
        client_id = id(client)
        assert name in manager._verified_collections.get(client_id, set())

        # Delete the collection externally — the cache still says "exists"
        await client.collections.delete(name)
        # Second call should return True from cache without hitting Weaviate
        result = await manager.verify_collection(client, name)
        assert result is True

    async def test_verify_embedding_collection(self, manager, client):
        result = await manager.verify_embedding_collection(client, _TEST_EMBEDDER)
        assert result is True
        assert _TEST_EMBEDDER in manager.embedding_table
        collection_name = manager.embedding_table[_TEST_EMBEDDER]
        assert await client.collections.exists(collection_name)

    async def test_verify_embedding_collection_cached_on_second_call(self, manager, client):
        await manager.verify_embedding_collection(client, _TEST_EMBEDDER)
        # Second call: embedder is already in embedding_table, returns True immediately
        result = await manager.verify_embedding_collection(client, _TEST_EMBEDDER)
        assert result is True


# ---------------------------------------------------------------------------
# Configuration CRUD
# ---------------------------------------------------------------------------


@requires_weaviate
class TestConfig:
    _UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    async def test_set_and_get_config(self, manager, client):
        config = {"key": "value", "nested": {"a": 1}}
        await manager.set_config(client, self._UUID, config)
        loaded = await manager.get_config(client, self._UUID)
        assert loaded == config

    async def test_get_config_missing_returns_none(self, manager, client):
        result = await manager.get_config(client, self._UUID)
        assert result is None

    async def test_set_config_overwrites(self, manager, client):
        await manager.set_config(client, self._UUID, {"v": 1})
        await manager.set_config(client, self._UUID, {"v": 2})
        loaded = await manager.get_config(client, self._UUID)
        assert loaded == {"v": 2}

    async def test_reset_config(self, manager, client):
        await manager.set_config(client, self._UUID, {"v": 1})
        await manager.reset_config(client, self._UUID)
        result = await manager.get_config(client, self._UUID)
        assert result is None


# ---------------------------------------------------------------------------
# Document CRUD
# ---------------------------------------------------------------------------


@requires_weaviate
class TestDocuments:
    async def test_exist_document_name_false_when_empty(self, manager, client):
        result = await manager.exist_document_name(client, "Nonexistent")
        assert result is None

    async def test_import_and_exist(self, manager, client):
        doc = make_document("Alpha")
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        uuid = await manager.exist_document_name(client, "Alpha")
        assert uuid is not None

    async def test_get_document(self, manager, client):
        doc = make_document("Beta")
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        uuid = await manager.exist_document_name(client, "Beta")
        fetched = await manager.get_document(client, str(uuid))
        assert fetched is not None
        assert fetched["title"] == "Beta"

    async def test_get_document_missing_returns_none(self, manager, client):
        result = await manager.get_document(client, "00000000-0000-0000-0000-000000000000")
        assert result is None

    async def test_delete_document(self, manager, client):
        doc = make_document("Gamma")
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        uuid = await manager.exist_document_name(client, "Gamma")
        assert uuid is not None

        await manager.delete_document(client, str(uuid))
        assert await manager.exist_document_name(client, "Gamma") is None

    async def test_delete_all_documents(self, manager, client):
        for title in ["D1", "D2", "D3"]:
            doc = make_document(title)
            doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
            await manager.import_document(client, doc, _TEST_EMBEDDER)

        await manager.delete_all_documents(client)

        for title in ["D1", "D2", "D3"]:
            assert await manager.exist_document_name(client, title) is None

    async def test_get_documents_pagination(self, manager, client):
        for i in range(5):
            doc = make_document(f"Page{i}")
            doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
            await manager.import_document(client, doc, _TEST_EMBEDDER)

        results, total = await manager.get_documents(
            client, query="", pageSize=3, page=1, labels=[]
        )
        assert total == 5
        assert len(results) == 3

    async def test_get_documents_bm25_search(self, manager, client):
        for title in ["Python guide", "JavaScript guide", "Rust primer"]:
            doc = make_document(title)
            doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
            await manager.import_document(client, doc, _TEST_EMBEDDER)

        results, _ = await manager.get_documents(
            client, query="Python", pageSize=10, page=1, labels=[]
        )
        titles = [r["title"] for r in results]
        assert "Python guide" in titles

    async def test_get_labels(self, manager, client):
        doc = make_document("Labelled")
        doc.labels = ["science", "tech"]
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        labels = await manager.get_labels(client)
        assert "science" in labels
        assert "tech" in labels


# ---------------------------------------------------------------------------
# Chunks
# ---------------------------------------------------------------------------


@requires_weaviate
class TestChunks:
    async def test_get_chunk(self, manager, client):
        doc = make_document("ChunkDoc", n_chunks=3)
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        uuid = await manager.exist_document_name(client, "ChunkDoc")
        fetched_doc = await manager.get_document(client, str(uuid))

        # get_chunk_by_ids: fetch chunks 0 and 1
        chunks = await manager.get_chunk_by_ids(client, _TEST_EMBEDDER, str(uuid), [0, 1])
        assert len(chunks) == 2
        chunk_ids = {c.properties["chunk_id"] for c in chunks}
        assert chunk_ids == {0, 1}

    async def test_get_chunk_count(self, manager, client):
        doc = make_document("CountDoc", n_chunks=4)
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        uuid = await manager.exist_document_name(client, "CountDoc")
        count = await manager.get_chunk_count(client, _TEST_EMBEDDER, str(uuid))
        assert count == 4

    async def test_hybrid_chunks_returns_results(self, manager, client):
        doc = make_document("HybridDoc", n_chunks=2)
        doc.meta = {"Embedder": {"config": {"Model": {"value": _TEST_EMBEDDER}}}}
        await manager.import_document(client, doc, _TEST_EMBEDDER)

        # Hybrid search with a tiny random vector — should return chunks
        results = await manager.hybrid_chunks(
            client,
            embedder=_TEST_EMBEDDER,
            query="chunk",
            vector=[0.1, 0.1, 0.1, 0.1],
            limit_mode="Limit",
            limit=10,
            labels=[],
            document_uuids=[],
        )
        assert len(results) > 0


# ---------------------------------------------------------------------------
# Suggestions
# ---------------------------------------------------------------------------


@requires_weaviate
class TestSuggestions:
    async def test_add_and_retrieve_suggestion(self, manager, client):
        await manager.add_suggestion(client, "what is RAG?")
        results = await manager.retrieve_suggestions(client, "RAG", limit=5)
        assert any(r["query"] == "what is RAG?" for r in results)

    async def test_add_suggestion_deduplicates(self, manager, client):
        await manager.add_suggestion(client, "duplicate query")
        await manager.add_suggestion(client, "duplicate query")
        results = await manager.retrieve_suggestions(client, "duplicate", limit=10)
        matches = [r for r in results if r["query"] == "duplicate query"]
        assert len(matches) == 1

    async def test_delete_suggestion(self, manager, client):
        await manager.add_suggestion(client, "to be deleted")
        results = await manager.retrieve_suggestions(client, "deleted", limit=5)
        uuid = next(r["uuid"] for r in results if r["query"] == "to be deleted")

        await manager.delete_suggestions(client, uuid)
        results_after = await manager.retrieve_suggestions(client, "deleted", limit=5)
        assert not any(r["query"] == "to be deleted" for r in results_after)

    async def test_retrieve_all_suggestions_pagination(self, manager, client):
        for i in range(5):
            await manager.add_suggestion(client, f"unique suggestion {i}")

        page1, total = await manager.retrieve_all_suggestions(client, page=1, pageSize=3)
        assert total >= 5
        assert len(page1) == 3
