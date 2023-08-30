from verba_rag.retrieval.simple_engine import SimpleVerbaQueryEngine

import os
from wasabi import msg
import openai


class AdvancedVerbaQueryEngine(SimpleVerbaQueryEngine):
    def query(self, query_string: str, model: str) -> tuple:
        """Execute a query to a receive specific chunks from Weaviate
        @parameter query_string : str - Search query
        @returns tuple - (system message, iterable list of results)
        """

        msg.info(f"Using model: {model}")

        # check semantic cache
        results, system_msg = self.retrieve_semantic_cache(query_string)

        if results:
            return (system_msg, results)

        query_results = (
            SimpleVerbaQueryEngine.client.query.get(
                class_name="Chunk",
                properties=["text", "doc_name", "chunk_id", "doc_uuid", "doc_type"],
            )
            .with_hybrid(query=query_string)
            .with_additional(properties=["score"])
            .with_limit(6)
            .do()
        )

        results = query_results["data"]["Get"]["Chunk"]
        msg.info(f"Retrieved {len(results)} chunks for {query_string}")
        if "data" not in query_results:
            raise Exception(query_results)

        context = self.combine_context(results=results)

        msg.info(
            f"Combined context of all chunks and their weighted windows ({len(context)} characters)"
        )

        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        try:
            msg.info(f"Starting API call to answer {query_string}")
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a Retrieval Augmented Generation chatbot. Try to answer this user query {query_string} with only the provided context. If the provided documentation does not provide enough information, say so. If the answer requires code examples encapsulate them with ```programming-language-name ```. Don't do pseudo-code.",
                    },
                    {"role": "user", "content": context},
                ],
            )
            system_msg = str(completion["choices"][0]["message"]["content"])
            self.add_semantic_cache(query_string, results, system_msg)
        except Exception as e:
            system_msg = f"Something went wrong! {str(e)} {str(completion)}"
            msg.fail(system_msg)

        return (system_msg, results)

    def combine_context(self, results: list) -> str:
        doc_name_map = {}

        context = ""

        for result in results:
            if result["doc_name"] not in doc_name_map:
                doc_name_map[result["doc_name"]] = {}

            doc_name_map[result["doc_name"]][result["chunk_id"]] = result

        for doc in doc_name_map:
            chunk_map = doc_name_map[doc]
            window = len(chunk_map)
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
                            SimpleVerbaQueryEngine.client.query.get(
                                class_name="Chunk",
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
                                            "valueText": str(doc),
                                        },
                                    ],
                                }
                            )
                            .with_limit(1)
                            .do()
                        )

                        if "data" in chunk_retrieval_results:
                            if chunk_retrieval_results["data"]["Get"]["Chunk"]:
                                added_chunks[str(_range)] = chunk_retrieval_results[
                                    "data"
                                ]["Get"]["Chunk"][0]

            for chunk in added_chunks:
                if chunk not in doc_name_map[doc]:
                    doc_name_map[doc][chunk] = added_chunks[chunk]

        for doc in doc_name_map:
            sorted_dict = {
                k: doc_name_map[doc][k]
                for k in sorted(doc_name_map[doc], key=lambda x: int(x))
            }
            for chunk in sorted_dict:
                context += sorted_dict[chunk]["text"]

        return context
