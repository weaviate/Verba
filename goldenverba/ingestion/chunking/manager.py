import tiktoken

from goldenverba.ingestion.chunking.wordchunker import WordChunker
from goldenverba.ingestion.chunking.sentencechunker import SentenceChunker
from goldenverba.ingestion.chunking.interface import Chunker
from goldenverba.ingestion.reader.document import Document

from wasabi import msg


class ChunkerManager:
    def __init__(self):
        self.chunker: dict[str, Chunker] = {
            "WordChunker": WordChunker(),
            "SentenceChunker": SentenceChunker(),
        }
        self.selected_chunker: Chunker = self.chunker["WordChunker"]

    def chunk(
        self, documents: list[Document], units: int, overlap: int
    ) -> list[Document]:
        """Chunk verba documents into chunks based on n and overlap
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks
        """
        chunked_docs = self.selected_chunker.chunk(documents, units, overlap)
        if self.check_chunks(chunked_docs):
            return chunked_docs
        return []

    def set_chunker(self, chunker: str) -> bool:
        if chunker in self.chunker:
            self.selected_chunker = self.chunker[chunker]
            return True
        else:
            msg.warn(f"Chunker {chunker} not found")
            return False

    def get_chunkers(self) -> dict[str, Chunker]:
        return self.chunker

    def check_chunks(self, documents: list[Document]) -> bool:
        """Checks token count of chunks which are hardcapped to 1000 tokens per chunk
        @parameter: documents : list[Document] - List of Verba documents
        @returns bool - Whether the chunks are within the token range
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        for document in documents:
            chunks = document.chunks
            for chunk in chunks:
                tokens = encoding.encode(chunk.text, disallowed_special=())
                chunk.set_tokens(tokens)
                if len(tokens) > 1000:
                    raise Exception(
                        "Chunk detected with more than 1000 tokens which exceeds the maximum size. Please reduce size of your chunk."
                    )

        return True
