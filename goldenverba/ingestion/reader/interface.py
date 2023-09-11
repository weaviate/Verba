from enum import Enum

from goldenverba.ingestion.reader.document import Document


class InputForm(Enum):
    UPLOAD = "UPLOAD"  # Input Form to upload text files directly
    INPUT = "INPUT"  # Simple Text Input in Frontend


class Reader:
    """
    Interface for Verba Readers
    """

    def __init__(self):
        self.name = "Reader"
        self.file_types = []
        self.requires_env = []
        self.description = ""
        self.input_form = InputForm.UPLOAD.value

    def load(contents: list[str], document_type: str) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: contents : list[str] - List of paths to resources
        @parameter: document_type : str - Document type
        @returns list[str] - List of strings
        """
        raise NotImplementedError("load method must be implemented by a subclass.")
