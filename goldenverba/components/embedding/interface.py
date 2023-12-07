import re
import os
import time
from dotenv import load_dotenv

from tqdm import tqdm
from wasabi import msg
from weaviate import Client

from goldenverba.components.component import VerbaComponent
from goldenverba.components.reader.document import Document
from goldenverba.components.reader.interface import InputForm
from goldenverba.components.schema.schema_generation import (
    EMBEDDINGS,
    VECTORIZERS,
    strip_non_letters,
)

load_dotenv()

class Embedder(VerbaComponent):
    """
    Interface for Verba Embedding.
    """

    def __init__(self):
        super().__init__()
        self.input_form = InputForm.TEXT.value  # Default for all Embedders
        self.vectorizer = ""

    def embed(documents: list[Document], client: Client, batch_size: int = 100) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")

    def import_data(
        self,
        documents: list[Document],
        client: Client,
    ) -> bool:
        """Import verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        try:
            if self.vectorizer not in VECTORIZERS and self.vectorizer not in EMBEDDINGS:
                msg.fail(f"Vectorizer of {self.name} not found")
                return False

            for i, document in enumerate(documents):
                batches = []
                uuid = ""
                temp_batch = []
                token_counter = 0
                for chunk in document.chunks:
                    if token_counter + len(chunk.tokens) <= 4000:
                        token_counter += len(chunk.tokens)
                        temp_batch.append(chunk)
                    else:
                        batches.append(temp_batch.copy())
                        token_counter = len(chunk.tokens)
                        temp_batch = [chunk]
                if len(temp_batch) > 0:
                    batches.append(temp_batch.copy())
                    token_counter = 0
                    temp_batch = []

                msg.info(
                    f"({i+1}/{len(documents)}) Importing document {document.name} with {len(batches)} batches"
                )

                with client.batch as batch:
                    batch.batch_size = 1
                    properties = {
                        "text": str(document.text),
                        "doc_name": str(document.name),
                        "doc_type": str(document.type),
                        "doc_link": str(document.link),
                        "chunk_count": len(document.chunks),
                        "timestamp": str(document.timestamp),
                    }

                    class_name = "Document_" + strip_non_letters(self.vectorizer)
                    uuid = client.batch.add_data_object(properties, class_name)

                    for chunk in document.chunks:
                        chunk.set_uuid(uuid)

                chunk_count = 0
                for _batch_id, chunk_batch in tqdm(
                    enumerate(batches), total=len(batches), desc="Importing batches"
                ):
                    with client.batch as batch:
                        batch.batch_size = len(chunk_batch)
                        for i, chunk in enumerate(chunk_batch):
                            chunk_count += 1

                            properties = {
                                "text": chunk.text,
                                "doc_name": str(document.name),
                                "doc_uuid": chunk.doc_uuid,
                                "doc_type": chunk.doc_type,
                                "chunk_id": chunk.chunk_id,
                            }
                            class_name = "Chunk_" + strip_non_letters(self.vectorizer)

                            # Check if vector already exists
                            if chunk.vector is None:
                                client.batch.add_data_object(properties, class_name)
                            else:
                                client.batch.add_data_object(
                                    properties, class_name, vector=chunk.vector
                                )
                            
                            wait_time_ms = int(os.getenv("WAIT_TIME_BETWEEN_INGESTION_QUERIES_MS","0"))
                            if wait_time_ms>0:
                                time.sleep(float(wait_time_ms)/1000)

                self.check_document_status(
                    client,
                    uuid,
                    document.name,
                    "Document_" + strip_non_letters(self.vectorizer),
                    "Chunk_" + strip_non_letters(self.vectorizer),
                    len(document.chunks),
                )
            return True
        except Exception as e:
            raise Exception(e)

    def check_document_status(
        self,
        client: Client,
        doc_uuid: str,
        doc_name: str,
        doc_class_name: str,
        chunk_class_name: str,
        chunk_count: int,
    ):
        """Verifies that imported documents and its chunks exist in the database, if not, remove everything that was added and rollback
        @parameter: client : Client - Weaviate Client
        @parameter: doc_uuid : str - Document UUID
        @parameter: doc_name : str - Document name
        @parameter: doc_class_name : str - Class name of Document
        @parameter: chunk_class_name : str - Class name of Chunks
        @parameter: chunk_count : int - Number of expected chunks
        @returns Optional[Exception] - Raises Exceptions if imported fail, will be catched by the manager.
        """
        document = client.data_object.get_by_id(
            doc_uuid,
            class_name=doc_class_name,
        )

        if document is not None:
            results = (
                client.query.get(
                    class_name=chunk_class_name,
                    properties=[
                        "doc_name",
                    ],
                )
                .with_where(
                    {
                        "path": ["doc_uuid"],
                        "operator": "Equal",
                        "valueText": doc_uuid,
                    }
                )
                .with_limit(chunk_count + 1)
                .do()
            )

            if len(results["data"]["Get"][chunk_class_name]) != chunk_count:
                # Rollback if fails
                self.remove_document(client, doc_name, doc_class_name, chunk_class_name)
                raise Exception(
                    f"Chunk mismatch for {doc_uuid} {len(results['data']['Get'][chunk_class_name])} != {chunk_count}"
                )
        else:
            raise Exception(f"Document {doc_uuid} not found {document}")

    def remove_document(
        self, client: Client, doc_name: str, doc_class_name: str, chunk_class_name: str
    ) -> None:
        """Deletes documents and its chunks
        @parameter: client : Client - Weaviate Client
        @parameter: doc_name : str - Document name
        @parameter: doc_class_name : str - Class name of Document
        @parameter: chunk_class_name : str - Class name of Chunks.
        """
        client.batch.delete_objects(
            class_name=doc_class_name,
            where={"path": ["doc_name"], "operator": "Equal", "valueText": doc_name},
        )

        client.batch.delete_objects(
            class_name=chunk_class_name,
            where={"path": ["doc_name"], "operator": "Equal", "valueText": doc_name},
        )

        msg.warn(f"Deleted document {doc_name} and its chunks")

    def remove_document_by_id(self, client: Client, doc_id: str):
        doc_class_name = "Document_" + strip_non_letters(self.vectorizer)
        chunk_class_name = "Chunk_" + strip_non_letters(self.vectorizer)

        client.data_object.delete(uuid=doc_id, class_name=doc_class_name)

        client.batch.delete_objects(
            class_name=chunk_class_name,
            where={"path": ["doc_uuid"], "operator": "Equal", "valueText": doc_id},
        )

        msg.warn(f"Deleted document {doc_id} and its chunks")

    def get_document_class(self) -> str:
        return "Document_" + strip_non_letters(self.vectorizer)

    def get_chunk_class(self) -> str:
        return "Chunk_" + strip_non_letters(self.vectorizer)

    def get_cache_class(self) -> str:
        return "Cache_" + strip_non_letters(self.vectorizer)

    def search_documents(self, client: Client, query: str, doc_type: str) -> list:
        """Search for documents from Weaviate
        @parameter query_string : str - Search query
        @returns list - Document list.
        """
        doc_class_name = "Document_" + strip_non_letters(self.vectorizer)

        if doc_type == "" or doc_type is None:
            query_results = (
                client.query.get(
                    class_name=doc_class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_bm25(query, properties=["doc_name"])
                .with_additional(properties=["id"])
                .with_limit(100)
                .do()
            )
        else:
            query_results = (
                client.query.get(
                    class_name=doc_class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_bm25(query, properties=["doc_name"])
                .with_where(
                    {
                        "path": ["doc_type"],
                        "operator": "Equal",
                        "valueText": doc_type,
                    }
                )
                .with_additional(properties=["id"])
                .with_limit(100)
                .do()
            )

        results = query_results["data"]["Get"][doc_class_name]
        return results

    def get_need_vectorization(self) -> bool:
        if self.vectorizer in EMBEDDINGS:
            return True
        return False

    def vectorize_query(self, query: str):
        raise NotImplementedError(
            "vectorize_query method must be implemented by a subclass."
        )

    def conversation_to_query(self, queries: list[str], conversation: dict) -> str:
        query = ""

        if len(conversation) > 1:
            if conversation[-1].type == "system":
                query += conversation[-1].content + " "
            elif conversation[-2].type == "system":
                query += conversation[-2].content + " "

        for _query in queries:
            query += _query + " "

        return query.lower()

    def retrieve_semantic_cache(
        self, client: Client, query: str, dist: float = 0.04
    ) -> str:
        """Retrieve results from semantic cache based on query and distance threshold
        @parameter query - str - User query
        @parameter dist - float - Distance threshold
        @returns Optional[dict] - List of results or None.
        """
        needs_vectorization = self.get_need_vectorization()

        match_results = (
            client.query.get(
                class_name=self.get_cache_class(),
                properties=["query", "system"],
            )
            .with_where(
                {
                    "path": ["query"],
                    "operator": "Equal",
                    "valueText": query,
                }
            )
            .with_limit(1)
        ).do()

        if "data" in match_results and len(match_results["data"]["Get"][self.get_cache_class()]) > 0 and (
            query
            == match_results["data"]["Get"][self.get_cache_class()][0]["query"]
        ):
            msg.good("Direct match from cache")
            return (
                match_results["data"]["Get"][self.get_cache_class()][0][
                    "system"
                ],
                0.0,
            )

        query_results = (
            client.query.get(
                class_name=self.get_cache_class(),
                properties=["query", "system"],
            )
            .with_additional(properties=["distance"])
            .with_limit(1)
        )

        if needs_vectorization:
            vector = self.vectorize_query(query)
            query_results = query_results.with_near_vector(
                content={"vector": vector},
            ).do()

        else:
            query_results = query_results.with_near_text(
                content={"concepts": [query]},
            ).do()

        if "data" not in query_results:
            msg.warn(query_results)
            return None, None

        results = query_results["data"]["Get"][self.get_cache_class()]

        if not results:
            return None, None

        result = results[0]

        if float(result["_additional"]["distance"]) <= dist:
            msg.good("Retrieved similar from cache")
            return result["system"], float(result["_additional"]["distance"])

        else:
            return None, None

    def add_to_semantic_cache(self, client: Client, query: str, system: str):
        """Add results to semantic cache
        @parameter query : str - User query
        @parameter results : list[dict] - Results from Weaviate
        @parameter system : str - System message
        @returns None.
        """
        needs_vectorization = self.get_need_vectorization()

        with client.batch as batch:
            batch.batch_size = 1
            properties = {
                "query": str(query),
                "system": system,
            }
            msg.good("Saved to cache")

            if needs_vectorization:
                vector = self.vectorize_query(query)
                client.batch.add_data_object(
                    properties, self.get_cache_class(), vector=vector
                )
            else:
                client.batch.add_data_object(properties, self.get_cache_class())
