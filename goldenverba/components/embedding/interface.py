import re
import os
import time
from dotenv import load_dotenv

from tqdm import tqdm
from wasabi import msg
from weaviate import WeaviateClient
from weaviate.classes.query import Filter
from weaviate.types import UUID
from verba_types import DocumentType, SuggestionType, VectorizerOrEmbeddingType
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

    def __init__(self, vectorizer: VectorizerOrEmbeddingType):
        super().__init__()
        self.input_form = InputForm.TEXT.value  # Default for all Embedders
        self.vectorizer = vectorizer

    def embed(
        self, documents: list[Document], client: WeaviateClient, batch_size: int = 100
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        raise NotImplementedError("embed method must be implemented by a subclass.")

    def check_valid_vectorizer(self) -> bool:
        """Checks if the vectorizer is available in the Weaviate instance
        @parameter client : WeaviateClient - Weaviate Client
        @returns bool - Bool whether the vectorizer is available.
        """
        # TODO: consider class
        if self.vectorizer.name not in [
            vectorizer.name for vectorizer in VECTORIZERS
        ] and self.vectorizer.name not in [embedding.name for embedding in EMBEDDINGS]:
            return False
        return True

    def import_data(
        self,
        documents: list[Document],
        client: WeaviateClient,
    ) -> bool:
        """Import verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        # TODO: target vector
        try:
            if not self.check_valid_vectorizer():
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

                doc_class = client.collections.get(self.get_document_class())

                uuid = doc_class.data.insert(
                    properties={
                        "doc_name": str(document.name),
                        "doc_type": str(document.type),
                        "doc_link": str(document.link),
                        "chunk_count": len(document.chunks),
                    }
                )

                for chunk in document.chunks:
                    chunk.set_uuid(uuid)

                chunk_count = 0
                for _batch_id, chunk_batch in tqdm(
                    enumerate(batches), total=len(batches), desc="Importing batches"
                ):
                    with client.batch.fixed_size(len(chunk_batch)) as batch:
                        for i, chunk in enumerate(chunk_batch):
                            chunk_count += 1

                            properties = {
                                "text": chunk.text,
                                "doc_name": str(document.name),
                                "doc_uuid": chunk.doc_uuid,
                                "doc_type": chunk.doc_type,
                                "chunk_id": chunk.chunk_id,
                            }
                            class_name = "Chunk"

                            # Check if vector already exists
                            # Target vector: check how to specify target vector (but not vector itself)
                            if chunk.vector is None:
                                batch.add_object(
                                    collection=class_name,
                                    properties=properties,
                                )
                            else:
                                batch.add_object(
                                    collection=class_name,
                                    properties=properties,
                                    vector={
                                        self.vectorizer.name: chunk.vector,
                                    },
                                )

                            wait_time_ms = int(
                                os.getenv("WAIT_TIME_BETWEEN_INGESTION_QUERIES_MS", "0")
                            )
                            if wait_time_ms > 0:
                                time.sleep(float(wait_time_ms) / 1000)

                self.check_document_status(
                    client,
                    uuid,
                    document.name,
                    "Document",
                    "Chunk",
                    self.vectorizer,
                    len(document.chunks),
                )
            return True
        except Exception as e:
            raise Exception(e)

    def check_document_status(
        self,
        client: WeaviateClient,
        doc_uuid: UUID,
        doc_name: str,
        doc_class_name: str,
        chunk_class_name: str,
        target_vector: VectorizerOrEmbeddingType,
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
        # TODO: target vector

        doc_class = client.collections.get(doc_class_name)

        document = doc_class.query.fetch_object_by_id(doc_uuid)

        if document is not None:
            results = doc_class.query.fetch_objects(
                filters=Filter.by_property("doc_name").equal(doc_name),
                limit=chunk_count + 1,
                return_properties=DocumentType,
                target_vector=target_vector.name,
            )

            if len(results.objects) != chunk_count:
                # Rollback if fails
                self.remove_document(client, doc_name, doc_class_name, chunk_class_name)
                raise Exception(
                    f"Chunk mismatch for {doc_uuid} {len(results.objects)} != {chunk_count}"
                )
        else:
            raise Exception(f"Document {doc_uuid} not found {document}")

    def remove_document(
        self,
        client: WeaviateClient,
        doc_name: str,
        doc_class_name: str,
        chunk_class_name: str,
    ) -> None:
        """Deletes documents and its chunks
        @parameter: client : Client - Weaviate Client
        @parameter: doc_name : str - Document name
        @parameter: doc_class_name : str - Class name of Document
        @parameter: chunk_class_name : str - Class name of Chunks.
        """
        # TODO: currently deletes ALL vectors!

        doc_collection = client.collections.get(doc_class_name)

        doc_collection.data.delete_many(
            where=Filter.by_property("doc_name").equal(doc_name)
        )

        chunk_collection = client.collections.get(chunk_class_name)

        chunk_collection.data.delete_many(
            where=Filter.by_property("doc_name").equal(doc_name)
        )

        msg.warn(f"Deleted document {doc_name} and its chunks")

    def remove_document_by_id(self, client: WeaviateClient, doc_id: str):
        # TODO: currently deletes ALL vectors!
        doc_class_name = "Document"
        chunk_class_name = "Chunk"

        chunk_collection = client.collections.get(chunk_class_name)

        chunk_collection.data.delete_by_id(doc_id)

        doc_collection = client.collections.get(doc_class_name)

        doc_collection.data.delete_by_id(doc_id)

        msg.warn(f"Deleted document {doc_id} and its chunks")

    def get_document_class(self) -> str:
        return "Document"

    def get_chunk_class(self) -> str:
        return "Chunk"

    def get_cache_class(self) -> str:
        return "Cache"

    def search_documents(
        self, client: WeaviateClient, query: str, doc_type: str
    ) -> list:
        """Search for documents from Weaviate
        @parameter query_string : str - Search query
        @returns list - Document list.
        """
        doc_class_name = "Document"

        doc_class = client.collections.get(doc_class_name)

        if doc_type == "" or doc_type is None:
            query_results = doc_class.query.hybrid(
                query=query,
                alpha=0,
                filters=Filter.by_property("doc_type").equal(doc_type),
                limit=10000,
                return_properties=DocumentType,
                target_vector=self.vectorizer.name,
            )
        else:
            query_results = doc_class.query.hybrid(
                query=query,
                alpha=0,
                filters=Filter.by_property("doc_type").equal(doc_type),
                limit=10000,
                return_properties=DocumentType,
                target_vector=self.vectorizer.name,
            )

        results = query_results.objects
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
        self, client: WeaviateClient, query: str, dist: float = 0.04
    ) -> str:
        """Retrieve results from semantic cache based on query and distance threshold
        @parameter query - str - User query
        @parameter dist - float - Distance threshold
        @returns Optional[dict] - List of results or None.
        """
        needs_vectorization = self.get_need_vectorization()

        match_results = client.collections.get(
            self.get_cache_class()
        ).query.fetch_objects(
            filters=Filter.by_property("query").equal(query),
            limit=1,
            return_properties=SuggestionType,
        )

        cache_class = client.collections.get(self.get_cache_class())

        if (
            match_results is not None
            and len(match_results.objects) > 0
            and (query == match_results.objects[0].properties.get("query"))
        ):
            msg.good("Direct match from cache")
            return (
                match_results.objects[0].properties.get("system"),
                0.0,
            )

        if needs_vectorization:
            vector = self.vectorize_query(query)
            query_results = cache_class.query.near_vector(
                near_vector=vector, return_properties=SuggestionType
            )

        else:
            query_results = cache_class.query.near_text(
                query=query, return_properties=SuggestionType
            )

        if len(query_results.objects) == 0:
            msg.warn(query_results)
            return None, None

        results = query_results.objects

        if not results:
            return None, None

        result = results[0]

        if float(result.metadata.distance) <= dist:
            msg.good("Retrieved similar from cache")
            return result.properties.get("system"), float(result.metadata.distance)

        else:
            return None, None

    def add_to_semantic_cache(self, client: WeaviateClient, query: str, system: str):
        """Add results to semantic cache
        @parameter query : str - User query
        @parameter results : list[dict] - Results from Weaviate
        @parameter system : str - System message
        @returns None.
        """
        needs_vectorization = self.get_need_vectorization()

        cache_class = client.collections.get(self.get_cache_class())

        if needs_vectorization:
            vector = self.vectorize_query(query)
            cache_class.data.insert(
                properties={"query": str(query), "system": system}, vector=vector
            )
        else:
            cache_class.data.insert(properties={"query": str(query), "system": system})
