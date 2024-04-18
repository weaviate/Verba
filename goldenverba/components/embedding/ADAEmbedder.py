from weaviate import WeaviateClient

from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.reader.document import Document

from verba_types import VectorizerOrEmbeddingType, VectorizerType

import weaviate.classes.config as wvc


class ADAEmbedder(Embedder):
    """
    ADAEmbedder for Verba.
    """

    def __init__(self):
        super().__init__(
            vectorizer=VectorizerType(
                name="text2vecopenai",
                config_class=wvc.Configure.NamedVectors.text2vec_openai,
            )
        )
        self.name = "ADAEmbedder"
        self.requires_env = ["OPENAI_API_KEY"]
        self.requires_library = ["openai"]
        self.description = "Embeds and retrieves objects using OpenAI's ADA model"

    def embed(
        self,
        documents: list[Document],
        client: WeaviateClient,
        batch_size: int = 100,
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        return self.import_data(documents, client)
