from goldenverba.retrieval.interface import VerbaQueryEngine

from typing import Optional
import json
from wasabi import msg


class SimpleVerbaQueryEngine(VerbaQueryEngine):
    def query(self, query_string: str, model: str = None) -> tuple:
        """Execute a query to a receive specific chunks from Weaviate
        @parameter query_string : str - Search query
        @returns tuple - (system message, iterable list of results)
        """
        # check semantic cache
        results, system_msg = self.retrieve_semantic_cache(query_string)

        if results:
            return (system_msg, results)

        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Chunk",
                properties=["text", "doc_name", "chunk_id", "doc_uuid", "doc_type"],
            )
            .with_hybrid(query=query_string)
            .with_generate(
                grouped_task=f"You are a chatbot for RAG, answer the query {query_string} based on the given context. Only use information provided in the context. Only if asked or required provide code examples based on the topic at the end of your answer encapsulated with ```programming-language ```"
            )
            .with_additional(properties=["score"])
            .with_limit(8)
            .do()
        )

        if "data" not in query_results:
            raise Exception(query_results)

        results = query_results["data"]["Get"]["Chunk"]

        if results[0]["_additional"]["generate"]["error"]:
            system_msg = results[0]["_additional"]["generate"]["error"]
        else:
            system_msg = results[0]["_additional"]["generate"]["groupedResult"]
            self.add_semantic_cache(query_string, results, system_msg)

        return (system_msg, results)

    def retrieve_document(self, doc_id: str) -> dict:
        """Return a document by it's ID (UUID format) from Weaviate
        @parameter doc_id : str - Document ID
        @returns dict - Document dict
        """
        document = VerbaQueryEngine.client.data_object.get_by_id(
            doc_id,
            class_name="Document",
        )
        return document

    def retrieve_all_documents(self) -> list:
        """Return all documents from Weaviate
        @returns list - Document list
        """
        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Document", properties=["doc_name", "doc_type", "doc_link"]
            )
            .with_additional(properties=["id"])
            .with_limit(1000)
            .do()
        )
        results = query_results["data"]["Get"]["Document"]
        return results

    def search_documents(self, query: str) -> list:
        """Search for documents from Weaviate
        @parameter query_string : str - Search query
        @returns list - Document list
        """
        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Document", properties=["doc_name", "doc_type", "doc_link"]
            )
            .with_bm25(query, properties=["doc_name"])
            .with_additional(properties=["id"])
            .with_limit(20)
            .do()
        )
        results = query_results["data"]["Get"]["Document"]
        return results

    # Custom methods

    def retrieve_semantic_cache(
        self, query: str, dist: float = 0.14
    ) -> Optional[tuple]:
        """Retrieve results from semantic cache based on query and distance threshold
        @parameter query - str - User query
        @parameter dist - float - Distance threshold
        @returns Optional[dict] - List of results or None
        """
        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Cache",
                properties=["query", "results", "system"],
            )
            .with_near_text(content={"concepts": query})
            .with_additional(properties=["distance"])
            .with_limit(1)
            .do()
        )

        results = query_results["data"]["Get"]["Cache"]

        if not results:
            return None, None

        result = results[0]

        if query == result["query"] or result["_additional"]["distance"] <= dist:
            msg.good(f"Retrieved from cache for query {query}")
            return (
                json.loads(result["results"]),
                f"Cached results ({round(float(result['_additional']['distance']),2)}): "
                + result["system"],
            )
        else:
            return None, None

    def add_semantic_cache(self, query: str, results: list[dict], system: str) -> None:
        """Add results to semantic cache
        @parameter query : str - User query
        @parameter results : list[dict] - Results from Weaviate
        @parameter system : str - System message
        @returns None
        """
        with VerbaQueryEngine.client.batch as batch:
            batch.batch_size = 1
            properties = {
                "query": str(query),
                "results": json.dumps(results),
                "system": system,
            }
            msg.good(f"Saved to cache for query {query}")
            VerbaQueryEngine.client.batch.add_data_object(properties, "Cache")

    def get_suggestions(self, query: str) -> list[str]:
        """Retrieve suggestions based on user query
        @parameter query : str - User query
        @returns list[str] - List of possible autocomplete suggestions
        """
        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Suggestion",
                properties=["suggestion"],
            )
            .with_bm25(query=query)
            .with_additional(properties=["score"])
            .with_limit(3)
            .do()
        )

        results = query_results["data"]["Get"]["Suggestion"]

        if not results:
            return []

        suggestions = []

        for result in results:
            if float(result["_additional"]["score"]) > 0.5:
                suggestions.append(result["suggestion"])

        return suggestions
