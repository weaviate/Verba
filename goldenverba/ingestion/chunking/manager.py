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
        return self.selected_chunker.chunk(documents, units, overlap)

    def set_chunker(self, chunker: str) -> bool:
        if chunker in self.chunker:
            self.selected_chunker = self.chunker[chunker]
            return True
        else:
            msg.warn(f"Chunker {chunker} not found")
            return False

    def get_chunkers(self) -> dict[str, Chunker]:
        return self.chunker
