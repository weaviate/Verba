"""
test_verba_manager.py
=====================
Unit tests for VerbaManager.

Strategy: instantiate a real VerbaManager, then replace sub-managers on the
instance with MagicMock / AsyncMock objects. This avoids patching import paths
and keeps each test focused on the behaviour being asserted.

Groups:
  1. Pure unit tests  — no mocks (create_user_config, _keys_match, verify_config,
                        get_deployments, verify_installed_libraries, verify_variables)
  2. Config round-trips — mock weaviate_manager for load/set/reset config methods
  3. Import pipeline    — mock reader, chunker, embedder, weaviate managers
  4. RAG pipeline       — mock embedder, retriever, generator managers
"""

import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from goldenverba.components.verba_manager import VerbaManager
from goldenverba.server.types import (
    FileConfig,
    FileStatus,
    ChunkScore,
    RAGComponentClass,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def manager():
    """Real VerbaManager with weaviate_manager replaced by a MagicMock."""
    m = VerbaManager()
    m.weaviate_manager = MagicMock()
    return m


@pytest.fixture
def mock_logger():
    """Minimal LoggerManager stand-in."""
    logger = MagicMock()
    logger.send_report = AsyncMock()
    return logger


def _minimal_config_setting(description="desc", values=None):
    """Return a minimal config-setting dict that verify_config can walk."""
    return {"description": description, "values": values or ["a", "b"]}


def _make_config(*category_keys):
    """
    Build a minimal RAG config dict for verify_config tests.
    Each category has one component ("comp") with one setting ("key").
    """
    return {
        cat: {
            "components": {
                "comp": {
                    "config": {
                        "key": _minimal_config_setting()
                    }
                }
            }
        }
        for cat in category_keys
    }


def _make_rag_component_class(selected="MockEmbedder", model_value="text-embedding-3-small"):
    """Return a RAGComponentClass-like MagicMock for use in rag_config dicts."""
    config_setting = MagicMock()
    config_setting.value = model_value

    component = MagicMock()
    component.config = {"Model": config_setting}

    rag_class = MagicMock(spec=RAGComponentClass)
    rag_class.selected = selected
    rag_class.components = {selected: component}
    return rag_class


# ---------------------------------------------------------------------------
# 1. Pure unit tests
# ---------------------------------------------------------------------------


class TestCreateUserConfig:
    def test_returns_default(self, manager):
        assert manager.create_user_config() == {"getting_started": False}


class TestKeysMatch:
    def test_matching_keys_returns_true(self, manager):
        assert manager._keys_match({"a": 1, "b": 2}, {"a": 3, "b": 4}, "test") is True

    def test_mismatched_keys_returns_false(self, manager):
        assert manager._keys_match({"a": 1}, {"b": 1}, "test") is False

    def test_empty_dicts_match(self, manager):
        assert manager._keys_match({}, {}, "test") is True

    def test_subset_returns_false(self, manager):
        assert manager._keys_match({"a": 1}, {"a": 1, "b": 2}, "test") is False


class TestVerifyConfig:
    def test_matching_configs_returns_true(self, manager):
        cfg = _make_config("Reader", "Chunker")
        assert manager.verify_config(cfg, cfg) is True

    def test_category_mismatch_returns_false(self, manager):
        a = _make_config("Reader")
        b = _make_config("Chunker")
        assert manager.verify_config(a, b) is False

    def test_component_mismatch_returns_false(self, manager):
        base = _make_config("Reader")
        drift = {
            "Reader": {
                "components": {
                    "other_comp": {"config": {"key": _minimal_config_setting()}}
                }
            }
        }
        assert manager.verify_config(base, drift) is False

    def test_config_key_mismatch_returns_false(self, manager):
        a = _make_config("Reader")
        b = {
            "Reader": {
                "components": {
                    "comp": {
                        "config": {
                            "different_key": _minimal_config_setting()
                        }
                    }
                }
            }
        }
        assert manager.verify_config(a, b) is False

    def test_description_mismatch_returns_false(self, manager):
        a = _make_config("Reader")
        b = {
            "Reader": {
                "components": {
                    "comp": {
                        "config": {
                            "key": _minimal_config_setting(description="changed")
                        }
                    }
                }
            }
        }
        assert manager.verify_config(a, b) is False

    def test_values_mismatch_returns_false(self, manager):
        a = _make_config("Reader")
        b = {
            "Reader": {
                "components": {
                    "comp": {
                        "config": {
                            "key": _minimal_config_setting(values=["x", "y"])
                        }
                    }
                }
            }
        }
        assert manager.verify_config(a, b) is False

    def test_malformed_config_returns_false(self, manager):
        assert manager.verify_config({"bad": "data"}, _make_config("Reader")) is False

    def test_demo_mode_always_true(self, manager):
        a = _make_config("Reader")
        b = _make_config("Chunker")  # deliberately mismatched
        with patch.dict(os.environ, {"VERBA_PRODUCTION": "Demo"}):
            assert manager.verify_config(a, b) is True


class TestGetDeployments:
    @pytest.mark.asyncio
    async def test_returns_env_vars_when_set(self, manager):
        with patch.dict(os.environ, {
            "WEAVIATE_URL_VERBA": "https://my.weaviate.io",
            "WEAVIATE_API_KEY_VERBA": "secret",
        }):
            result = await manager.get_deployments()
        assert result["WEAVIATE_URL_VERBA"] == "https://my.weaviate.io"
        assert result["WEAVIATE_API_KEY_VERBA"] == "secret"

    @pytest.mark.asyncio
    async def test_returns_empty_strings_when_unset(self, manager):
        env = {k: v for k, v in os.environ.items()
               if k not in ("WEAVIATE_URL_VERBA", "WEAVIATE_API_KEY_VERBA")}
        with patch.dict(os.environ, env, clear=True):
            result = await manager.get_deployments()
        assert result["WEAVIATE_URL_VERBA"] == ""
        assert result["WEAVIATE_API_KEY_VERBA"] == ""


class TestVerifyInstalledLibraries:
    def test_importable_library_marked_true(self, manager):
        # Inject a fake component whose requires_library contains a stdlib module.
        fake_component = MagicMock()
        fake_component.requires_library = ["os"]
        fake_component.requires_env = []
        manager.reader_manager.readers = {"fake": fake_component}
        # Reset the other managers so they contribute nothing.
        for attr in ("chunkers", "embedders", "retrievers", "generators"):
            mgr_name = attr.replace("ers", "er_manager").replace("ors", "or_manager")
        manager.chunker_manager.chunkers = {}
        manager.embedder_manager.embedders = {}
        manager.retriever_manager.retrievers = {}
        manager.generator_manager.generators = {}

        manager.installed_libraries = {}
        manager.verify_installed_libraries()
        assert manager.installed_libraries.get("os") is True

    def test_missing_library_marked_false(self, manager):
        fake_component = MagicMock()
        fake_component.requires_library = ["__nonexistent_lib__"]
        fake_component.requires_env = []
        manager.reader_manager.readers = {"fake": fake_component}
        manager.chunker_manager.chunkers = {}
        manager.embedder_manager.embedders = {}
        manager.retriever_manager.retrievers = {}
        manager.generator_manager.generators = {}

        manager.installed_libraries = {}
        manager.verify_installed_libraries()
        assert manager.installed_libraries.get("__nonexistent_lib__") is False


class TestVerifyVariables:
    def test_set_env_var_marked_true(self, manager):
        fake_component = MagicMock()
        fake_component.requires_env = ["TEST_VAR_VERBA"]
        fake_component.requires_library = []
        manager.reader_manager.readers = {"fake": fake_component}
        manager.chunker_manager.chunkers = {}
        manager.embedder_manager.embedders = {}
        manager.retriever_manager.retrievers = {}
        manager.generator_manager.generators = {}

        with patch.dict(os.environ, {"TEST_VAR_VERBA": "value"}):
            manager.environment_variables = {}
            manager.verify_variables()
        assert manager.environment_variables.get("TEST_VAR_VERBA") is True

    def test_unset_env_var_marked_false(self, manager):
        fake_component = MagicMock()
        fake_component.requires_env = ["MISSING_VAR_VERBA_XYZ"]
        fake_component.requires_library = []
        manager.reader_manager.readers = {"fake": fake_component}
        manager.chunker_manager.chunkers = {}
        manager.embedder_manager.embedders = {}
        manager.retriever_manager.retrievers = {}
        manager.generator_manager.generators = {}

        env = {k: v for k, v in os.environ.items() if k != "MISSING_VAR_VERBA_XYZ"}
        with patch.dict(os.environ, env, clear=True):
            manager.environment_variables = {}
            manager.verify_variables()
        assert manager.environment_variables.get("MISSING_VAR_VERBA_XYZ") is False


# ---------------------------------------------------------------------------
# 2. Config round-trip tests
# ---------------------------------------------------------------------------


class TestLoadRagConfig:
    @pytest.mark.asyncio
    async def test_returns_stored_config_when_valid(self, manager):
        """Stored config passes verify_config → returned as-is; no write."""
        # create_config() returns a real config; mirror it as the "stored" one.
        real_config = manager.create_config()
        manager.weaviate_manager.get_config = AsyncMock(return_value=real_config)
        manager.weaviate_manager.set_config = AsyncMock()

        result = await manager.load_rag_config(client=MagicMock())

        assert result is real_config
        manager.weaviate_manager.set_config.assert_not_called()

    @pytest.mark.asyncio
    async def test_regenerates_config_on_schema_drift(self, manager):
        """Stored config fails verify_config → fresh config written and returned."""
        stale_config = {"completely": "wrong"}
        manager.weaviate_manager.get_config = AsyncMock(return_value=stale_config)
        manager.weaviate_manager.set_config = AsyncMock()

        result = await manager.load_rag_config(client=MagicMock())

        # set_config called with the RAG UUID
        manager.weaviate_manager.set_config.assert_awaited_once()
        call_args = manager.weaviate_manager.set_config.call_args
        assert call_args.args[1] == manager.rag_config_uuid
        # Returned config is a fresh one (has all 5 pipeline categories).
        assert set(result.keys()) == {"Reader", "Chunker", "Embedder", "Retriever", "Generator"}

    @pytest.mark.asyncio
    async def test_returns_fresh_config_when_none_stored(self, manager):
        """No stored config → fresh config returned; nothing written."""
        manager.weaviate_manager.get_config = AsyncMock(return_value=None)
        manager.weaviate_manager.set_config = AsyncMock()

        result = await manager.load_rag_config(client=MagicMock())

        manager.weaviate_manager.set_config.assert_not_called()
        assert set(result.keys()) == {"Reader", "Chunker", "Embedder", "Retriever", "Generator"}


class TestLoadThemeConfig:
    @pytest.mark.asyncio
    async def test_returns_theme_and_themes_when_stored(self, manager):
        stored = {"theme": "dark", "themes": {"dark": {}, "light": {}}}
        manager.weaviate_manager.get_config = AsyncMock(return_value=stored)

        theme, themes = await manager.load_theme_config(client=MagicMock())

        assert theme == "dark"
        assert themes == {"dark": {}, "light": {}}

    @pytest.mark.asyncio
    async def test_returns_none_tuple_when_nothing_stored(self, manager):
        manager.weaviate_manager.get_config = AsyncMock(return_value=None)

        theme, themes = await manager.load_theme_config(client=MagicMock())

        assert theme is None
        assert themes is None


class TestLoadUserConfig:
    @pytest.mark.asyncio
    async def test_returns_stored_config(self, manager):
        stored = {"getting_started": True, "extra": "data"}
        manager.weaviate_manager.get_config = AsyncMock(return_value=stored)

        result = await manager.load_user_config(client=MagicMock())

        assert result == stored

    @pytest.mark.asyncio
    async def test_returns_default_when_nothing_stored(self, manager):
        manager.weaviate_manager.get_config = AsyncMock(return_value=None)

        result = await manager.load_user_config(client=MagicMock())

        assert result == {"getting_started": False}


class TestSetConfigs:
    @pytest.mark.asyncio
    async def test_set_rag_config_uses_correct_uuid(self, manager):
        manager.weaviate_manager.set_config = AsyncMock()
        client = MagicMock()
        payload = {"some": "config"}

        await manager.set_rag_config(client, payload)

        manager.weaviate_manager.set_config.assert_awaited_once_with(
            client, manager.rag_config_uuid, payload
        )

    @pytest.mark.asyncio
    async def test_set_theme_config_uses_correct_uuid(self, manager):
        manager.weaviate_manager.set_config = AsyncMock()
        client = MagicMock()
        payload = {"theme": "light"}

        await manager.set_theme_config(client, payload)

        manager.weaviate_manager.set_config.assert_awaited_once_with(
            client, manager.theme_config_uuid, payload
        )

    @pytest.mark.asyncio
    async def test_set_user_config_uses_correct_uuid(self, manager):
        manager.weaviate_manager.set_config = AsyncMock()
        client = MagicMock()
        payload = {"getting_started": True}

        await manager.set_user_config(client, payload)

        manager.weaviate_manager.set_config.assert_awaited_once_with(
            client, manager.user_config_uuid, payload
        )


class TestResetConfigs:
    @pytest.mark.asyncio
    async def test_reset_rag_config_uses_correct_uuid(self, manager):
        manager.weaviate_manager.reset_config = AsyncMock()
        client = MagicMock()

        await manager.reset_rag_config(client)

        manager.weaviate_manager.reset_config.assert_awaited_once_with(
            client, manager.rag_config_uuid
        )

    @pytest.mark.asyncio
    async def test_reset_theme_config_uses_correct_uuid(self, manager):
        manager.weaviate_manager.reset_config = AsyncMock()
        client = MagicMock()

        await manager.reset_theme_config(client)

        manager.weaviate_manager.reset_config.assert_awaited_once_with(
            client, manager.theme_config_uuid
        )

    @pytest.mark.asyncio
    async def test_reset_user_config_uses_correct_uuid(self, manager):
        manager.weaviate_manager.reset_config = AsyncMock()
        client = MagicMock()

        await manager.reset_user_config(client)

        manager.weaviate_manager.reset_config.assert_awaited_once_with(
            client, manager.user_config_uuid
        )


# ---------------------------------------------------------------------------
# 3. Import pipeline tests
# ---------------------------------------------------------------------------


def _make_file_config(filename="test.txt", overwrite=False):
    """Minimal FileConfig for import pipeline tests."""
    reader_class = _make_rag_component_class(selected="Basic")
    chunker_class = _make_rag_component_class(selected="Token")
    embedder_class = _make_rag_component_class(selected="OpenAI")

    return FileConfig(
        fileID="file-001",
        filename=filename,
        isURL=False,
        overwrite=overwrite,
        extension=".txt",
        source="",
        content="hello world",
        labels=[],
        rag_config={
            "Reader": reader_class,
            "Chunker": chunker_class,
            "Embedder": embedder_class,
        },
        file_size=11,
        status=FileStatus.READY,
        metadata="",
        status_report={},
    )


class TestImportDocument:
    @pytest.mark.asyncio
    async def test_happy_path_single_document(self, manager, mock_logger):
        """Reader → chunk → embed → store: logger receives STARTING then DONE."""
        from goldenverba.components.document import Document
        from goldenverba.components.chunk import Chunk

        chunk = Chunk(content="hello world", chunk_id="0")
        doc = Document(title="test.txt", content="hello world", extension=".txt")
        doc.chunks = [chunk]

        # Mock reader
        manager.reader_manager.load = AsyncMock(return_value=[doc])
        # Mock chunker
        manager.chunker_manager.chunk = AsyncMock(return_value=[doc])
        # Mock embedder
        manager.embedder_manager.vectorize = AsyncMock(return_value=[doc])
        # Mock weaviate
        manager.weaviate_manager.exist_document_name = AsyncMock(return_value=None)
        manager.weaviate_manager.import_document = AsyncMock()

        file_config = _make_file_config()
        await manager.import_document(MagicMock(), file_config, mock_logger)

        # First status: STARTING
        first_call = mock_logger.send_report.call_args_list[0]
        assert first_call.kwargs["status"] == FileStatus.STARTING
        # Last status: DONE (from process_single_document or import_document level)
        statuses = [call.kwargs["status"] for call in mock_logger.send_report.call_args_list]
        assert FileStatus.DONE in statuses

    @pytest.mark.asyncio
    async def test_duplicate_no_overwrite_reports_error(self, manager, mock_logger):
        """Existing document + overwrite=False → ERROR logged; delete NOT called."""
        manager.weaviate_manager.exist_document_name = AsyncMock(return_value="existing-uuid")
        manager.weaviate_manager.delete_document = AsyncMock()

        file_config = _make_file_config(overwrite=False)
        await manager.import_document(MagicMock(), file_config, mock_logger)

        statuses = [call.kwargs["status"] for call in mock_logger.send_report.call_args_list]
        assert FileStatus.ERROR in statuses
        manager.weaviate_manager.delete_document.assert_not_called()

    @pytest.mark.asyncio
    async def test_duplicate_with_overwrite_deletes_then_imports(self, manager, mock_logger):
        """Existing document + overwrite=True → delete called before import."""
        from goldenverba.components.document import Document
        from goldenverba.components.chunk import Chunk

        chunk = Chunk(content="hello world", chunk_id="0")
        doc = Document(title="test.txt", content="hello world", extension=".txt")
        doc.chunks = [chunk]

        manager.weaviate_manager.exist_document_name = AsyncMock(return_value="existing-uuid")
        manager.weaviate_manager.delete_document = AsyncMock()
        manager.reader_manager.load = AsyncMock(return_value=[doc])
        manager.chunker_manager.chunk = AsyncMock(return_value=[doc])
        manager.embedder_manager.vectorize = AsyncMock(return_value=[doc])
        manager.weaviate_manager.import_document = AsyncMock()

        file_config = _make_file_config(overwrite=True)
        await manager.import_document(MagicMock(), file_config, mock_logger)

        # Both import_document and process_single_document check for duplicates,
        # so delete_document is called once per duplicate check (two total here).
        assert manager.weaviate_manager.delete_document.await_count >= 1
        statuses = [call.kwargs["status"] for call in mock_logger.send_report.call_args_list]
        assert FileStatus.ERROR not in statuses


# ---------------------------------------------------------------------------
# 4. RAG pipeline tests
# ---------------------------------------------------------------------------


class TestRetrieveChunks:
    @pytest.mark.asyncio
    async def test_returns_documents_and_context(self, manager):
        dummy_vector = [0.1, 0.2, 0.3]
        expected_docs = [{"uuid": "doc-1", "chunks": []}]
        expected_context = "some retrieved context"

        manager.embedder_manager.vectorize_query = AsyncMock(return_value=dummy_vector)
        manager.retriever_manager.retrieve = AsyncMock(
            return_value=(expected_docs, expected_context)
        )
        manager.weaviate_manager.add_suggestion = AsyncMock()

        rag_config = {
            "Retriever": _make_rag_component_class(selected="Window"),
            "Embedder": _make_rag_component_class(selected="OpenAI"),
        }

        docs, context = await manager.retrieve_chunks(
            client=MagicMock(),
            query="what is Verba?",
            rag_config=rag_config,
        )

        assert docs == expected_docs
        assert context == expected_context

    @pytest.mark.asyncio
    async def test_short_query_skips_suggestion(self, manager):
        """Query shorter than 3 chars → add_suggestion not called."""
        manager.embedder_manager.vectorize_query = AsyncMock(return_value=[0.0])
        manager.retriever_manager.retrieve = AsyncMock(return_value=([], ""))
        manager.weaviate_manager.add_suggestion = AsyncMock()

        rag_config = {
            "Retriever": _make_rag_component_class(selected="Window"),
            "Embedder": _make_rag_component_class(selected="OpenAI"),
        }

        await manager.retrieve_chunks(
            client=MagicMock(),
            query="hi",
            rag_config=rag_config,
        )

        manager.weaviate_manager.add_suggestion.assert_not_called()


class TestGenerateStreamAnswer:
    @pytest.mark.asyncio
    async def test_yields_all_chunks_with_full_text_on_stop(self, manager):
        """Streamed tokens are yielded; final stop chunk gets full_text appended."""

        async def _fake_stream(rag_config, query, context, conversation):
            yield {"message": "Hello", "finish_reason": ""}
            yield {"message": " world", "finish_reason": "stop"}

        manager.generator_manager.generate_stream = _fake_stream

        rag_config = {"Generator": _make_rag_component_class(selected="OpenAI")}
        chunks = []
        async for chunk in manager.generate_stream_answer(rag_config, "q", "ctx", []):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0]["message"] == "Hello"
        assert chunks[1]["message"] == " world"
        assert chunks[1]["full_text"] == "Hello world"

    @pytest.mark.asyncio
    async def test_yields_nothing_when_stream_is_empty(self, manager):
        async def _empty_stream(rag_config, query, context, conversation):
            return
            yield  # make it an async generator

        manager.generator_manager.generate_stream = _empty_stream

        rag_config = {"Generator": _make_rag_component_class(selected="OpenAI")}
        chunks = []
        async for chunk in manager.generate_stream_answer(rag_config, "q", "ctx", []):
            chunks.append(chunk)

        assert chunks == []
