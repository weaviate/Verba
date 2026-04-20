"""
test_readers.py
===============
Unit and integration tests for the reader system.

Unit tests (Groups 1–7) run with no API keys and no network — all external
calls are mocked. Integration tests (Group 8) are opt-in: each test skips
unless the corresponding env var is set.

How to enable integration tests
--------------------------------
Set any combination of these in goldenverba/.env or your shell:

    UNSTRUCTURED_API_KEY=...
    GITHUB_TOKEN=...
    GITLAB_TOKEN=...

HTMLReader integration test uses https://example.com — no key required, but
set READER_NETWORK_TESTS=1 to opt in (avoids surprises in air-gapped CI).
"""

import asyncio
import base64
import io
import json
import os

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from goldenverba.components.reader.reader_manager import ReaderManager
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.reader.HTMLReader import HTMLReader
from goldenverba.components.reader.GitReader import GitReader
from goldenverba.components.reader.UnstructuredAPI import UnstructuredReader
from goldenverba.components.reader.WhisperReader import WhisperReader
from goldenverba.server.types import FileConfig, FileStatus, RAGComponentClass, RAGComponentConfig
from goldenverba.components.types import InputConfig


# ---------------------------------------------------------------------------
# Integration test skip markers
# ---------------------------------------------------------------------------

requires_unstructured = pytest.mark.skipif(
    not os.getenv("UNSTRUCTURED_API_KEY"),
    reason="Set UNSTRUCTURED_API_KEY to run Unstructured integration tests",
)
requires_github = pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN"),
    reason="Set GITHUB_TOKEN to run GitHub reader integration tests",
)
requires_gitlab = pytest.mark.skipif(
    not os.getenv("GITLAB_TOKEN"),
    reason="Set GITLAB_TOKEN to run GitLab reader integration tests",
)
requires_network = pytest.mark.skipif(
    not os.getenv("READER_NETWORK_TESTS"),
    reason="Set READER_NETWORK_TESTS=1 to run network-dependent reader tests",
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def _minimal_rag_class(name="Default") -> RAGComponentClass:
    """Build the smallest valid RAGComponentClass Pydantic model."""
    component = RAGComponentConfig(
        name=name,
        variables=[],
        library=[],
        description="",
        config={},
        type="",
        available=True,
    )
    return RAGComponentClass(selected=name, components={name: component})


def _make_file_config(
    filename="test.txt",
    extension="txt",
    content="hello world",
    is_url=False,
    overwrite=False,
    rag_config=None,
):
    return FileConfig(
        fileID="file-001",
        filename=filename,
        isURL=is_url,
        overwrite=overwrite,
        extension=extension,
        source="",
        content=_b64(content) if extension != "" else content,
        labels=[],
        rag_config=rag_config or {"Reader": _minimal_rag_class()},
        file_size=len(content),
        status=FileStatus.READY,
        metadata="",
        status_report={},
    )


def _make_config(**overrides) -> dict:
    """Return a minimal reader config dict."""
    return overrides


def _mock_aiohttp_response(status=200, json_data=None, text_data="<html>hi</html>"):
    """Return a context-manager-compatible mock aiohttp response."""
    response = MagicMock()
    response.status = status
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=json_data or {})
    response.text = AsyncMock(return_value=text_data)
    response.read = AsyncMock(return_value=text_data.encode() if isinstance(text_data, str) else text_data)

    if status >= 400:
        from aiohttp import ClientResponseError
        response.raise_for_status.side_effect = ClientResponseError(
            request_info=MagicMock(), history=(), status=status
        )

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=response)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm, response


def _mock_session(get_response=None, post_response=None):
    """Return a mock aiohttp.ClientSession context manager."""
    session = MagicMock()
    if get_response is not None:
        session.get = MagicMock(return_value=get_response)
    if post_response is not None:
        session.post = MagicMock(return_value=post_response)

    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)
    return session_cm, session


# ---------------------------------------------------------------------------
# 1. ReaderManager
# ---------------------------------------------------------------------------


class TestReaderManager:
    def test_all_readers_registered(self):
        manager = ReaderManager()
        expected = {"Default", "HTML", "Git", "Unstructured IO", "Whisper"}
        assert expected == set(manager.readers.keys())

    @pytest.mark.asyncio
    async def test_unknown_reader_raises(self):
        manager = ReaderManager()
        logger = MagicMock()
        logger.send_report = AsyncMock()
        fc = _make_file_config()

        with pytest.raises(Exception, match="Reader .* not found"):
            await manager.load("NonExistentReader", fc, logger)

    @pytest.mark.asyncio
    async def test_load_delegates_to_reader(self):
        manager = ReaderManager()
        logger = MagicMock()
        logger.send_report = AsyncMock()

        fake_doc = MagicMock()
        manager.readers["Default"] = MagicMock()
        manager.readers["Default"].load = AsyncMock(return_value=[fake_doc])

        fc = _make_file_config()
        result = await manager.load("Default", fc, logger)

        assert result == [fake_doc]
        manager.readers["Default"].load.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_load_sends_status_report(self):
        manager = ReaderManager()
        logger = MagicMock()
        logger.send_report = AsyncMock()

        fake_doc = MagicMock()
        manager.readers["Default"] = MagicMock()
        manager.readers["Default"].load = AsyncMock(return_value=[fake_doc])

        fc = _make_file_config()
        await manager.load("Default", fc, logger)

        logger.send_report.assert_awaited()


# ---------------------------------------------------------------------------
# 2. BasicReader
# ---------------------------------------------------------------------------


class TestBasicReader:
    @pytest.fixture
    def reader(self):
        return BasicReader()

    # --- text / code ---

    @pytest.mark.asyncio
    async def test_loads_txt_file(self, reader):
        fc = _make_file_config(extension="txt", content="hello world")
        docs = await reader.load({}, fc)
        assert len(docs) == 1
        assert "hello world" in docs[0].content

    @pytest.mark.asyncio
    async def test_loads_py_file(self, reader):
        fc = _make_file_config(filename="script.py", extension="py", content="print('hi')")
        docs = await reader.load({}, fc)
        assert len(docs) == 1
        assert "print('hi')" in docs[0].content

    @pytest.mark.asyncio
    async def test_unknown_extension_falls_back_to_text(self, reader):
        fc = _make_file_config(filename="foo.xyz", extension="xyz", content="raw bytes")
        docs = await reader.load({}, fc)
        assert len(docs) == 1

    # --- PDF ---

    @pytest.mark.asyncio
    async def test_load_pdf_returns_text(self, reader):
        page = MagicMock()
        page.extract_text.return_value = "Page content"

        with patch("goldenverba.components.reader.BasicReader.PdfReader") as MockPdf:
            MockPdf.return_value.pages = [page]
            result = await reader.load_pdf_file(b"fake-pdf-bytes")

        assert "Page content" in result

    @pytest.mark.asyncio
    async def test_load_pdf_skips_none_pages(self, reader):
        page_good = MagicMock()
        page_good.extract_text.return_value = "Good page"
        page_none = MagicMock()
        page_none.extract_text.return_value = None

        with patch("goldenverba.components.reader.BasicReader.PdfReader") as MockPdf:
            MockPdf.return_value.pages = [page_none, page_good]
            result = await reader.load_pdf_file(b"fake-pdf-bytes")

        assert "None" not in result
        assert "Good page" in result

    @pytest.mark.asyncio
    async def test_load_pdf_raises_when_pypdf_missing(self, reader):
        with patch("goldenverba.components.reader.BasicReader.PdfReader", None):
            with pytest.raises(ImportError):
                await reader.load_pdf_file(b"data")

    # --- DOCX ---

    @pytest.mark.asyncio
    async def test_load_docx_returns_paragraph_text(self, reader):
        para1, para2 = MagicMock(), MagicMock()
        para1.text = "First paragraph"
        para2.text = "Second paragraph"

        with patch("goldenverba.components.reader.BasicReader.docx") as mock_docx:
            mock_docx.Document.return_value.paragraphs = [para1, para2]
            result = await reader.load_docx_file(b"fake-docx")

        assert "First paragraph" in result
        assert "Second paragraph" in result

    @pytest.mark.asyncio
    async def test_load_docx_raises_when_docx_missing(self, reader):
        with patch("goldenverba.components.reader.BasicReader.docx", None):
            with pytest.raises(ImportError):
                await reader.load_docx_file(b"data")

    # --- CSV ---

    @pytest.mark.asyncio
    async def test_load_csv_formats_headers_and_rows(self, reader):
        csv_bytes = b"name,age\nAlice,30\nBob,25"
        result = await reader.load_csv_file(csv_bytes)
        assert "Headers:" in result
        assert "name" in result
        assert "Alice" in result

    @pytest.mark.asyncio
    async def test_load_csv_handles_empty_file(self, reader):
        result = await reader.load_csv_file(b"")
        assert "Empty" in result

    @pytest.mark.asyncio
    async def test_load_csv_handles_mismatched_columns(self, reader):
        # Row 2 has fewer columns than header — should not crash
        csv_bytes = b"a,b,c\n1,2\n3,4,5"
        result = await reader.load_csv_file(csv_bytes)
        assert result  # just needs to not raise

    # --- JSON ---

    @pytest.mark.asyncio
    async def test_load_json_raises_on_invalid_json(self, reader):
        fc = _make_file_config(extension="json")
        bad_json = b"not valid json{"
        with pytest.raises(ValueError, match="Invalid JSON"):
            await reader.load_json_file(bad_json, fc)

    @pytest.mark.asyncio
    async def test_load_json_falls_back_to_pretty_print(self, reader):
        fc = _make_file_config(extension="json")
        valid_json = json.dumps({"key": "value"}).encode()

        with patch("goldenverba.components.document.Document.from_json", return_value=None):
            docs = await reader.load_json_file(valid_json, fc)

        assert len(docs) == 1
        assert "key" in docs[0].content


# ---------------------------------------------------------------------------
# 3. HTMLReader
# ---------------------------------------------------------------------------


class TestHTMLReader:
    @pytest.fixture
    def reader(self):
        return HTMLReader()

    # --- extract_links ---

    def test_extract_links_same_domain(self, reader):
        html = '<a href="/page">link</a><a href="https://example.com/other">other</a>'
        links = reader.extract_links(html, "https://example.com/base")
        assert all("example.com" in l for l in links)

    def test_extract_links_excludes_off_domain(self, reader):
        html = '<a href="https://evil.com/steal">bad</a>'
        links = reader.extract_links(html, "https://example.com/")
        assert links == []

    def test_extract_links_resolves_relative(self, reader):
        html = '<a href="/about">about</a>'
        links = reader.extract_links(html, "https://example.com/")
        assert "https://example.com/about" in links

    # --- fetch_html_and_convert ---

    @pytest.mark.asyncio
    async def test_fetch_returns_base64_html(self, reader):
        html_text = "<h1>Hello</h1>"
        get_cm, _ = _mock_aiohttp_response(text_data=html_text)
        session = MagicMock()
        session.get = MagicMock(return_value=get_cm)

        content_b64, size, raw = await reader.fetch_html_and_convert(session, "https://example.com", False)

        decoded = base64.b64decode(content_b64).decode()
        assert decoded == html_text
        assert size == len(html_text.encode())

    @pytest.mark.asyncio
    async def test_fetch_converts_to_markdown(self, reader):
        html_text = "<h1>Title</h1>"
        get_cm, _ = _mock_aiohttp_response(text_data=html_text)
        session = MagicMock()
        session.get = MagicMock(return_value=get_cm)

        with patch("goldenverba.components.reader.HTMLReader.md", return_value="# Title\n") as mock_md:
            content_b64, _, _ = await reader.fetch_html_and_convert(session, "https://example.com", True)
            mock_md.assert_called_once_with(html_text)

        decoded = base64.b64decode(content_b64).decode()
        assert "Title" in decoded

    # --- load ---

    @pytest.mark.asyncio
    async def test_load_returns_document_per_url(self, reader):
        html_text = "<p>content</p>"
        get_cm, _ = _mock_aiohttp_response(text_data=html_text)
        session_cm, session = _mock_session(get_response=get_cm)
        session.get = MagicMock(return_value=get_cm)

        config = {
            "URLs": InputConfig(type="multi", value="", description="", values=["https://example.com"]),
            "Convert To Markdown": InputConfig(type="bool", value=False, description="", values=[]),
            "Recursive": InputConfig(type="bool", value=False, description="", values=[]),
            "Max Depth": InputConfig(type="number", value=1, description="", values=[]),
        }

        with patch("goldenverba.components.reader.HTMLReader.aiohttp.ClientSession", return_value=session_cm):
            docs = await reader.load(config, _make_file_config())

        assert len(docs) == 1

    @pytest.mark.asyncio
    async def test_load_continues_on_url_failure(self, reader):
        """A failing URL should be skipped, not crash the whole load."""
        config = {
            "URLs": InputConfig(type="multi", value="", description="", values=["https://bad-url.example"]),
            "Convert To Markdown": InputConfig(type="bool", value=False, description="", values=[]),
            "Recursive": InputConfig(type="bool", value=False, description="", values=[]),
            "Max Depth": InputConfig(type="number", value=1, description="", values=[]),
        }

        # Simulate a session whose get() always raises
        session = MagicMock()
        session.get = MagicMock(side_effect=Exception("network error"))
        session_cm = MagicMock()
        session_cm.__aenter__ = AsyncMock(return_value=session)
        session_cm.__aexit__ = AsyncMock(return_value=False)

        with patch("goldenverba.components.reader.HTMLReader.aiohttp.ClientSession", return_value=session_cm):
            docs = await reader.load(config, _make_file_config())

        # No docs returned but no exception raised
        assert docs == []


# ---------------------------------------------------------------------------
# 4. GitReader
# ---------------------------------------------------------------------------


class TestGitReader:
    @pytest.fixture
    def reader(self):
        return GitReader()

    def test_get_headers_github(self, reader):
        headers = reader.get_headers("mytoken", "GitHub")
        assert headers["Authorization"] == "token mytoken"
        assert "Accept" in headers

    def test_get_headers_gitlab(self, reader):
        headers = reader.get_headers("mytoken", "GitLab")
        assert headers["Authorization"] == "Bearer mytoken"

    def test_get_token_reads_github_env(self, reader):
        config = {}  # no "Git Token" key
        with patch.dict(os.environ, {"GITHUB_TOKEN": "gh-tok"}):
            token = reader.get_token(config, "GitHub")
        assert token == "gh-tok"

    def test_get_token_reads_gitlab_env(self, reader):
        config = {}
        with patch.dict(os.environ, {"GITLAB_TOKEN": "gl-tok"}):
            token = reader.get_token(config, "GitLab")
        assert token == "gl-tok"

    @pytest.mark.asyncio
    async def test_fetch_docs_github_filters_by_extension_and_path(self, reader):
        api_tree = {
            "tree": [
                {"path": "src/main.py", "type": "blob"},
                {"path": "src/readme.md", "type": "blob"},
                {"path": "other/main.py", "type": "blob"},
                {"path": "src/image.png", "type": "blob"},
            ]
        }
        get_cm, _ = _mock_aiohttp_response(json_data=api_tree)
        session_cm, session = _mock_session(get_response=get_cm)
        session.get = MagicMock(return_value=get_cm)

        mock_reader = MagicMock()
        mock_reader.extension = [".py", ".md"]

        with patch("goldenverba.components.reader.GitReader.aiohttp.ClientSession", return_value=session_cm):
            paths = await reader.fetch_docs_github("https://api.github.com/...", "src", "token", mock_reader)

        # Should include src/*.py and src/*.md but not other/ or .png
        assert "src/main.py" in paths
        assert "src/readme.md" in paths
        assert "other/main.py" not in paths
        assert "src/image.png" not in paths

    @pytest.mark.asyncio
    async def test_fetch_docs_gitlab_filters_blobs_by_extension(self, reader):
        api_data = [
            {"path": "app.py", "type": "blob"},
            {"path": "app.png", "type": "blob"},
            {"path": "subdir", "type": "tree"},
        ]
        get_cm, _ = _mock_aiohttp_response(json_data=api_data)
        session_cm, session = _mock_session(get_response=get_cm)
        session.get = MagicMock(return_value=get_cm)

        mock_reader = MagicMock()
        mock_reader.extension = [".py"]

        with patch("goldenverba.components.reader.GitReader.aiohttp.ClientSession", return_value=session_cm):
            paths = await reader.fetch_docs_gitlab("https://gitlab.com/...", "token", mock_reader)

        assert "app.py" in paths
        assert "app.png" not in paths
        assert "subdir" not in paths

    @pytest.mark.asyncio
    async def test_download_file_github_returns_tuple(self, reader):
        api_data = {
            "content": _b64("print('hello')"),
            "html_url": "https://github.com/owner/repo/blob/main/src/main.py",
            "size": 15,
        }
        get_cm, _ = _mock_aiohttp_response(json_data=api_data)
        session_cm, session = _mock_session(get_response=get_cm)
        session.get = MagicMock(return_value=get_cm)

        with patch("goldenverba.components.reader.GitReader.aiohttp.ClientSession", return_value=session_cm):
            content, link, size, ext = await reader.download_file_github(
                "owner", "repo", "src/main.py", "main", "token"
            )

        assert content == _b64("print('hello')")
        assert "github.com" in link
        assert size == 15
        assert ext == "py"

    @pytest.mark.asyncio
    async def test_download_file_gitlab_raises_on_error(self, reader):
        get_cm, mock_resp = _mock_aiohttp_response(status=404, text_data="Not Found")
        mock_resp.status = 404
        session_cm, session = _mock_session(get_response=get_cm)
        session.get = MagicMock(return_value=get_cm)

        with patch("goldenverba.components.reader.GitReader.aiohttp.ClientSession", return_value=session_cm):
            with pytest.raises(Exception, match="Failed to download"):
                await reader.download_file_gitlab("owner", "repo", "missing.py", "main", "token")


# ---------------------------------------------------------------------------
# 5. UnstructuredReader
# ---------------------------------------------------------------------------


class TestUnstructuredReader:
    @pytest.fixture
    def reader(self):
        return UnstructuredReader()

    def _config(self, strategy="auto", api_key="test-key", api_url="https://api.unstructuredapp.io/general/v0/general"):
        return {
            "Strategy": InputConfig(type="dropdown", value=strategy, description="", values=["auto", "hi_res", "ocr_only", "fast"]),
            "API Key": InputConfig(type="password", value=api_key, description="", values=[]),
            "API URL": InputConfig(type="text", value=api_url, description="", values=[]),
        }

    @pytest.mark.asyncio
    async def test_raises_on_invalid_strategy(self, reader):
        fc = _make_file_config()
        with pytest.raises(ValueError, match="Invalid strategy"):
            await reader.load(self._config(strategy="invalid"), fc)

    @pytest.mark.asyncio
    async def test_joins_chunk_texts(self, reader):
        api_response = [{"text": "Hello "}, {"text": "world"}]
        post_cm, _ = _mock_aiohttp_response(json_data=api_response)
        session_cm, session = _mock_session(post_response=post_cm)
        session.post = MagicMock(return_value=post_cm)

        with patch("goldenverba.components.reader.UnstructuredAPI.aiohttp.ClientSession", return_value=session_cm):
            docs = await reader.load(self._config(), _make_file_config())

        assert len(docs) == 1
        assert docs[0].content == "Hello world"

    @pytest.mark.asyncio
    async def test_raises_on_api_error_detail(self, reader):
        api_response = {"detail": "Invalid API key"}
        post_cm, _ = _mock_aiohttp_response(json_data=api_response)
        session_cm, session = _mock_session(post_response=post_cm)
        session.post = MagicMock(return_value=post_cm)

        with patch("goldenverba.components.reader.UnstructuredAPI.aiohttp.ClientSession", return_value=session_cm):
            with pytest.raises(Exception, match="API error"):
                await reader.load(self._config(), _make_file_config())


# ---------------------------------------------------------------------------
# 6. WhisperReader
# ---------------------------------------------------------------------------


class TestWhisperReader:
    @pytest.fixture
    def reader(self):
        return WhisperReader()

    def _config(self, model_size="base", device="cpu"):
        return {
            "Model Size": InputConfig(type="dropdown", value=model_size, description="", values=["tiny", "base", "small", "medium", "large-v3"]),
            "Device": InputConfig(type="dropdown", value=device, description="", values=["cpu", "cuda", "auto"]),
        }

    def test_reader_name(self, reader):
        assert reader.name == "Whisper"

    def test_no_env_required(self, reader):
        assert reader.requires_env == []

    def test_audio_extensions_present(self, reader):
        for ext in [".mp3", ".wav", ".mp4", ".flac", ".ogg"]:
            assert ext in reader.extension

    @pytest.mark.asyncio
    async def test_raises_when_faster_whisper_missing(self, reader):
        with patch("goldenverba.components.reader.WhisperReader.WhisperModel", None):
            with pytest.raises(ImportError, match="faster-whisper"):
                await reader.load(self._config(), _make_file_config(extension="wav", content="fake"))

    @pytest.mark.asyncio
    async def test_uses_asyncio_to_thread(self, reader):
        """_transcribe() must run in a thread, not block the event loop."""
        mock_segment = MagicMock()
        mock_segment.text = "Hello world"

        with patch("goldenverba.components.reader.WhisperReader.WhisperModel"):
            with patch("goldenverba.components.reader.WhisperReader.asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
                mock_thread.return_value = ([mock_segment], MagicMock())
                fc = _make_file_config(extension="wav", content="fake-audio")
                docs = await reader.load(self._config(), fc)

        mock_thread.assert_awaited_once()
        assert "Hello world" in docs[0].content

    @pytest.mark.asyncio
    async def test_raises_on_empty_transcript(self, reader):
        mock_segment = MagicMock()
        mock_segment.text = "   "  # whitespace only → empty after strip

        with patch("goldenverba.components.reader.WhisperReader.WhisperModel"):
            with patch("goldenverba.components.reader.WhisperReader.asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
                mock_thread.return_value = ([mock_segment], MagicMock())
                with pytest.raises(Exception, match="empty transcript"):
                    await reader.load(self._config(), _make_file_config(extension="wav", content="fake"))

    @pytest.mark.asyncio
    async def test_cleans_up_temp_file_on_success(self, reader):
        mock_segment = MagicMock()
        mock_segment.text = "Some speech"

        with patch("goldenverba.components.reader.WhisperReader.WhisperModel"):
            with patch("goldenverba.components.reader.WhisperReader.asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
                with patch("goldenverba.components.reader.WhisperReader.os.unlink") as mock_unlink:
                    mock_thread.return_value = ([mock_segment], MagicMock())
                    await reader.load(self._config(), _make_file_config(extension="wav", content="fake"))
                    mock_unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleans_up_temp_file_on_failure(self, reader):
        with patch("goldenverba.components.reader.WhisperReader.WhisperModel"):
            with patch("goldenverba.components.reader.WhisperReader.asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
                with patch("goldenverba.components.reader.WhisperReader.os.unlink") as mock_unlink:
                    mock_thread.side_effect = Exception("model crash")
                    with pytest.raises(Exception):
                        await reader.load(self._config(), _make_file_config(extension="wav", content="fake"))
                    mock_unlink.assert_called_once()


# ---------------------------------------------------------------------------
# 7. Integration tests (opt-in)
# ---------------------------------------------------------------------------


class TestHTMLReaderIntegration:
    @requires_network
    @pytest.mark.asyncio
    async def test_loads_example_com(self):
        reader = HTMLReader()
        config = {
            "URLs": InputConfig(type="multi", value="", description="", values=["https://example.com"]),
            "Convert To Markdown": InputConfig(type="bool", value=False, description="", values=[]),
            "Recursive": InputConfig(type="bool", value=False, description="", values=[]),
            "Max Depth": InputConfig(type="number", value=1, description="", values=[]),
        }
        docs = await reader.load(config, _make_file_config())
        assert len(docs) == 1
        assert len(docs[0].content) > 0


class TestUnstructuredIntegration:
    @requires_unstructured
    @pytest.mark.asyncio
    async def test_loads_plain_text(self):
        reader = UnstructuredReader()
        config = {
            "Strategy": InputConfig(type="dropdown", value="auto", description="", values=["auto", "hi_res", "ocr_only", "fast"]),
            "API Key": InputConfig(type="password", value=os.environ["UNSTRUCTURED_API_KEY"], description="", values=[]),
            # Always use the current production URL regardless of any stale env var
            "API URL": InputConfig(
                type="text",
                value="https://api.unstructuredapp.io/general/v0/general",
                description="",
                values=[],
            ),
        }
        fc = _make_file_config(filename="test.txt", extension="txt", content="Hello from Verba integration test.")
        try:
            docs = await reader.load(config, fc)
        except Exception as e:
            msg = str(e)
            if "Cannot connect to host" in msg or "nodename nor servname" in msg:
                pytest.skip(f"Unstructured API unreachable: {e}")
            if "401" in msg or "Unauthorized" in msg:
                pytest.skip(f"Unstructured API key invalid or expired: {e}")
            raise
        assert len(docs) == 1
        assert len(docs[0].content) > 0


class TestGitReaderIntegration:
    @requires_github
    @pytest.mark.asyncio
    async def test_reads_public_github_repo(self):
        reader = GitReader()
        config = {
            "Platform": InputConfig(type="dropdown", value="GitHub", description="", values=["GitHub", "GitLab"]),
            "Owner": InputConfig(type="text", value="weaviate", description="", values=[]),
            "Name": InputConfig(type="text", value="Verba", description="", values=[]),
            "Branch": InputConfig(type="text", value="main", description="", values=[]),
            "Path": InputConfig(type="text", value="README.md", description="", values=[]),
            "Git Token": InputConfig(type="password", value=os.environ["GITHUB_TOKEN"], description="", values=[]),
        }
        docs = await reader.load(config, _make_file_config())
        assert len(docs) >= 1
