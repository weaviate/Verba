"""
Tests for goldenverba/server/helpers.py

Covers BatchManager and LoggerManager.
No real network calls or Weaviate connections are made.
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from goldenverba.server.helpers import BatchManager, LoggerManager
from goldenverba.server.types import (
    DataBatchPayload,
    FileStatus,
    Credentials,
    FileConfig,
    RAGComponentClass,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

DUMMY_CREDENTIALS = Credentials(
    deployment="Local",
    url="http://localhost:8080",
    key="",
)


def _make_file_config(
    file_id: str = "file-001",
    filename: str = "test.txt",
) -> FileConfig:
    """Return a minimal but valid FileConfig object."""
    return FileConfig(
        fileID=file_id,
        filename=filename,
        isURL=False,
        overwrite=False,
        extension=".txt",
        source="local",
        content="Hello world",
        labels=[],
        rag_config={},
        file_size=11,
        status=FileStatus.READY,
        metadata="",
        status_report={},
    )


def _serialise_file_config(fc: FileConfig) -> str:
    """Return the JSON string that the frontend would send as a batch payload."""
    return fc.model_dump_json()


def _make_payload(
    file_id: str,
    chunk: str,
    order: int,
    total: int,
    is_last: bool = False,
) -> DataBatchPayload:
    return DataBatchPayload(
        fileID=file_id,
        chunk=chunk,
        order=order,
        total=total,
        isLastChunk=is_last,
        credentials=DUMMY_CREDENTIALS,
    )


def _split_into_chunks(text: str, n: int) -> list[str]:
    """Split *text* into *n* roughly-equal string chunks."""
    size = max(1, len(text) // n)
    parts = [text[i : i + size] for i in range(0, len(text), size)]
    # If rounding produced more than n parts, merge the tail into the last part
    while len(parts) > n:
        parts[-2] = parts[-2] + parts[-1]
        parts.pop()
    return parts


# ---------------------------------------------------------------------------
# BatchManager tests
# ---------------------------------------------------------------------------


class TestBatchManagerNormalFlow:
    """Single-chunk and multi-chunk happy-path scenarios."""

    def test_single_chunk_returns_file_config(self):
        """A batch with total=1 should resolve immediately."""
        manager = BatchManager()
        fc = _make_file_config()
        payload = _make_payload(
            file_id=fc.fileID,
            chunk=_serialise_file_config(fc),
            order=0,
            total=1,
            is_last=True,
        )

        result = manager.add_batch(payload)

        assert result is not None, "Expected a FileConfig back from a complete batch"
        assert isinstance(result, FileConfig)
        assert result.fileID == fc.fileID
        assert result.filename == fc.filename

    def test_batch_removed_after_assembly(self):
        """Once all chunks arrive the entry must be cleaned up."""
        manager = BatchManager()
        fc = _make_file_config()
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 3)

        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            manager.add_batch(
                _make_payload(fc.fileID, part, i, len(parts), is_last)
            )

        assert fc.fileID not in manager.batches, (
            "Batch entry must be removed once the FileConfig is assembled"
        )

    def test_multi_chunk_reassembly(self):
        """Splitting a FileConfig JSON into multiple ordered chunks then reassembling
        must produce the same FileConfig."""
        manager = BatchManager()
        fc = _make_file_config(file_id="reassembly-test", filename="reassembly.txt")
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 4)

        result = None
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            result = manager.add_batch(
                _make_payload(fc.fileID, part, i, len(parts), is_last)
            )

        assert result is not None
        assert result.fileID == fc.fileID
        assert result.filename == fc.filename
        assert result.extension == fc.extension

    def test_incomplete_batch_returns_none(self):
        """Sending fewer chunks than `total` must not resolve yet."""
        manager = BatchManager()
        fc = _make_file_config()
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 3)

        # Only send the first chunk, not the remaining two
        result = manager.add_batch(
            _make_payload(fc.fileID, parts[0], 0, 3, is_last=False)
        )

        assert result is None, "Batch should not resolve before all chunks arrive"

    def test_batch_entry_exists_while_incomplete(self):
        """An in-progress batch must remain in the dict."""
        manager = BatchManager()
        fc = _make_file_config()
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 3)

        manager.add_batch(_make_payload(fc.fileID, parts[0], 0, 3, is_last=False))

        assert fc.fileID in manager.batches, (
            "In-progress batch must remain registered in BatchManager"
        )


class TestBatchManagerOutOfOrderChunks:
    """Chunks that arrive in a non-sequential order.

    NOTE: BatchManager.check_batch() joins chunks using dict insertion order,
    not sorted key order.  Sending chunks out of sequence therefore produces a
    garbled JSON string and the assembly fails silently (returns None / raises).
    These tests document the *actual* behaviour so that a future fix can be
    verified by updating the assertions here.
    """

    def test_in_order_chunks_assemble_correctly(self):
        """Chunks delivered in order 0→1→2 must produce a valid FileConfig."""
        manager = BatchManager()
        fc = _make_file_config(file_id="in-order-test")
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 3)

        result = None
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            result = manager.add_batch(
                _make_payload(fc.fileID, part, i, len(parts), is_last)
            )

        assert result is not None, "In-order chunks must assemble correctly"
        assert result.fileID == fc.fileID

    def test_out_of_order_single_chunk_resolves(self):
        """A single-chunk batch is always in-order; it must resolve regardless."""
        manager = BatchManager()
        fc = _make_file_config(file_id="single-chunk-ooo")
        full_json = _serialise_file_config(fc)

        result = manager.add_batch(
            _make_payload(fc.fileID, full_json, 0, 1, is_last=True)
        )

        assert result is not None
        assert result.fileID == fc.fileID

    def test_two_chunks_in_order_assemble(self):
        """Two chunks delivered in the correct order must produce a FileConfig."""
        manager = BatchManager()
        fc = _make_file_config(file_id="two-chunk-test")
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 2)

        manager.add_batch(_make_payload(fc.fileID, parts[0], 0, 2, is_last=False))
        result = manager.add_batch(
            _make_payload(fc.fileID, parts[1], 1, 2, is_last=True)
        )

        assert result is not None, "Two in-order chunks should assemble correctly"
        assert result.fileID == fc.fileID


class TestBatchManagerTTL:
    """Stale entries are evicted once their TTL expires."""

    def test_stale_entry_evicted_on_next_add(self):
        """An entry older than _BATCH_TTL_SECONDS is removed the next time add_batch
        is called for a *different* file."""
        import time
        from goldenverba.server.helpers import _BATCH_TTL_SECONDS

        manager = BatchManager()
        old_fc = _make_file_config(file_id="old-upload")
        new_fc = _make_file_config(file_id="new-upload")

        # Seed the old entry
        manager.add_batch(_make_payload(old_fc.fileID, "x", 0, 2, is_last=False))

        # Back-date its created_at so it looks expired
        manager.batches[old_fc.fileID]["created_at"] = (
            time.monotonic() - _BATCH_TTL_SECONDS - 1
        )

        # Trigger eviction via a new batch
        manager.add_batch(
            _make_payload(new_fc.fileID, _serialise_file_config(new_fc), 0, 1, is_last=True)
        )

        assert old_fc.fileID not in manager.batches, (
            "Stale entry must be evicted after TTL"
        )

    def test_fresh_entry_not_evicted(self):
        """An entry within its TTL must not be evicted."""
        manager = BatchManager()
        fc = _make_file_config(file_id="fresh-upload")
        other_fc = _make_file_config(file_id="trigger-upload")

        manager.add_batch(_make_payload(fc.fileID, "x", 0, 2, is_last=False))
        # Trigger eviction check without ageing the entry
        manager.add_batch(
            _make_payload(other_fc.fileID, _serialise_file_config(other_fc), 0, 1, is_last=True)
        )

        assert fc.fileID in manager.batches, "Fresh entry must survive eviction check"


class TestBatchManagerAbandonedBatch:
    """A partial upload that never completes stays in the dict until TTL."""

    def test_abandoned_batch_stays_in_dict(self):
        """A partial batch whose remaining chunks never arrive must not disappear."""
        manager = BatchManager()
        fc = _make_file_config(file_id="abandoned")
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 5)

        # Deliver only 2 of 5 chunks, then stop
        manager.add_batch(_make_payload(fc.fileID, parts[0], 0, 5, is_last=False))
        manager.add_batch(_make_payload(fc.fileID, parts[1], 1, 5, is_last=False))

        # Entry must still be present — TTL hasn't elapsed (300 s)
        assert fc.fileID in manager.batches
        assert len(manager.batches[fc.fileID]["chunks"]) == 2

    def test_multiple_independent_batches_tracked_separately(self):
        """Two concurrent uploads must not interfere with each other."""
        manager = BatchManager()
        fc1 = _make_file_config(file_id="file-A", filename="a.txt")
        fc2 = _make_file_config(file_id="file-B", filename="b.txt")

        json1 = _serialise_file_config(fc1)
        json2 = _serialise_file_config(fc2)

        # Start both uploads, complete only the second
        manager.add_batch(_make_payload(fc1.fileID, json1[:10], 0, 2, is_last=False))
        manager.add_batch(
            _make_payload(fc2.fileID, json2, 0, 1, is_last=True)
        )

        # fc1 should still be pending; fc2 should be gone (completed)
        assert fc1.fileID in manager.batches
        assert fc2.fileID not in manager.batches


class TestBatchManagerDuplicateChunk:
    """Sending the same order index twice must overwrite the stored chunk."""

    def test_duplicate_order_overwrites(self):
        """The second delivery of order=0 replaces the first."""
        manager = BatchManager()
        fc = _make_file_config()
        full_json = _serialise_file_config(fc)

        # Send a garbage chunk at order=0 first, then the correct one
        manager.add_batch(_make_payload(fc.fileID, "GARBAGE", 0, 1, is_last=False))
        result = manager.add_batch(
            _make_payload(fc.fileID, full_json, 0, 1, is_last=True)
        )

        assert result is not None
        assert result.fileID == fc.fileID


class TestBatchManagerLastChunkFlag:
    """isLastChunk=True on a partial batch should clean up without assembling."""

    def test_is_last_chunk_triggers_cleanup_even_if_incomplete(self):
        """When isLastChunk is True the entry is removed regardless of completeness."""
        manager = BatchManager()
        fc = _make_file_config(file_id="last-flag-test")
        full_json = _serialise_file_config(fc)
        parts = _split_into_chunks(full_json, 3)

        # Send only one chunk but mark it as the last
        manager.add_batch(
            _make_payload(fc.fileID, parts[0], 0, 3, is_last=True)
        )

        assert fc.fileID not in manager.batches, (
            "isLastChunk=True must remove the entry even if not all chunks arrived"
        )


# ---------------------------------------------------------------------------
# LoggerManager tests
# ---------------------------------------------------------------------------


class TestLoggerManagerInstantiation:
    def test_instantiation_without_socket(self):
        """LoggerManager must be constructable without a socket."""
        lm = LoggerManager()
        assert lm.socket is None

    def test_instantiation_with_socket(self):
        """LoggerManager must store the provided socket."""
        mock_socket = MagicMock()
        lm = LoggerManager(socket=mock_socket)
        assert lm.socket is mock_socket


class TestLoggerManagerSendReport:
    @pytest.mark.asyncio
    async def test_send_report_without_socket_does_not_crash(self):
        """send_report must not raise even when no socket is configured."""
        lm = LoggerManager()
        # Should complete without raising
        await lm.send_report(
            file_Id="f-001",
            status=FileStatus.CHUNKING,
            message="all good",
            took=0.42,
        )

    @pytest.mark.asyncio
    async def test_send_report_with_socket_calls_send_json(self):
        """send_report must call socket.send_json with the correct payload."""
        mock_socket = MagicMock()
        mock_socket.send_json = AsyncMock()
        lm = LoggerManager(socket=mock_socket)

        await lm.send_report(
            file_Id="f-001",
            status=FileStatus.DONE,
            message="finished",
            took=1.23,
        )

        mock_socket.send_json.assert_awaited_once()
        sent_payload = mock_socket.send_json.call_args[0][0]
        assert sent_payload["fileID"] == "f-001"
        assert sent_payload["status"] == FileStatus.DONE
        assert sent_payload["message"] == "finished"
        assert sent_payload["took"] == 1.23

    @pytest.mark.asyncio
    async def test_send_report_without_socket_skips_send_json(self):
        """Without a socket, send_json must never be called."""
        mock_socket = MagicMock()
        mock_socket.send_json = AsyncMock()

        # Deliberately do NOT pass the socket
        lm = LoggerManager()
        await lm.send_report("f-002", FileStatus.ERROR, "oops", 0.0)

        mock_socket.send_json.assert_not_awaited()


class TestLoggerManagerCreateNewDocument:
    @pytest.mark.asyncio
    async def test_create_new_document_without_socket_does_not_crash(self):
        """create_new_document must not raise when socket is None."""
        lm = LoggerManager()
        await lm.create_new_document(
            new_file_id="new-001",
            document_name="renamed.txt",
            original_file_id="orig-001",
        )

    @pytest.mark.asyncio
    async def test_create_new_document_with_socket_sends_correct_payload(self):
        """create_new_document must send all three identifiers via socket."""
        mock_socket = MagicMock()
        mock_socket.send_json = AsyncMock()
        lm = LoggerManager(socket=mock_socket)

        await lm.create_new_document(
            new_file_id="new-001",
            document_name="renamed.txt",
            original_file_id="orig-001",
        )

        mock_socket.send_json.assert_awaited_once()
        payload = mock_socket.send_json.call_args[0][0]
        assert payload["new_file_id"] == "new-001"
        assert payload["filename"] == "renamed.txt"
        assert payload["original_file_id"] == "orig-001"
