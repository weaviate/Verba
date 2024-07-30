from weaviate import Client
from weaviate.gql.get import HybridFusion
from wasabi import msg

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Embedder, Retriever
from goldenverba.components.types import InputConfig


class WindowRetriever(Retriever):
    """
    WindowRetriever that retrieves chunks and their surrounding context depending on the window size.
    """

    def __init__(self):
        super().__init__()
        self.description = "Retrieve relevant chunks from Weaviate"
        self.name = "Advanced"

        self.config = {
                    "Search Mode": InputConfig(
                        type="dropdown", value="Hybrid Search", description="Switch between search types.", values=["Hybrid Search","Vector Search", "Keyword Search (BM25)"]
                    ),
                    "Limit Mode": InputConfig(
                        type="dropdown", value="Autocut", description="Method for limiting the results. Autocut decides automatically how many chunks to retrieve, while fixed sets a fixed limit.", values=["Autocut", "Fixed"]
                    ),
                    "Limit": InputConfig(
                        type="number", value=1, description="Value for limiting the results. Value controls Autocut sensitivity and Fixed Size", values=[]
                    ),
                    "Window": InputConfig(
                        type="number", value=1, description="Number of surrounding chunks of retrieved chunks to add to context", values=[]
                    ),
                    "Threshold": InputConfig(
                        type="number", value=80, description="Threshold of chunk score to apply window technique (1-100)", values=[]
                    )
                }

    async def retrieve(
        self,
        query, vector, config, weaviate_manager, embedder
    ):
       
        search_mode = config["Search Mode"].value
        limit_mode = config["Limit Mode"].value
        limit = int(config["Limit"].value)

        window = max(0,min(10, int(config["Window"].value)))
        window_threshold = max(0,min(100, int(config["Threshold"].value)))
        window_threshold /= 100

        if search_mode == "Hybrid Search":
            chunks = await weaviate_manager.hybrid_chunks(embedder, query, vector, limit_mode, limit)
        # TODO Add other search methods
            
        # Group Chunks by document and sum score
        doc_map = {}
        scores = []
        for chunk in chunks:
            if chunk.properties["doc_uuid"] not in doc_map:
                document = await weaviate_manager.get_document(chunk.properties["doc_uuid"])
                doc_map[chunk.properties["doc_uuid"]] = {"title":document["title"], "chunks": [], "score": 0}
            doc_map[chunk.properties["doc_uuid"]]["chunks"].append({"uuid":str(chunk.uuid), "score":chunk.metadata.score, "chunk_id":chunk.properties["chunk_id"], "content":chunk.properties["content"]})
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
        for doc in doc_map:
            additional_chunk_ids = []
            for chunk in doc_map[doc]["chunks"]:
                if window_threshold <= normalize_value(float(chunk["score"]),float(max_score),float(min_score)):
                    additional_chunk_ids += generate_window_list(chunk["chunk_id"], window)
            unique_chunk_ids = set(additional_chunk_ids)

            if len(unique_chunk_ids) > 0:
                additional_chunks = await weaviate_manager.get_chunk_by_ids(embedder, doc, unique_chunk_ids)
                for chunk in additional_chunks:
                    doc_map[doc]["chunks"].append({"uuid":str(chunk.uuid), "score":0, "chunk_id":chunk.properties["chunk_id"], "content":chunk.properties["content"]})

            _chunks = [{"uuid":str(chunk["uuid"]), "score":chunk["score"], "chunk_id":chunk["chunk_id"]} for chunk in doc_map[doc]["chunks"]]
            _chunks_sorted = sorted(_chunks, key=lambda x: x["chunk_id"])

            documents.append({"title":doc_map[doc]["title"], "chunks":_chunks_sorted, "score":doc_map[doc]["score"], "uuid":str(doc)})
        # TODO Context Generation
                    
        sorted_documents = sorted(documents, key=lambda x: x["score"], reverse=True)
        print(sorted_documents)


        return (sorted_documents, "Placeholder Context")

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
                doc_name_map[chunk.doc_name] = {"score": 0, "chunks":{}}

            doc_name_map[chunk.doc_name]["chunks"][chunk.chunk_id] = chunk
            doc_name_map[chunk.doc_name]["score"] += float(chunk.score)

        doc_name_map = dict(sorted(doc_name_map.items(), key=lambda item: item[1]['score'], reverse=True))

        for doc in doc_name_map:
            chunk_map = doc_name_map[doc]["chunks"]
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
                    doc_name_map[doc]["chunks"][chunk] = added_chunks[chunk]

        for doc in doc_name_map:
            sorted_dict = {
                k: doc_name_map[doc]["chunks"][k]
                for k in sorted(doc_name_map[doc]["chunks"], key=lambda x: int(x))
            }

            context += "--- Document " + doc + " ---" + "\n\n"

            for chunk in sorted_dict:
                context += "Chunk "+ str(sorted_dict[chunk].chunk_id) + "\n\n" + sorted_dict[chunk].text + "\n\n"

        return context
