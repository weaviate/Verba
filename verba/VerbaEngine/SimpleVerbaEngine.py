from VerbaEngine.interface import VerbaQueryEngine

from typing import Optional
import json
from wasabi import msg


class SimpleVerbaQueryEngine(VerbaQueryEngine):
    def change_generative_model(self, generative_model: str):
        class_obj = {"moduleConfig": {"generative-openai": {"model": generative_model}}}
        VerbaQueryEngine.client.schema.update_config("Chunk", class_obj)

    def query(self, query_string: str) -> tuple:
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
                grouped_task=f"You are a chatbot for Weaviate, a vector database, answer the query {query_string} with the given snippets of documentation in 2-3 sentences and if needed give code examples at the end of the answer encapsulated with ```programming-language ```"
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
        document = VerbaQueryEngine.client.data_object.get_by_id(
            doc_id,
            class_name="Document",
        )
        return document

    def retrieve_all_documents(self) -> list:
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

    def retrieve_semantic_cache(self, query: str) -> Optional[dict]:
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

        if query == result["query"] or result["_additional"]["distance"] <= 0.14:
            msg.good(f"Retrieved from cache for query {query}")
            return (
                json.loads(result["results"]),
                f"Cached ({round(float(result['_additional']['distance']),2)}) "
                + result["system"],
            )
        else:
            return None, None

    def add_semantic_cache(self, query: str, results: list[dict], system: str) -> None:
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
        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Suggestion",
                properties=["suggestion"],
            )
            .with_bm25(query=query)
            .with_limit(3)
            .do()
        )

        results = query_results["data"]["Get"]["Suggestion"]

        if not results:
            return []

        suggestions = [result["suggestion"] for result in results]

        return suggestions
