from VerbaEngine.interface import VerbaQueryEngine


class SimpleVerbaQueryEngine(VerbaQueryEngine):
    def query(self, query_string: str) -> list:
        results = (
            VerbaQueryEngine.client.query.get(
                class_name="Chunk",
                properties=["text", "doc_name", "chunk_id", "doc_uuid"],
            )
            .with_near_text(content={"concepts": [query_string]})
            .with_generate(
                grouped_task=f"Can you answer the query {query_string} with the given snippets of documentation? If yes, answer the query, if no then say the data is not sufficient, only use knowledge and context provided"
            )
            .with_limit(10)
            .do()
        )

        if "data" not in results:
            raise Exception(results)

        return results["data"]["Get"]["Chunk"]

    def retrieve_document(self, doc_id: str) -> dict:
        document = VerbaQueryEngine.client.data_object.get_by_id(
            doc_id,
            class_name="Document",
        )

        return document
