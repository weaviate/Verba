from weaviate import Client

from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import InputForm


class Embedder:
    """
    Interface for Verba Embedding
    """

    def __init__(self):
        self.name = ""
        self.requires_env = []
        self.requires_library = []
        self.input_form = InputForm.TEXT.value  # Default for all Embedders
        self.description = ""
        self.vectorizer = "text2vec-openai"

    def embed(documents: list[Document], client: Client, batch_size: int = 100) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")
