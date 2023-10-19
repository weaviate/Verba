from weaviate import Client
from wasabi import msg

from goldenverba.ingestion.embedding.interface import Embedder
from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import InputForm
from goldenverba.ingestion.schema.schema_generation import (
    VECTORIZERS,
    EMBEDDINGS,
    strip_non_letters,
)


class ADAEmbedder(Embedder):
    """
    ADAEmbedder for Verba
    """

    def __init__(self):
        super().__init__()
        self.name = "ADAEmbedder"
        self.requires_env = ["OPENAI_API_KEY"]
        self.requires_library = ["openai"]
        self.description = "Embeds and retrieves objects using OpenAI's ADA model"
        self.vectorizer = "text2vec-openai"

    def embed(
        self,
        documents: list[Document],
        client: Client,
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful
        """
        return self.import_data(documents, client)
