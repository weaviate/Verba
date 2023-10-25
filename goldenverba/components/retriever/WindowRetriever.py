from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.retriever.interface import Retriever

from weaviate.gql.get import HybridFusion

from weaviate import Client


class WindowRetriever(Retriever):
    """
    WindowRetriever that retrieves chunks and their surrounding context depending on the window size
    """

    def __init__(self):
        super().__init__()
        self.description = "WindowRetriever uses Hybrid Search to retrieve relevant chunks and adds their surrounding context"
        self.name = "WindowRetriever"

    def retrieve(
        self,
        queries: list[str],
        client: Client,
        embedder: Embedder,
    ) -> list[Chunk]:
        """Ingest data into Weaviate
        @parameter: queries : list[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns list[Chunk] - List of retrieved chunks
        """
        chunk_class = embedder.get_chunk_class()
        needs_vectorization = embedder.get_need_vectorization()
        chunks = []

        for query in queries:
            query_results = (
                client.query.get(
                    class_name=chunk_class,
                    properties=[
                        "text",
                        "doc_name",
                        "chunk_id",
                        "doc_uuid",
                        "doc_type",
                    ],
                )
                .with_additional(properties=["score"])
                .with_autocut(1)
            )

            if needs_vectorization:
                vector = embedder.vectorize_query(query)
                query_results = query_results.with_hybrid(
                    query=query,
                    vector=vector,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    properties=[
                        "text",
                    ],
                ).do()

            else:
                query_results = query_results.with_hybrid(
                    query=query,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    properties=[
                        "text",
                    ],
                ).do()

            for chunk in query_results["data"]["Get"][chunk_class]:
                chunk_obj = Chunk(
                    chunk["text"],
                    chunk["doc_name"],
                    chunk["doc_type"],
                    chunk["doc_uuid"],
                    chunk["chunk_id"],
                )
                chunk_obj.set_score(chunk["_additional"]["score"])
                chunks.append(chunk_obj)

        sorted_chunks = self.sort_chunks(chunks)

        context = self.combine_context(sorted_chunks, client, embedder)

        return sorted_chunks, context

    def combine_context(
        self,
        chunks: list[Chunk],
        client: Client,
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
                chunk_id = int(chunk)
                all_chunk_range = list(range(chunk_id - window, chunk_id + window + 1))
                for _range in all_chunk_range:
                    if (
                        _range >= 0
                        and _range not in chunk_map
                        and _range not in added_chunks
                    ):
                        chunk_retrieval_results = (
                            client.query.get(
                                class_name=embedder.get_chunk_class(),
                                properties=[
                                    "text",
                                    "doc_name",
                                    "chunk_id",
                                    "doc_uuid",
                                    "doc_type",
                                ],
                            )
                            .with_where(
                                {
                                    "operator": "And",
                                    "operands": [
                                        {
                                            "path": ["chunk_id"],
                                            "operator": "Equal",
                                            "valueNumber": _range,
                                        },
                                        {
                                            "path": ["doc_name"],
                                            "operator": "Equal",
                                            "valueText": chunk_map[chunk].doc_name,
                                        },
                                    ],
                                }
                            )
                            .with_limit(1)
                            .do()
                        )

                        if "data" in chunk_retrieval_results:
                            if chunk_retrieval_results["data"]["Get"][
                                embedder.get_chunk_class()
                            ]:
                                chunk_obj = Chunk(
                                    chunk_retrieval_results["data"]["Get"][
                                        embedder.get_chunk_class()
                                    ][0]["text"],
                                    chunk_retrieval_results["data"]["Get"][
                                        embedder.get_chunk_class()
                                    ][0]["doc_name"],
                                    chunk_retrieval_results["data"]["Get"][
                                        embedder.get_chunk_class()
                                    ][0]["doc_type"],
                                    chunk_retrieval_results["data"]["Get"][
                                        embedder.get_chunk_class()
                                    ][0]["doc_uuid"],
                                    chunk_retrieval_results["data"]["Get"][
                                        embedder.get_chunk_class()
                                    ][0]["chunk_id"],
                                )
                                added_chunks[str(_range)] = chunk_obj

            for chunk in added_chunks:
                if chunk not in doc_name_map[doc]:
                    doc_name_map[doc][chunk] = added_chunks[chunk]

        for doc in doc_name_map:
            sorted_dict = {
                k: doc_name_map[doc][k]
                for k in sorted(doc_name_map[doc], key=lambda x: int(x))
            }

            for chunk in sorted_dict:
                context += sorted_dict[chunk].text

        return context
