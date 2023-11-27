from wasabi import msg
from weaviate import Client

from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.generation.interface import Generator
from goldenverba.components.retriever.interface import Retriever
from goldenverba.components.retriever.SimpleRetriever import SimpleRetriever
from goldenverba.components.retriever.WindowRetriever import WindowRetriever


class RetrieverManager:
    def __init__(self):
        self.retrievers: dict[str, Retriever] = {
            "WindowRetriever": WindowRetriever(),
            "SimpleRetriever": SimpleRetriever(),
        }
        self.selected_retriever: Retriever = self.retrievers["WindowRetriever"]

    def retrieve(
        self,
        queries: list[str],
        client: Client,
        embedder: Embedder,
        generator: Generator,
    ) -> list[Chunk]:
        """Ingest data into Weaviate
        @parameter: queries : list[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns list[Chunk] - List of retrieved chunks.
        """
        chunks, context = self.selected_retriever.retrieve(queries, client, embedder)
        managed_context = self.selected_retriever.cutoff_text(
            context, generator.context_window
        )
        return chunks, managed_context

    def set_retriever(self, retriever: str) -> bool:
        if retriever in self.retrievers:
            self.selected_retriever = self.retrievers[retriever]
            return True
        else:
            msg.warn(f"Retriever {retriever} not found")
            return False

    def get_retrievers(self) -> dict[str, Retriever]:
        return self.retrievers
