from tqdm import tqdm
from wasabi import msg
from weaviate import Client

from goldenverba.components.interfaces import Embedder
from goldenverba.components.document import Document


class SentenceTransformersEmbedder(Embedder):
    """
    SentenceTransformersEmbedder base class for Verba.
    """

    def __init__(self, vectorizer: str):
        super().__init__()
        self.vectorizer = vectorizer
        self.name = self.__class__.__name__
        self.description = f"Embeds and retrieves objects using SentenceTransformer with the {self.vectorizer} model"
        self.requires_library = ["sentence-transformers"]
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.vectorizer)
        except Exception as e:
            pass

    def embed(
        self,
        documents: list[Document],
        client: Client,
        logging: list[dict],
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        # TODO: Call model.encode with a list of chunks instead of a single chunk for faster inference
        for document in tqdm(
            documents, total=len(documents), desc="Vectorizing document chunks"
        ):
            for chunk in document.chunks:
                chunk.set_vector(self.vectorize_chunk(chunk.text))

        return self.import_data(documents, client, logging)

    def vectorize_chunk(self, chunk) -> list[float]:
        return self.model.encode(chunk).tolist()

    def vectorize_query(self, query: str) -> list[float]:
        return self.vectorize_chunk(query)
