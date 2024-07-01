from weaviate import Client

from goldenverba.components.interfaces import Embedder
from goldenverba.components.document import Document


class ADAEmbedder(Embedder):
    """
    ADAEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "ADAEmbedder"
        self.requires_env = ["OPENAI_API_KEY"]
        self.description = "Embeds and retrieves objects using OpenAI's ADA model"
        self.vectorizer = "text2vec-openai"

    def embed(
        self, documents: list[Document], client: Client, logging: list[dict]
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        return self.import_data(documents, client, logging)
