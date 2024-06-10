import asyncio
import numpy as np

from tqdm import tqdm
from weaviate import Client

from goldenverba.components.interfaces import Embedder
from goldenverba.components.document import Document

try:
    from infinity_emb import EngineArgs
    from infinity_emb.engine import AsyncEngineArray
    from infinity_emb.env import MANAGER
    INFINITY_IMPORTED = True
except:
    INFINITY_IMPORTED = False


class InfinityEmbedder(Embedder):
    def __init__(
            self,
    ):
        super().__init__()
        self.name = "InfinityEmbedder"
        self.requires_library = ["torch", "transformers", "infinity_emb"]
        self.requires_env = ["INFINITY_MODEL_ID"]
        self.description = "Embeds and retrieves objects using Infinity and SentenceTransformer"
        self.vectorizer = "InfinityEmbedder"

        if not INFINITY_IMPORTED:
            raise ImportError("The Infinity library is not installed. Please install it using `pip install infinity-emb>=0.0.40`")
        
        # set via INFINITY_MODEL_ID, which is a `;` separated list of model names from huggingface/hub
        self.engine_array = AsyncEngineArray.from_args([EngineArgs(model_name_or_path = model_name) for model_name in MANAGER.model_id])  

    async def _async_embed(self, sentences: list[str], model_name: str = "") -> list[np.ndarray]:
        """queue the embeddings and usage of the sentences in the engine"""
        if not model_name:
            model_name = self._default_model
        engine = self.engine_array[model_name]
        was_already_running = engine.is_running
        if not was_already_running:
            await engine.astart()
        embeddings, _ = await engine.embed(sentences=sentences)
        if not was_already_running:
            await engine.astop()
        return embeddings

    def _embed(self, sentences: list[str], model_name: str = ""):
        """runs asyncio.run() on the async version of the function"""
        return asyncio.run(self._async_embed(sentences, model_name))
    
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
        all_vectors = iter(self._embed( [chunk.text for document in documents for chunk in document.chunks]))
        for document in documents:
            for chunk in document.chunks:
                chunk.set_vector(next(all_vectors))
        return self.import_data(documents, client, logging)

    def vectorize_chunk(self, chunk) -> list[float]:
        return self._embed([chunk])[0]

    def vectorize_query(self, query: str) -> list[float]:
        return self.vectorize_chunk(query)