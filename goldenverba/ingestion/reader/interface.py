from goldenverba.ingestion.util import setup_client
from goldenverba.ingestion.reader.document import Document


class Reader:
    """
    Interface for Verba Readers
    """

    def __init__(self):
        self.client = setup_client()

    def load(paths: list[str], document_type: str) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: paths : list[str] - List of paths to resources
        @parameter: document_type : str - Document type
        @returns list[str] - List of strings
        """
        raise NotImplementedError("load method must be implemented by a subclass.")
