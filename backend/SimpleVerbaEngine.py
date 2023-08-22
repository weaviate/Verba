from VerbaEngine.interface import VerbaQueryEngine


class SimpleVerbaQueryEngine(VerbaQueryEngine):
    def change_generative_model(self, generative_model: str):
        class_obj = {"moduleConfig": {"generative-openai": {"model": generative_model}}}
        VerbaQueryEngine.client.schema.update_config("Chunk", class_obj)

    def query(self, query_string: str) -> tuple:
        """Execute a query to a receive specific chunks from Weaviate
        @parameter query_string : str - Search query
        @returns tuple - (system message, iterable list of results)
        """
        query_results = (
            VerbaQueryEngine.client.query.get(
                class_name="Chunk",
                properties=["text", "doc_name", "chunk_id", "doc_uuid"],
            )
            .with_hybrid(query=query_string)
            .with_generate(
                grouped_task=f"You are a chatbot for Weaviate, a vector database, answer the query {query_string} with the given snippets of documentation in 2-3 sentences and if needed give code examples at the end of the answer encapsulated with ```programming-language ```"
            )
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
        """Return a document by it's ID (UUID format) from Weaviate
        @parameter doc_id : str - Document ID
        @returns dict - Document dict
        """
        document = VerbaQueryEngine.client.data_object.get_by_id(
            doc_id,
            class_name="Document",
        )

        return document
