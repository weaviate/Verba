from goldenverba.components.interfaces import Retriever
from goldenverba.components.types import InputConfig


class WindowRetriever(Retriever):
    """
    WindowRetriever that retrieves chunks and their surrounding context depending on the window size.
    """

    def __init__(self):
        super().__init__()
        self.description = "Retrieve relevant chunks from Weaviate"
        self.name = "Advanced"

        self.config["Search Mode"] = InputConfig(
            type="dropdown",
            value="Hybrid Search",
            description="Switch between search types.",
            values=["Hybrid Search"],
        )
        self.config["Limit Mode"] = InputConfig(
            type="dropdown",
            value="Autocut",
            description="Method for limiting the results. Autocut decides automatically how many chunks to retrieve, while fixed sets a fixed limit.",
            values=["Autocut", "Fixed"],
        )
        self.config["Limit/Sensitivity"] = InputConfig(
            type="number",
            value=1,
            description="Value for limiting the results. Value controls Autocut sensitivity and Fixed Size",
            values=[],
        )
        self.config["Chunk Window"] = InputConfig(
            type="number",
            value=1,
            description="Number of surrounding chunks of retrieved chunks to add to context",
            values=[],
        )
        self.config["Threshold"] = InputConfig(
            type="number",
            value=80,
            description="Threshold of chunk score to apply window technique (1-100)",
            values=[],
        )

    async def retrieve(
        self,
        client,
        query,
        vector,
        config,
        weaviate_manager,
        embedder,
        labels,
        document_uuids,
    ):

        search_mode = config["Search Mode"].value
        limit_mode = config["Limit Mode"].value
        limit = int(config["Limit/Sensitivity"].value)

        window = max(0, min(10, int(config["Chunk Window"].value)))
        window_threshold = max(0, min(100, int(config["Threshold"].value)))
        window_threshold /= 100

        if search_mode == "Hybrid Search":
            chunks = await weaviate_manager.hybrid_chunks(
                client,
                embedder,
                query,
                vector,
                limit_mode,
                limit,
                labels,
                document_uuids,
            )
        # TODO Add other search methods

        if len(chunks) == 0:
            return ([], "We couldn't find any chunks to the query")

        # Group Chunks by document and sum score
        doc_map = {}
        scores = [0]
        for chunk in chunks:
            if chunk.properties["doc_uuid"] not in doc_map:
                document = await weaviate_manager.get_document(
                    client, chunk.properties["doc_uuid"]
                )
                if document is None:
                    continue
                doc_map[chunk.properties["doc_uuid"]] = {
                    "title": document["title"],
                    "chunks": [],
                    "score": 0,
                    "metadata": document["metadata"],
                }
            doc_map[chunk.properties["doc_uuid"]]["chunks"].append(
                {
                    "uuid": str(chunk.uuid),
                    "score": chunk.metadata.score,
                    "chunk_id": chunk.properties["chunk_id"],
                    "content": chunk.properties["content"],
                }
            )
            doc_map[chunk.properties["doc_uuid"]]["score"] += chunk.metadata.score
            scores.append(chunk.metadata.score)
        min_score = min(scores)
        max_score = max(scores)

        def normalize_value(value, max_value, min_value):
            return (value - min_value) / (max_value - min_value)

        def generate_window_list(value, window):

            value = int(value)
            window = int(window)
            # Create a range of values around the given value, excluding the original value
            return [i for i in range(value - window, value + window + 1) if i != value]

        documents = []
        context_documents = []
        for doc in doc_map:
            additional_chunk_ids = []
            for chunk in doc_map[doc]["chunks"]:
                if window_threshold <= normalize_value(
                    float(chunk["score"]), float(max_score), float(min_score)
                ):
                    additional_chunk_ids += generate_window_list(
                        chunk["chunk_id"], window
                    )
            unique_chunk_ids = set(additional_chunk_ids)

            if len(unique_chunk_ids) > 0:
                additional_chunks = await weaviate_manager.get_chunk_by_ids(
                    client, embedder, doc, unique_chunk_ids
                )
                existing_chunk_ids = set(
                    chunk["chunk_id"] for chunk in doc_map[doc]["chunks"]
                )
                for chunk in additional_chunks:
                    if chunk.properties["chunk_id"] not in existing_chunk_ids:
                        doc_map[doc]["chunks"].append(
                            {
                                "uuid": str(chunk.uuid),
                                "score": 0,
                                "chunk_id": chunk.properties["chunk_id"],
                                "content": chunk.properties["content"],
                            }
                        )
                        existing_chunk_ids.add(chunk.properties["chunk_id"])

            _chunks = [
                {
                    "uuid": str(chunk["uuid"]),
                    "score": chunk["score"],
                    "chunk_id": chunk["chunk_id"],
                    "embedder": embedder,
                }
                for chunk in doc_map[doc]["chunks"]
            ]
            context_chunks = [
                {
                    "uuid": str(chunk["uuid"]),
                    "score": chunk["score"],
                    "content": chunk["content"],
                    "chunk_id": chunk["chunk_id"],
                    "embedder": embedder,
                }
                for chunk in doc_map[doc]["chunks"]
            ]
            _chunks_sorted = sorted(_chunks, key=lambda x: x["chunk_id"])
            context_chunks_sorted = sorted(context_chunks, key=lambda x: x["chunk_id"])

            documents.append(
                {
                    "title": doc_map[doc]["title"],
                    "chunks": _chunks_sorted,
                    "score": doc_map[doc]["score"],
                    "metadata": doc_map[doc]["metadata"],
                    "uuid": str(doc),
                }
            )

            context_documents.append(
                {
                    "title": doc_map[doc]["title"],
                    "chunks": context_chunks_sorted,
                    "score": doc_map[doc]["score"],
                    "uuid": str(doc),
                    "metadata": doc_map[doc]["metadata"],
                }
            )

        sorted_context_documents = sorted(
            context_documents, key=lambda x: x["score"], reverse=True
        )
        sorted_documents = sorted(documents, key=lambda x: x["score"], reverse=True)

        context = self.combine_context(sorted_context_documents)

        return (sorted_documents, context)

    def combine_context(self, documents: list[dict]) -> str:

        context = ""

        for document in documents:
            context += f"Document Title: {document['title']}\n"
            if len(document["metadata"]) > 0:
                context += f"Document Metadata: {document['metadata']}\n"
            for chunk in document["chunks"]:
                context += f"Chunk: {int(chunk['chunk_id'])+1}\n"
                if chunk["score"] > 0:
                    context += f"High Relevancy: {chunk['score']:.2f}\n"
                context += f"{chunk['content']}\n"
            context += "\n\n"

        return context
