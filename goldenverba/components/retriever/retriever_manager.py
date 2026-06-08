"""
retriever_manager.py
====================
Retriever component registry and RetrieverManager.

To add a new Retriever:
  1. Implement it in this directory (goldenverba/components/retriever/)
  2. Import it below and add an instance to the `retrievers` list
"""

from goldenverba.components.interfaces import Retriever
from goldenverba.components.weaviate_manager import WeaviateManager
from goldenverba.components.retriever.WindowRetriever import WindowRetriever

# All available retrievers — add new instances here
retrievers = [WindowRetriever()]


class RetrieverManager:
    """Dispatches retrieve() calls to the correct Retriever implementation."""

    def __init__(self):
        self.retrievers: dict[str, Retriever] = {
            retriever.name: retriever for retriever in retrievers
        }

    async def retrieve(
        self,
        client,
        retriever: str,
        query: str,
        vector: list[float],
        rag_config: dict,
        weaviate_manager: WeaviateManager,
        labels: list[str],
        document_uuids: list[str],
    ):
        try:
            if retriever not in self.retrievers:
                raise Exception(f"Retriever {retriever} not found")

            embedder_model = (
                rag_config["Embedder"]
                .components[rag_config["Embedder"].selected]
                .config["Model"]
                .value
            )
            config = rag_config["Retriever"].components[retriever].config
            documents, context = await self.retrievers[retriever].retrieve(
                client,
                query,
                vector,
                config,
                weaviate_manager,
                embedder_model,
                labels,
                document_uuids,
            )
            return (documents, context)

        except Exception as e:
            raise e
