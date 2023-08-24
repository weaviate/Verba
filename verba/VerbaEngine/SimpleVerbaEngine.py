from VerbaEngine.interface import VerbaQueryEngine


class SimpleVerbaQueryEngine(VerbaQueryEngine):
    def change_generative_model(self, generative_model: str):
        class_obj = {"moduleConfig": {"generative-openai": {"model": generative_model}}}
        VerbaQueryEngine.client.schema.update_config("Chunk", class_obj)

    def query(self, query_string: str) -> tuple:
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
