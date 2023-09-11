import glob
from datetime import datetime

from pathlib import Path
from wasabi import msg

from goldenverba.ingestion.chunking.interface import Chunker
from goldenverba.ingestion.reader.document import Document


class WordChunker(Chunker):
    """
    WordChunker for Verba
    """

    def __init__(self):
        self.name = "TextReader"
        self.requires_env = []
        self.description = "Chunks documents based by words."

    def chunk(documents: list[Document], units: int, overlap: int) -> list[Document]:
        """Chunk verba documents into chunks based on n and overlap
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")
