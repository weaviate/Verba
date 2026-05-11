"""
Tests for goldenverba/server/api.py FastAPI endpoints.

Strategy: patch the module-level `manager` and `client_manager` singletons
so that no real Weaviate connection or LLM call is required.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

import goldenverba.server.api as api_module
from weaviate.client import WeaviateAsyncClient

# ---------------------------------------------------------------------------
# Shared payload helpers
# ---------------------------------------------------------------------------

CREDENTIALS = {"deployment": "Local", "url": "", "key": ""}


def creds_payload(**extra):
    return {**CREDENTIALS, **extra}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_weaviate_client():
    # spec=WeaviateAsyncClient makes isinstance() checks in api.py pass
    return MagicMock(spec=WeaviateAsyncClient)


@pytest.fixture
def mock_manager():
    m = MagicMock()
    m.get_deployments = AsyncMock(
        return_value={"WEAVIATE_URL_VERBA": "", "WEAVIATE_API_KEY_VERBA": ""}
    )
    m.load_rag_config = AsyncMock(
        return_value={
            "Reader": {"components": {}, "selected": ""},
            "Chunker": {"components": {}, "selected": ""},
            "Embedder": {"components": {}, "selected": ""},
            "Retriever": {"components": {}, "selected": ""},
            "Generator": {"components": {}, "selected": ""},
        }
    )
    m.load_user_config = AsyncMock(return_value={"getting_started": False})
    m.load_theme_config = AsyncMock(return_value=(None, None))
    m.set_rag_config = AsyncMock()
    m.set_user_config = AsyncMock()
    m.set_theme_config = AsyncMock()
    m.retrieve_chunks = AsyncMock(return_value=([], ""))
    m.get_content = AsyncMock(return_value=([], 0))

    wm = MagicMock()
    wm.get_document = AsyncMock(
        return_value={
            "title": "test.txt",
            "content": "",
            "extension": ".txt",
            "fileSize": 42,
            "labels": [],
            "source": "",
            "meta": "{}",
            "metadata": "",
        }
    )
    wm.get_documents = AsyncMock(return_value=([], 0))
    wm.get_labels = AsyncMock(return_value=[])
    wm.get_chunks = AsyncMock(return_value=[])
    wm.get_chunk = AsyncMock(return_value={})
    wm.get_vectors = AsyncMock(
        return_value={"embedder": "test", "dimensions": 3, "groups": []}
    )
    wm.get_datacount = AsyncMock(return_value=0)
    wm.get_metadata = AsyncMock(
        return_value=(
            {"node_count": 1, "weaviate_version": "1.0", "nodes": []},
            {"collection_count": 0, "collections": []},
        )
    )
    wm.delete_document = AsyncMock()
    wm.delete_all = AsyncMock()
    wm.delete_all_documents = AsyncMock()
    wm.delete_all_configs = AsyncMock()
    wm.delete_all_suggestions = AsyncMock()
    wm.retrieve_suggestions = AsyncMock(return_value=[])
    wm.retrieve_all_suggestions = AsyncMock(return_value=([], 0))
    wm.delete_suggestions = AsyncMock()
    m.weaviate_manager = wm
    return m


@pytest.fixture
def mock_client_manager(mock_weaviate_client):
    m = MagicMock()
    m.connect = AsyncMock(return_value=mock_weaviate_client)
    m.disconnect = AsyncMock()
    m.clean_up = AsyncMock()
    return m


@pytest.fixture
def client(mock_manager, mock_client_manager):
    # The same-origin middleware checks that Origin matches the server's base URL.
    # TestClient uses http://testserver, so we pass that as the default Origin header.
    with (
        patch.object(api_module, "manager", mock_manager),
        patch.object(api_module, "client_manager", mock_client_manager),
    ):
        with TestClient(
            api_module.app, headers={"origin": "http://testserver"}
        ) as c:
            yield c


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_body_has_message(self, client):
        data = client.get("/api/health").json()
        assert data["message"] == "Alive!"

    def test_health_calls_clean_up(self, client, mock_client_manager):
        client.get("/api/health")
        mock_client_manager.clean_up.assert_awaited_once()

    def test_health_contains_production_field(self, client):
        data = client.get("/api/health").json()
        assert "production" in data

    def test_health_contains_deployments(self, client):
        data = client.get("/api/health").json()
        assert "deployments" in data


# ---------------------------------------------------------------------------
# /api/connect
# ---------------------------------------------------------------------------


class TestConnectEndpoint:
    def _payload(self, **extra):
        return {"credentials": CREDENTIALS, "port": "8080", **extra}

    def test_connect_success_returns_200(self, client):
        resp = client.post("/api/connect", json=self._payload())
        assert resp.status_code == 200

    def test_connect_success_connected_true(self, client):
        data = client.post("/api/connect", json=self._payload()).json()
        assert data["connected"] is True

    def test_connect_success_returns_rag_config(self, client):
        data = client.post("/api/connect", json=self._payload()).json()
        assert "rag_config" in data

    def test_connect_failure_returns_400(self, client, mock_client_manager):
        mock_client_manager.connect = AsyncMock(
            side_effect=Exception("connection refused")
        )
        resp = client.post("/api/connect", json=self._payload())
        assert resp.status_code == 400

    def test_connect_failure_connected_false(self, client, mock_client_manager):
        mock_client_manager.connect = AsyncMock(
            side_effect=Exception("connection refused")
        )
        data = client.post("/api/connect", json=self._payload()).json()
        assert data["connected"] is False

    def test_connect_failure_contains_error(self, client, mock_client_manager):
        mock_client_manager.connect = AsyncMock(
            side_effect=Exception("bad credentials")
        )
        data = client.post("/api/connect", json=self._payload()).json()
        assert "error" in data
        assert data["error"] != ""


# ---------------------------------------------------------------------------
# /api/get_rag_config
# ---------------------------------------------------------------------------


class TestGetRagConfig:
    def test_returns_200(self, client):
        resp = client.post("/api/get_rag_config", json=CREDENTIALS)
        assert resp.status_code == 200

    def test_returns_rag_config(self, client):
        data = client.post("/api/get_rag_config", json=CREDENTIALS).json()
        assert "rag_config" in data

    def test_error_returns_500(self, client, mock_manager):
        mock_manager.load_rag_config = AsyncMock(side_effect=Exception("db error"))
        resp = client.post("/api/get_rag_config", json=CREDENTIALS)
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /api/set_rag_config
# ---------------------------------------------------------------------------


class TestSetRagConfig:
    def _payload(self):
        rag_config = {
            "Reader": {"selected": "", "components": {}},
            "Chunker": {"selected": "", "components": {}},
            "Embedder": {"selected": "", "components": {}},
            "Retriever": {"selected": "", "components": {}},
            "Generator": {"selected": "", "components": {}},
        }
        return {"rag_config": rag_config, "credentials": CREDENTIALS}

    def test_success_returns_200_status(self, client):
        data = client.post("/api/set_rag_config", json=self._payload()).json()
        assert data["status"] == 200

    def test_calls_set_rag_config(self, client, mock_manager):
        client.post("/api/set_rag_config", json=self._payload())
        mock_manager.set_rag_config.assert_awaited_once()


# ---------------------------------------------------------------------------
# /api/query
# ---------------------------------------------------------------------------


class TestQueryEndpoint:
    def _payload(self, query="what is Verba?"):
        return {
            "query": query,
            "RAG": {
                "Reader": {"selected": "", "components": {}},
                "Chunker": {"selected": "", "components": {}},
                "Embedder": {"selected": "", "components": {}},
                "Retriever": {"selected": "", "components": {}},
                "Generator": {"selected": "", "components": {}},
            },
            "labels": [],
            "documentFilter": [],
            "credentials": CREDENTIALS,
        }

    def test_returns_200(self, client):
        resp = client.post("/api/query", json=self._payload())
        assert resp.status_code == 200

    def test_returns_documents_and_context(self, client):
        data = client.post("/api/query", json=self._payload()).json()
        assert "documents" in data
        assert "context" in data

    def test_error_path_returns_error_field(self, client, mock_manager):
        mock_manager.retrieve_chunks = AsyncMock(side_effect=Exception("retrieval failed"))
        data = client.post("/api/query", json=self._payload()).json()
        assert data["error"] != ""
        assert data["documents"] == []

    def test_query_too_long_rejected(self, client):
        resp = client.post("/api/query", json=self._payload(query="x" * 50_001))
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /api/get_document
# ---------------------------------------------------------------------------


class TestGetDocument:
    def _payload(self, uuid="abc-123"):
        return {"uuid": uuid, "credentials": CREDENTIALS}

    def test_returns_document(self, client):
        data = client.post("/api/get_document", json=self._payload()).json()
        assert data["document"]["title"] == "test.txt"

    def test_document_not_found_returns_error(self, client, mock_manager):
        mock_manager.weaviate_manager.get_document = AsyncMock(return_value=None)
        data = client.post("/api/get_document", json=self._payload()).json()
        assert data["document"] is None
        assert data["error"] != ""

    def test_exception_returns_error(self, client, mock_manager):
        mock_manager.weaviate_manager.get_document = AsyncMock(
            side_effect=Exception("weaviate down")
        )
        data = client.post("/api/get_document", json=self._payload()).json()
        assert data["document"] is None


# ---------------------------------------------------------------------------
# /api/get_all_documents
# ---------------------------------------------------------------------------


class TestGetAllDocuments:
    def _payload(self, query="", page=1, page_size=10):
        return {
            "query": query,
            "labels": [],
            "page": page,
            "pageSize": page_size,
            "credentials": CREDENTIALS,
        }

    def test_returns_200(self, client):
        resp = client.post("/api/get_all_documents", json=self._payload())
        assert resp.status_code == 200

    def test_returns_empty_list_when_no_docs(self, client):
        data = client.post("/api/get_all_documents", json=self._payload()).json()
        assert data["documents"] == []
        assert data["totalDocuments"] == 0

    def test_returns_documents_from_manager(self, client, mock_manager):
        mock_manager.weaviate_manager.get_documents = AsyncMock(
            return_value=([{"title": "foo.txt", "uuid": "u1", "labels": []}], 1)
        )
        data = client.post("/api/get_all_documents", json=self._payload()).json()
        assert len(data["documents"]) == 1
        assert data["totalDocuments"] == 1


# ---------------------------------------------------------------------------
# /api/delete_document
# ---------------------------------------------------------------------------


class TestDeleteDocument:
    def _payload(self, uuid="abc-123"):
        return {"uuid": uuid, "credentials": CREDENTIALS}

    def test_returns_200_on_success(self, client):
        resp = client.post("/api/delete_document", json=self._payload())
        assert resp.status_code == 200

    def test_calls_delete_document(self, client, mock_manager):
        client.post("/api/delete_document", json=self._payload("my-uuid"))
        mock_manager.weaviate_manager.delete_document.assert_awaited_once()

    def test_exception_returns_400(self, client, mock_manager):
        mock_manager.weaviate_manager.delete_document = AsyncMock(
            side_effect=Exception("weaviate down")
        )
        resp = client.post("/api/delete_document", json=self._payload())
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /api/reset
# ---------------------------------------------------------------------------


class TestResetEndpoint:
    def _payload(self, mode="ALL"):
        return {"resetMode": mode, "credentials": CREDENTIALS}

    def test_reset_all_calls_delete_all(self, client, mock_manager):
        client.post("/api/reset", json=self._payload("ALL"))
        mock_manager.weaviate_manager.delete_all.assert_awaited_once()

    def test_reset_documents_calls_delete_all_documents(self, client, mock_manager):
        client.post("/api/reset", json=self._payload("DOCUMENTS"))
        mock_manager.weaviate_manager.delete_all_documents.assert_awaited_once()

    def test_reset_config_calls_delete_all_configs(self, client, mock_manager):
        client.post("/api/reset", json=self._payload("CONFIG"))
        mock_manager.weaviate_manager.delete_all_configs.assert_awaited_once()

    def test_reset_suggestions_calls_delete_all_suggestions(self, client, mock_manager):
        client.post("/api/reset", json=self._payload("SUGGESTIONS"))
        mock_manager.weaviate_manager.delete_all_suggestions.assert_awaited_once()

    def test_exception_returns_500(self, client, mock_manager):
        mock_manager.weaviate_manager.delete_all = AsyncMock(
            side_effect=Exception("weaviate down")
        )
        resp = client.post("/api/reset", json=self._payload("ALL"))
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /api/get_meta
# ---------------------------------------------------------------------------


class TestGetMeta:
    def test_returns_node_and_collection_payload(self, client):
        data = client.post("/api/get_meta", json=CREDENTIALS).json()
        assert "node_payload" in data
        assert "collection_payload" in data

    def test_exception_returns_error(self, client, mock_manager):
        mock_manager.weaviate_manager.get_metadata = AsyncMock(
            side_effect=Exception("metadata unavailable")
        )
        data = client.post("/api/get_meta", json=CREDENTIALS).json()
        assert data["error"] != ""


# ---------------------------------------------------------------------------
# /api/get_suggestions  /api/delete_suggestion
# ---------------------------------------------------------------------------


class TestSuggestions:
    def test_get_suggestions_returns_list(self, client):
        data = client.post(
            "/api/get_suggestions",
            json={"query": "test", "limit": 5, "credentials": CREDENTIALS},
        ).json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_get_suggestions_exception_returns_empty(self, client, mock_manager):
        mock_manager.weaviate_manager.retrieve_suggestions = AsyncMock(
            side_effect=Exception("boom")
        )
        data = client.post(
            "/api/get_suggestions",
            json={"query": "test", "limit": 5, "credentials": CREDENTIALS},
        ).json()
        assert data["suggestions"] == []

    def test_delete_suggestion_returns_200_status(self, client):
        data = client.post(
            "/api/delete_suggestion",
            json={"uuid": "some-uuid", "credentials": CREDENTIALS},
        ).json()
        assert data["status"] == 200

    def test_get_all_suggestions_returns_list_and_count(self, client):
        data = client.post(
            "/api/get_all_suggestions",
            json={"page": 1, "pageSize": 10, "credentials": CREDENTIALS},
        ).json()
        assert "suggestions" in data
        assert "total_count" in data


# ---------------------------------------------------------------------------
# /api/get_content
# ---------------------------------------------------------------------------


class TestGetContent:
    def _payload(self):
        return {
            "uuid": "doc-uuid",
            "page": 1,
            "chunkScores": [],
            "credentials": CREDENTIALS,
        }

    def test_returns_content_and_max_page(self, client):
        data = client.post("/api/get_content", json=self._payload()).json()
        assert "content" in data
        assert "maxPage" in data

    def test_exception_returns_error(self, client, mock_manager):
        mock_manager.get_content = AsyncMock(side_effect=Exception("db error"))
        data = client.post("/api/get_content", json=self._payload()).json()
        assert data["error"] != ""


# ---------------------------------------------------------------------------
# /api/get_datacount
# ---------------------------------------------------------------------------


class TestGetDatacount:
    def test_returns_datacount(self, client):
        data = client.post(
            "/api/get_datacount",
            json={
                "embedding_model": "all-MiniLM-L6-v2",
                "documentFilter": [],
                "credentials": CREDENTIALS,
            },
        ).json()
        assert "datacount" in data
        assert data["datacount"] == 0

    def test_exception_returns_zero(self, client, mock_manager):
        mock_manager.weaviate_manager.get_datacount = AsyncMock(
            side_effect=Exception("boom")
        )
        data = client.post(
            "/api/get_datacount",
            json={
                "embedding_model": "all-MiniLM-L6-v2",
                "documentFilter": [],
                "credentials": CREDENTIALS,
            },
        ).json()
        assert data["datacount"] == 0


# ---------------------------------------------------------------------------
# /api/get_labels
# ---------------------------------------------------------------------------


class TestGetLabels:
    def test_returns_labels_from_manager(self, client, mock_manager):
        mock_manager.weaviate_manager.get_labels = AsyncMock(
            return_value=["finance", "legal"]
        )
        data = client.post("/api/get_labels", json=CREDENTIALS).json()
        assert data["labels"] == ["finance", "legal"]

    def test_exception_returns_empty_list(self, client, mock_manager):
        mock_manager.weaviate_manager.get_labels = AsyncMock(
            side_effect=Exception("boom")
        )
        data = client.post("/api/get_labels", json=CREDENTIALS).json()
        assert data["labels"] == []
