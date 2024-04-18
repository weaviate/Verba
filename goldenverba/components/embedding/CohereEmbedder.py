from weaviate import Client

from verba_types import VectorizerType, EmbeddingType
from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.reader.document import Document

import weaviate.classes.config as wvc


class CohereEmbedder(Embedder):
    """
    CohereEmbedder for Verba.
    """

    def __init__(self):
        super().__init__(
            vectorizer=VectorizerType(
                name="text2veccohere",
                config_class=wvc.Configure.NamedVectors.text2vec_cohere,
            )
        )
        self.name = "CohereEmbedder"
        self.requires_env = ["COHERE_API_KEY"]
        self.description = (
            "Embeds and retrieves objects using Cohere's embed-multilingual-v2.0 model"
        )
        self.vectorizer = "text2vec-cohere"

    def embed(
        self,
        documents: list[Document],
        client: Client,
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        return self.import_data(documents, client)
