from weaviate import WeaviateClient
from weaviate.collections.classes.grpc import HybridFusion
from verba_types import DocumentType, ChunkType
from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.retriever.interface import Retriever


class SimpleRetriever(Retriever):
    """
    SimpleRetriver that retrieves chunks through hybrid search, no reranking or additional logic.
    """

    def __init__(self):
        super().__init__()
        self.description = "SimpleRetriever uses Hybrid Search to retrieve relevant chunks to the user's query"
        self.name = "SimpleRetriever"

    def retrieve(
        self,
        queries: list[str],
        client: WeaviateClient,
        embedder: Embedder,
    ) -> tuple[list[Chunk], str]:
        """Ingest data into Weaviate
        @parameter: queries : list[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns list[Chunk] - List of retrieved chunks.
        """
        chunk_class = embedder.get_chunk_class()
        chunk_class = client.collections.get(chunk_class)
        needs_vectorization = embedder.get_need_vectorization()
        chunks = []

        for query in queries:

            if needs_vectorization:
                vector = embedder.vectorize_query(query)
                query_results = chunk_class.query.hybrid(
                    query=query,
                    vector=vector,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    return_properties=ChunkType,
                    target_vector=embedder.vectorizer.name,
                )

            else:

                query_results = chunk_class.query.hybrid(
                    query=query,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    return_properties=ChunkType,
                    target_vector=embedder.vectorizer.name,
                )

            for chunk in query_results.objects:

                chunk_obj = Chunk(
                    text=chunk.properties.get("text"),
                    doc_name=chunk.properties.get("doc_name"),
                    doc_type=chunk.properties.get("doc_type"),
                    doc_uuid=chunk.properties.get("doc_uuid"),
                    chunk_id=str(chunk.properties.get("chunk_id")),
                )
                chunk_obj.set_score(chunk.metadata.score)
                chunks.append(chunk_obj)

        sorted_chunks = self.sort_chunks(chunks)

        context = ""
        for chunk in sorted_chunks:
            context += chunk.text + " "

        return sorted_chunks, context
