from weaviate import WeaviateClient
from weaviate.collections.classes.grpc import HybridFusion

from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.retriever.interface import Retriever

from weaviate.classes.query import Filter
from verba_types import ChunkType


class WindowRetriever(Retriever):
    """
    WindowRetriever that retrieves chunks and their surrounding context depending on the window size.
    """

    def __init__(self):
        super().__init__()
        self.description = "WindowRetriever uses Hybrid Search to retrieve relevant chunks and adds their surrounding context"
        self.name = "WindowRetriever"

    def retrieve(
        self,
        queries: list[str],
        client: WeaviateClient,
        embedder: Embedder,
    ) -> list[Chunk]:
        """Ingest data into Weaviate
        @parameter: queries : list[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns list[Chunk] - List of retrieved chunks.
        """
        chunk_class = client.collections.get(embedder.get_chunk_class())
        needs_vectorization = embedder.get_need_vectorization()
        chunks = []

        for query in queries:
            query_results = []

            if needs_vectorization:
                vector = embedder.vectorize_query(query)

                query_results = chunk_class.query.hybrid(
                    query=query,
                    return_properties=ChunkType,
                    target_vector=embedder.vectorizer.name,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    vector=vector,
                )

            else:
                query_results = chunk_class.query.hybrid(
                    query=query,
                    return_properties=ChunkType,
                    target_vector=embedder.vectorizer.name,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                )

            for chunk in query_results.objects:
                chunk_obj = Chunk(
                    chunk.properties.get("text"),
                    chunk.properties.get("doc_name"),
                    chunk.properties.get("doc_type"),
                    chunk.properties.get("doc_uuid"),
                    str(chunk.properties.get("chunk_id")),
                )
                chunk_obj.set_score(chunk.metadata.score)
                chunks.append(chunk_obj)

        sorted_chunks = self.sort_chunks(chunks)

        context = self.combine_context(sorted_chunks, client, embedder)

        return sorted_chunks, context

    def combine_context(
        self,
        chunks: list[Chunk],
        client: WeaviateClient,
        embedder: Embedder,
    ) -> str:
        doc_name_map = {}

        context = ""

        for chunk in chunks:
            if chunk.doc_name not in doc_name_map:
                doc_name_map[chunk.doc_name] = {}

            doc_name_map[chunk.doc_name][chunk.chunk_id] = chunk

        for doc in doc_name_map:
            chunk_map = doc_name_map[doc]
            window = 2
            added_chunks = {}
            for chunk in chunk_map:
                chunk_id = int(float(chunk))
                all_chunk_range = list(range(chunk_id - window, chunk_id + window + 1))
                for _range in all_chunk_range:
                    if (
                        _range >= 0
                        and _range not in chunk_map
                        and _range not in added_chunks
                    ):
                        class_name = client.collections.get(embedder.get_chunk_class())
                        chunk_retrieval_results = class_name.query.fetch_objects(
                            return_properties=ChunkType,
                            limit=1,
                            filters=Filter.by_property("chunk_id").equal(_range)
                            & Filter.by_property("doc_name").equal(
                                chunk_map[chunk].doc_name
                            ),
                        )

                        if len(chunk_retrieval_results.objects) > 0:
                            chk = chunk_retrieval_results.objects[0].properties
                            chunk_obj = Chunk(
                                chk.get("text"),
                                chk.get("doc_name"),
                                chk.get("doc_type"),
                                chk.get("doc_uuid"),
                                str(chk.get("chunk_id")),
                            )

                            added_chunks[str(_range)] = chunk_obj

            for chunk in added_chunks:
                if chunk not in doc_name_map[doc]:
                    doc_name_map[doc][chunk] = added_chunks[chunk]

        for doc in doc_name_map:
            sorted_dict = {
                k: doc_name_map[doc][k]
                for k in sorted(doc_name_map[doc], key=lambda x: int(float(x)))
            }

            for chunk in sorted_dict:
                context += sorted_dict[chunk].text

        return context
