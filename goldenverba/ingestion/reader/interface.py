from enum import Enum

from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.component import VerbaComponent


class InputForm(Enum):
    UPLOAD = "UPLOAD"  # Input Form to upload text files directly
    INPUT = "INPUT"  # Simple Text Input in Frontend
    CHUNKER = "CHUNKER"  # Default Input for Chunkers
    TEXT = "TEXT"  # Default Input for Embedder


class Reader(VerbaComponent):
    """
    Interface for Verba Readers
    """

    def __init__(self):
        super().__init__()
        self.file_types = []
        self.input_form = InputForm.UPLOAD.value

    def load(
        bytes: list[str],
        contents: list[str],
        paths: list[str],
        fileNames: list[str],
        document_type: str,
    ) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: bytes : list[str] - List of bytes
        @parameter: contents : list[str] - List of string content
        @parameter: paths : list[str] - List of paths to files
        @parameter: fileNames : list[str] - List of file names
        @parameter: document_type : str - Document type
        @returns list[str] - List of strings
        """
        raise NotImplementedError("load method must be implemented by a subclass.")
