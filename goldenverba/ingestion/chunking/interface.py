from enum import Enum

from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import InputForm


class Chunker:
    """
    Interface for Verba Chunking
    """

    def __init__(self):
        self.name = ""
        self.requires_env = []
        self.input_form = InputForm.CHUNKER.value  # Default for all Chunkers
        self.description = ""

    def chunk(documents: list[Document], units: int, overlap: int) -> list[Document]:
        """Chunk verba documents into chunks based on units and overlap
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")
