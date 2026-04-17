import asyncio

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SentenceTransformersEmbedder(Embedding):
    """
    SentenceTransformersEmbedder base class for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "SentenceTransformers"
        self.requires_library = ["sentence_transformers"]
        self.description = "Embeds and retrieves objects using SentenceTransformer"
        self.config = {
            "Model": InputConfig(
                type="dropdown",
                value="all-MiniLM-L6-v2",
                description="Select an HuggingFace Embedding Model",
                values=[
                    "all-MiniLM-L6-v2",
                    "mixedbread-ai/mxbai-embed-large-v1",
                    "all-mpnet-base-v2",
                    "BAAI/bge-m3",
                    "all-MiniLM-L12-v2",
                    "paraphrase-MiniLM-L6-v2",
                ],
            ),
        }
        # Cache loaded models by name to avoid reloading from disk on every call
        self._model_cache: dict = {}

    def _get_model(self, model_name: str):
        if SentenceTransformer is None:
            raise ImportError(
                "sentence_transformers is not installed. "
                "Install it with: pip install goldenverba[huggingface]"
            )
        if model_name not in self._model_cache:
            self._model_cache[model_name] = SentenceTransformer(model_name)
        return self._model_cache[model_name]

    async def vectorize(self, config: dict, content: list[str]) -> list[list[float]]:
        try:
            model_name = config.get("Model").value
            model = self._get_model(model_name)
            # model.encode() is synchronous and CPU-bound — run in thread pool
            # to avoid blocking the async event loop
            embeddings = await asyncio.to_thread(model.encode, content)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Failed to vectorize chunks: {str(e)}")
