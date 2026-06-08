"""
Tests for the three built-in chunkers:
  - TokenChunker   (goldenverba/components/chunking/TokenChunker.py)
  - SentenceChunker (goldenverba/components/chunking/SentenceChunker.py)
  - MarkdownChunker (goldenverba/components/chunking/MarkdownChunker.py)

These are pure text-processing operations – no network calls required.
"""
import pytest

from goldenverba.components.document import Document
from goldenverba.components.chunk import Chunk
from goldenverba.components.types import InputConfig
from goldenverba.components.chunking.TokenChunker import TokenChunker
from goldenverba.components.chunking.SentenceChunker import SentenceChunker
from goldenverba.components.chunking.MarkdownChunker import MarkdownChunker


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

SHORT_SENTENCE = "The quick brown fox jumps over the lazy dog."

MULTI_SENTENCE = (
    "The sun rose early. Birds began to sing. The air was crisp and cool. "
    "Children ran outside to play. A gentle breeze rustled the leaves. "
    "It was a perfect morning. Everyone felt alive and refreshed."
)

LONG_TOKEN_TEXT = " ".join([f"word{i}" for i in range(600)])

MARKDOWN_TEXT = """\
# Introduction

This is the introduction paragraph with some text.

## Background

Here is some background information that explains the context.

### Details

Fine-grained details live under this subsection.

## Summary

A brief wrap-up of what was covered.
"""


def _make_token_config(tokens: int = 50, overlap: int = 10) -> dict[str, InputConfig]:
    return {
        "Tokens": InputConfig(
            type="number", value=tokens, description="Tokens per chunk", values=[]
        ),
        "Overlap": InputConfig(
            type="number", value=overlap, description="Overlap tokens", values=[]
        ),
    }


def _make_sentence_config(
    sentences: int = 2, overlap: int = 0
) -> dict[str, InputConfig]:
    return {
        "Sentences": InputConfig(
            type="number",
            value=sentences,
            description="Sentences per chunk",
            values=[],
        ),
        "Overlap": InputConfig(
            type="number", value=overlap, description="Overlap sentences", values=[]
        ),
    }


# ---------------------------------------------------------------------------
# TokenChunker
# ---------------------------------------------------------------------------


class TestTokenChunker:
    def _chunker(self) -> TokenChunker:
        return TokenChunker()

    @pytest.mark.asyncio
    async def test_produces_chunks(self):
        """TokenChunker should split a long document into multiple chunks."""
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(50, 0), [doc])

        assert len(result) == 1
        assert len(result[0].chunks) > 1, "Expected multiple chunks for a long text"

    @pytest.mark.asyncio
    async def test_returns_list_of_chunk_objects(self):
        """Every element in document.chunks must be a Chunk instance."""
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(50, 0), [doc])

        for chunk in result[0].chunks:
            assert isinstance(chunk, Chunk)

    @pytest.mark.asyncio
    async def test_chunks_have_content(self):
        """Each chunk must have non-empty content."""
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(50, 0), [doc])

        for chunk in result[0].chunks:
            assert chunk.content.strip() != "", "Chunk content must not be empty"

    @pytest.mark.asyncio
    async def test_chunk_ids_are_sequential(self):
        """chunk_id values must form a contiguous sequence starting at 0."""
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(50, 0), [doc])

        ids = [c.chunk_id for c in result[0].chunks]
        assert ids == list(range(len(ids)))

    @pytest.mark.asyncio
    async def test_respects_max_token_size(self):
        """Each chunk should contain at most (tokens + overlap) words."""
        tokens = 30
        overlap = 5
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(tokens, overlap), [doc])

        for chunk in result[0].chunks:
            word_count = len(chunk.content.split())
            assert word_count <= tokens + overlap + 5, (
                f"Chunk has {word_count} words, expected <= {tokens + overlap}"
            )

    @pytest.mark.asyncio
    async def test_overlap_text_is_shared(self):
        """With overlap > 0, the tail of one chunk should appear at the head of next."""
        tokens = 10
        overlap = 3
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(tokens, overlap), [doc])
        chunks = result[0].chunks

        if len(chunks) >= 2:
            # Last 'overlap' words of chunk 0 should appear in chunk 1
            tail_words = chunks[0].content.split()[-overlap:]
            head_words = chunks[1].content.split()[:overlap]
            assert tail_words == head_words, (
                "Overlap words from chunk[0] should appear at start of chunk[1]"
            )

    @pytest.mark.asyncio
    async def test_empty_string_yields_one_chunk(self):
        """An empty document should still produce exactly one (empty) chunk."""
        doc = Document(content="")
        result = await self._chunker().chunk(_make_token_config(50, 0), [doc])

        # The chunker either produces 0 chunks or 1 empty chunk; it must not crash
        assert isinstance(result[0].chunks, list)

    @pytest.mark.asyncio
    async def test_very_short_text_yields_single_chunk(self):
        """Text shorter than one chunk boundary should result in a single chunk."""
        doc = Document(content=SHORT_SENTENCE)
        result = await self._chunker().chunk(_make_token_config(250, 50), [doc])

        assert len(result[0].chunks) == 1
        assert result[0].chunks[0].content == SHORT_SENTENCE

    @pytest.mark.asyncio
    async def test_overlap_clamped_when_greater_than_units(self):
        """When overlap >= units the chunker should clamp overlap and not crash."""
        doc = Document(content=LONG_TOKEN_TEXT)
        # overlap (60) > tokens (50) -- the chunker should handle this gracefully
        result = await self._chunker().chunk(_make_token_config(50, 60), [doc])

        assert len(result[0].chunks) >= 1

    @pytest.mark.asyncio
    async def test_skips_already_chunked_documents(self):
        """If a document already has chunks, the chunker must leave them unchanged."""
        doc = Document(content=LONG_TOKEN_TEXT)
        pre_existing_chunk = Chunk(
            content="pre-existing",
            chunk_id=0,
            start_i=0,
            end_i=12,
            content_without_overlap="pre-existing",
        )
        doc.chunks.append(pre_existing_chunk)

        result = await self._chunker().chunk(_make_token_config(50, 0), [doc])

        assert len(result[0].chunks) == 1
        assert result[0].chunks[0].content == "pre-existing"

    @pytest.mark.asyncio
    async def test_content_without_overlap_shorter_or_equal_to_content(self):
        """content_without_overlap must be <= content in length."""
        doc = Document(content=LONG_TOKEN_TEXT)
        result = await self._chunker().chunk(_make_token_config(20, 5), [doc])

        for chunk in result[0].chunks:
            assert len(chunk.content_without_overlap) <= len(chunk.content)


# ---------------------------------------------------------------------------
# SentenceChunker
# ---------------------------------------------------------------------------


class TestSentenceChunker:
    def _chunker(self) -> SentenceChunker:
        return SentenceChunker()

    @pytest.mark.asyncio
    async def test_splits_on_sentence_boundaries(self):
        """SentenceChunker should produce more than one chunk for multi-sentence text."""
        doc = Document(content=MULTI_SENTENCE)
        result = await self._chunker().chunk(_make_sentence_config(2, 0), [doc])

        assert len(result[0].chunks) > 1

    @pytest.mark.asyncio
    async def test_returns_chunk_instances(self):
        """Every element of document.chunks must be a Chunk."""
        doc = Document(content=MULTI_SENTENCE)
        result = await self._chunker().chunk(_make_sentence_config(2, 0), [doc])

        for chunk in result[0].chunks:
            assert isinstance(chunk, Chunk)

    @pytest.mark.asyncio
    async def test_chunk_content_is_nonempty(self):
        """Chunks must not be blank."""
        doc = Document(content=MULTI_SENTENCE)
        result = await self._chunker().chunk(_make_sentence_config(2, 0), [doc])

        for chunk in result[0].chunks:
            assert chunk.content.strip() != ""

    @pytest.mark.asyncio
    async def test_chunk_ids_sequential(self):
        """chunk_id values must be contiguous starting from 0."""
        doc = Document(content=MULTI_SENTENCE)
        result = await self._chunker().chunk(_make_sentence_config(2, 0), [doc])
        ids = [c.chunk_id for c in result[0].chunks]
        assert ids == list(range(len(ids)))

    @pytest.mark.asyncio
    async def test_single_sentence_yields_one_chunk(self):
        """A document with a single sentence should end up in a single chunk."""
        doc = Document(content=SHORT_SENTENCE)
        result = await self._chunker().chunk(_make_sentence_config(5, 1), [doc])

        assert len(result[0].chunks) == 1
        assert result[0].chunks[0].content.strip() == SHORT_SENTENCE.strip()

    @pytest.mark.asyncio
    async def test_overlap_produces_shared_sentences(self):
        """With sentence-level overlap the last sentence of one chunk should
        appear at the start of the next chunk's content."""
        doc = Document(content=MULTI_SENTENCE)
        # 2 sentences per chunk, 1 sentence overlap
        result = await self._chunker().chunk(_make_sentence_config(2, 1), [doc])
        chunks = result[0].chunks

        if len(chunks) >= 2:
            # The last sentence of chunk 0 must appear in chunk 1
            last_sentence_chunk0 = chunks[0].content.split(".")[-2].strip()
            assert last_sentence_chunk0 in chunks[1].content, (
                "Overlapping sentence from chunk[0] should appear in chunk[1]"
            )

    @pytest.mark.asyncio
    async def test_overlap_clamped_when_too_large(self):
        """overlap >= sentences must be clamped without crashing."""
        doc = Document(content=MULTI_SENTENCE)
        # overlap (5) >= sentences (3)
        result = await self._chunker().chunk(_make_sentence_config(3, 5), [doc])
        assert len(result[0].chunks) >= 1

    @pytest.mark.asyncio
    async def test_skips_already_chunked_documents(self):
        """Pre-chunked documents must not be re-chunked."""
        doc = Document(content=MULTI_SENTENCE)
        sentinel = Chunk(
            content="sentinel",
            chunk_id=0,
            start_i=0,
            end_i=8,
            content_without_overlap="sentinel",
        )
        doc.chunks.append(sentinel)

        result = await self._chunker().chunk(_make_sentence_config(2, 0), [doc])

        assert len(result[0].chunks) == 1
        assert result[0].chunks[0].content == "sentinel"

    @pytest.mark.asyncio
    async def test_all_text_covered(self):
        """Concatenating content_without_overlap for all chunks should cover
        all of the original sentences (no sentence should be lost)."""
        doc = Document(content=MULTI_SENTENCE)
        result = await self._chunker().chunk(_make_sentence_config(2, 0), [doc])

        combined = " ".join(c.content_without_overlap for c in result[0].chunks)
        # Every sentence from the source must appear somewhere in the combination
        for sentence in MULTI_SENTENCE.split("."):
            sentence = sentence.strip()
            if sentence:
                assert sentence in combined, (
                    f"Sentence '{sentence}' is missing from combined chunks"
                )


# ---------------------------------------------------------------------------
# MarkdownChunker
# ---------------------------------------------------------------------------


class TestMarkdownChunker:
    def _chunker(self) -> MarkdownChunker:
        return MarkdownChunker()

    @pytest.mark.asyncio
    async def test_splits_by_headers(self):
        """MarkdownChunker should produce one chunk per top-level section."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])

        # Our sample has 4 sections (Introduction, Background, Details, Summary)
        assert len(result[0].chunks) >= 3

    @pytest.mark.asyncio
    async def test_returns_chunk_instances(self):
        """Every element in document.chunks must be a Chunk."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])

        for chunk in result[0].chunks:
            assert isinstance(chunk, Chunk)

    @pytest.mark.asyncio
    async def test_chunk_content_nonempty(self):
        """No chunk produced by the MarkdownChunker should be empty."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])

        for chunk in result[0].chunks:
            assert chunk.content.strip() != ""

    @pytest.mark.asyncio
    async def test_chunk_ids_sequential(self):
        """chunk_id values must form a sequence starting at 0."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])
        ids = [c.chunk_id for c in result[0].chunks]
        assert ids == list(range(len(ids)))

    @pytest.mark.asyncio
    async def test_headers_prepended_to_chunk_content(self):
        """Fix for PR #323: header text must appear inside the chunk so retrieval
        is context-aware even when the section body alone is ambiguous."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])

        # The 'Background' section chunk must contain 'Background' in its content
        background_chunks = [
            c for c in result[0].chunks if "Background" in c.content
        ]
        assert len(background_chunks) >= 1, (
            "Expected at least one chunk whose content includes the 'Background' header"
        )

    @pytest.mark.asyncio
    async def test_nested_headers_included_in_chunk(self):
        """A subsection chunk should include its ancestor header names (PR #323)."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])

        details_chunks = [c for c in result[0].chunks if "Details" in c.content]
        assert len(details_chunks) >= 1, (
            "Chunk for the '### Details' subsection must include the header text"
        )

    @pytest.mark.asyncio
    async def test_content_without_overlap_equals_content(self):
        """MarkdownChunker has no overlap concept; both fields should be equal."""
        doc = Document(content=MARKDOWN_TEXT)
        result = await self._chunker().chunk({}, [doc])

        for chunk in result[0].chunks:
            assert chunk.content == chunk.content_without_overlap

    @pytest.mark.asyncio
    async def test_plain_text_no_headers_yields_one_chunk(self):
        """Markdown text with no headers should produce a single chunk."""
        doc = Document(content="Just a plain paragraph without any headings.")
        result = await self._chunker().chunk({}, [doc])

        assert len(result[0].chunks) == 1

    @pytest.mark.asyncio
    async def test_skips_already_chunked_documents(self):
        """Pre-chunked documents must not be re-chunked."""
        doc = Document(content=MARKDOWN_TEXT)
        sentinel = Chunk(
            content="sentinel",
            chunk_id=0,
            start_i=0,
            end_i=8,
            content_without_overlap="sentinel",
        )
        doc.chunks.append(sentinel)

        result = await self._chunker().chunk({}, [doc])

        assert len(result[0].chunks) == 1
        assert result[0].chunks[0].content == "sentinel"

    @pytest.mark.asyncio
    async def test_multiple_documents_chunked_independently(self):
        """Each document in the list must be chunked independently."""
        doc1 = Document(content=MARKDOWN_TEXT)
        doc2 = Document(content="# Solo\n\nOnly one section here.")

        result = await self._chunker().chunk({}, [doc1, doc2])

        assert len(result[0].chunks) >= 3, "First doc should have several sections"
        assert len(result[1].chunks) == 1, "Second doc has one section"


# ---------------------------------------------------------------------------
# Cross-chunker contract tests
# ---------------------------------------------------------------------------


class TestChunkerContracts:
    """Every chunker must satisfy a shared contract."""

    CHUNKERS = [
        (TokenChunker, _make_token_config(50, 0)),
        (SentenceChunker, _make_sentence_config(2, 0)),
        (MarkdownChunker, {}),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("chunker_cls,config", CHUNKERS)
    async def test_returns_list_of_documents(self, chunker_cls, config):
        doc = Document(content=MULTI_SENTENCE)
        result = await chunker_cls().chunk(config, [doc])
        assert isinstance(result, list)
        assert all(isinstance(d, Document) for d in result)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("chunker_cls,config", CHUNKERS)
    async def test_chunks_are_chunk_instances(self, chunker_cls, config):
        doc = Document(content=MULTI_SENTENCE)
        result = await chunker_cls().chunk(config, [doc])
        for chunk in result[0].chunks:
            assert isinstance(chunk, Chunk)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("chunker_cls,config", CHUNKERS)
    async def test_no_empty_chunks(self, chunker_cls, config):
        doc = Document(content=MULTI_SENTENCE)
        result = await chunker_cls().chunk(config, [doc])
        for chunk in result[0].chunks:
            assert chunk.content.strip() != ""
