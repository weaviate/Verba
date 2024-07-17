import os
import ssl
import time
import importlib

import weaviate
from dotenv import load_dotenv, find_dotenv
from wasabi import msg
from weaviate.embedded import EmbeddedOptions
import asyncio

import goldenverba.components.schema.schema_generation as schema_manager
from goldenverba.server.ImportLogger import LoggerManager

from goldenverba.components.chunk import Chunk
from goldenverba.components.document import Document
from goldenverba.server.types import ImportStreamPayload, FileConfig,FileStatus

from goldenverba.components.interfaces import (
    VerbaComponent,
    Reader,
    Chunker,
    Embedder,
    Retriever,
    Generator,
)
from goldenverba.components.managers import (
    ReaderManager,
    ChunkerManager,
    EmbeddingManager,
    RetrieverManager,
    GeneratorManager,
    WeaviateManager
)

load_dotenv()

class VerbaManager:
    """Manages all Verba Components."""

    def __init__(self) -> None:
        self.reader_manager = ReaderManager()
        self.chunker_manager = ChunkerManager()
        self.embedder_manager = EmbeddingManager()
        self.retriever_manager = RetrieverManager()
        self.generator_manager = GeneratorManager()
        self.weaviate_manager = WeaviateManager()
        self.config_uuid = "e0adcc12-9bad-4588-8a1e-bab0af6ed485"
        self.environment_variables = {}
        self.installed_libraries = {}
        self.weaviate_type = ""
        self.enable_caching = True

        self.verify_installed_libraries()
        self.verify_variables()

        self.weaviate_manager.connect()
        self.weaviate_manager.verify_collections(self.environment_variables, self.installed_libraries)

    async def import_document(self, fileConfig: FileConfig, logger: LoggerManager):
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 

            # TODO Check for duplicate filename
            # Check if document names exist in DB
            # for document in loaded_documents:
            #    if not self.check_if_document_exits(document):
            #        filtered_documents.append(document)
            #    else:
            #        logger.send_message(f"{document.name} already exists.",2)

            await logger.send_report(fileConfig.fileID, status=FileStatus.STARTING, message="Starting Import", took=0)

            load_task = asyncio.create_task(self.reader_manager.load(fileConfig.rag_config["Reader"].selected, fileConfig, logger))
            document = await load_task

            chunk_task = asyncio.create_task(self.chunker_manager.chunk(fileConfig.rag_config["Chunker"].selected, fileConfig, document, logger))
            chunked_document = await chunk_task

            embedding_task = asyncio.create_task(self.embedder_manager.vectorize(fileConfig.rag_config["Embedder"].selected, fileConfig, document, logger))
            vectorized_document = await embedding_task

            await logger.send_report(fileConfig.fileID, status=FileStatus.DONE, message=f"Successfully imported {fileConfig.filename} into Verba", took=round(loop.time() - start_time, 2))

        except Exception as e:
            await logger.send_report(fileConfig.fileID, status=FileStatus.ERROR, message=f"Error when importing {fileConfig.filename}: {str(e)}", took=0)
            return 

    def create_config(self) -> dict:
        """Creates the RAG Configuration and returns the full Verba Config with also Settings"""

        setting_config = {}

        available_environments = self.environment_variables
        available_libraries = self.installed_libraries

        readers = self.reader_manager.readers
        reader_config = {
            "components": {
                reader: readers[reader].get_meta(
                    available_environments, available_libraries
                )
                for reader in readers
            },
            "selected": list(readers.values())[0].name,
        }

        chunkers = self.chunker_manager.chunkers
        chunkers_config = {
            "components": {
                chunker: chunkers[chunker].get_meta(
                    available_environments, available_libraries
                )
                for chunker in chunkers
            },
            "selected": list(chunkers.values())[0].name,
        }

        embedders = self.embedder_manager.embedders
        embedder_config = {
            "components": {
                embedder: embedders[embedder].get_meta(
                    available_environments, available_libraries
                )
                for embedder in embedders
            },
            "selected": list(embedders.values())[0].name,
        }

        retrievers = self.retriever_manager.get_retrievers()
        retrievers_config = {
            "components": {
                retriever: retrievers[retriever].get_meta(
                    available_environments, available_libraries
                )
                for retriever in retrievers
            },
            "selected": list(retrievers.values())[0].name,
        }

        generators = self.generator_manager.get_generators()
        generator_config = {
            "components": {
                generator: generators[generator].get_meta(
                    available_environments, available_libraries
                )
                for generator in generators
            },
            "selected": list(generators.values())[0].name,
        }

        return {
            "RAG": {
                "Reader": reader_config,
                "Chunker": chunkers_config,
                "Embedder": embedder_config,
                "Retriever": retrievers_config,
                "Generator": generator_config,
            },
            "SETTING": setting_config,
        }

    def set_config(self, config: dict):
        msg.info("Saving Configuration")
        self.weaviate_manager.set_config(self.config_uuid, config)

    def load_config(self):
        """Check if a Configuration File exists in the database, if yes, check if corrupted. Returns a valid configuration file"""
        loaded_config = self.weaviate_manager.get_config(self.config_uuid)
        if loaded_config is not None:
            msg.info("Using Existing Configuration")
            return loaded_config
        else:
            msg.info("Creating Configuration")
            return self.create_config()
        
    def reset_config(self):
        msg.info("Resetting Configuration")
        self.weaviate_manager.reset_config(self.config_uuid)

    def verify_installed_libraries(self) -> None:
        """
        Checks which libraries are installed and fills out the self.installed_libraries dictionary for the frontend to access, this will be displayed in the status page.
        """
        reader = [lib for reader in self.reader_manager.readers for lib in self.reader_manager.readers[reader].requires_library]
        chunker = [lib for chunker in self.chunker_manager.chunkers for lib in self.chunker_manager.chunkers[chunker].requires_library]
        embedder = [lib for embedder in self.embedder_manager.embedders for lib in self.embedder_manager.embedders[embedder].requires_library]
        retriever = [lib for retriever in self.retriever_manager.retrievers for lib in self.retriever_manager.retrievers[retriever].requires_library]
        generator = [lib for generator in self.generator_manager.generators for lib in self.generator_manager.generators[generator].requires_library]

        required_libraries = reader + chunker + embedder + retriever + generator
        unique_libraries = set(required_libraries)

        for lib in unique_libraries:
            try:
                importlib.import_module(lib)
                self.installed_libraries[lib] = True
            except Exception:
                self.installed_libraries[lib] = False

    def verify_variables(self) -> None:
        """
        Checks which environment variables are installed and fills out the self.environment_variables dictionary for the frontend to access.
        """
        reader = [lib for reader in self.reader_manager.readers for lib in self.reader_manager.readers[reader].requires_env]
        chunker = [lib for chunker in self.chunker_manager.chunkers for lib in self.chunker_manager.chunkers[chunker].requires_env]
        embedder = [lib for embedder in self.embedder_manager.embedders for lib in self.embedder_manager.embedders[embedder].requires_env]
        retriever = [lib for retriever in self.retriever_manager.retrievers for lib in self.retriever_manager.retrievers[retriever].requires_env]
        generator = [lib for generator in self.generator_manager.generators for lib in self.generator_manager.generators[generator].requires_env]

        required_envs = reader + chunker + embedder + retriever + generator
        unique_envs = set(required_envs)

        for env in unique_envs:
            if os.environ.get(env) is not None:
                self.environment_variables[env] = True
            else:
                self.environment_variables[env] = False
   
   ########

    def get_schemas(self) -> dict:
        """
        @returns dict - A dictionary with the schema names and their object count.
        """
        schema_info = self.client.schema.get()

        schemas = {}

        try:
            for _class in schema_info["classes"]:
                results = (
                    self.client.query.aggregate(_class["class"]).with_meta_count().do()
                )
                if "VERBA" in _class["class"]:
                    schemas[_class["class"]] = (
                        results.get("data", {})
                        .get("Aggregate", {})
                        .get(_class["class"], [{}])[0]
                        .get("meta", {})
                        .get("count", 0)
                    )
        except Exception as e:
            msg.fail(f"Couldn't retrieve information about Collections, if you're using Weaviate Embedded, try to reset `~/.local/share/weaviate` ({str(e)})")

        return schemas

    def get_suggestions(self, query: str) -> list[str]:
        """Retrieve suggestions based on user query
        @parameter query : str - User query
        @returns list[str] - List of possible autocomplete suggestions.
        """
        query_results = (
            self.client.query.get(
                class_name="VERBA_Suggestion",
                properties=["suggestion"],
            )
            .with_bm25(query=query)
            .with_limit(3)
            .do()
        )

        results = query_results["data"]["Get"]["VERBA_Suggestion"]

        if not results:
            return []

        suggestions = []

        for result in results:
            suggestions.append(result["suggestion"])

        return suggestions

    def set_suggestions(self, query: str):
        """Adds suggestions to the suggestion class
        @parameter query : str - Query to save in suggestions.
        """
        # Don't set new suggestions when in production
        production_key = os.environ.get("VERBA_PRODUCTION", "")
        if production_key == "True":
            return
        check_results = (
            self.client.query.get(
                class_name="VERBA_Suggestion",
                properties=["suggestion"],
            )
            .with_where(
                {
                    "path": ["suggestion"],
                    "operator": "Equal",
                    "valueText": query,
                }
            )
            .with_limit(1)
            .do()
        )

        if (
            "data" in check_results
            and len(check_results["data"]["Get"]["VERBA_Suggestion"]) > 0
        ):
            if (
                query
                == check_results["data"]["Get"]["VERBA_Suggestion"][0]["suggestion"]
            ):
                return

        with self.client.batch as batch:
            batch.batch_size = 1
            properties = {
                "suggestion": query,
            }
            self.client.batch.add_data_object(properties, "VERBA_Suggestion")

        msg.info("Added query to suggestions")

    def retrieve_chunks(self, queries: list[str]) -> list[Chunk]:
        chunks, context = self.retriever_manager.retrieve(
            queries,
            self.client,
            self.embedder_manager.embedders[self.embedder_manager.selected_embedder],
            self.generator_manager.generators[
                self.generator_manager.selected_generator
            ],
        )
        return chunks, context

    def retrieve_all_documents(self, doc_type: str, page: int, pageSize: int) -> list:
        """Return all documents from Weaviate
        @returns list - Document list.
        """
        class_name = "VERBA_Document_" + schema_manager.strip_non_letters(
            self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].vectorizer
        )

        offset = pageSize * (page - 1)

        if doc_type == "":
            query_results = (
                self.client.query.get(
                    class_name=class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_additional(properties=["id"])
                .with_limit(pageSize)
                .with_offset(offset)
                .with_sort(
                    [
                        {
                            "path": ["doc_name"],
                            "order": "asc",
                        }
                    ]
                )
                .do()
            )
        else:
            query_results = (
                self.client.query.get(
                    class_name=class_name,
                    properties=["doc_name", "doc_type", "doc_link"],
                )
                .with_additional(properties=["id"])
                .with_where(
                    {
                        "path": ["doc_type"],
                        "operator": "Equal",
                        "valueText": doc_type,
                    }
                )
                .with_limit(pageSize)
                .with_offset(offset)
                .with_sort(
                    [
                        {
                            "path": ["doc_name"],
                            "order": "asc",
                        }
                    ]
                )
                .do()
            )

        results = query_results["data"]["Get"][class_name]
        return results

    def retrieve_all_document_types(self) -> list:
        """Aggreagtes and returns all document types from Weaviate
        @returns list - Document list.
        """
        class_name = "VERBA_Document_" + schema_manager.strip_non_letters(
            self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].vectorizer
        )

        query_results = (
            self.client.query.aggregate(class_name)
            .with_fields("doc_type {count topOccurrences {value occurs}}")
            .do()
        )

        results = [
            doc_type["value"]
            for doc_type in query_results["data"]["Aggregate"][class_name][0][
                "doc_type"
            ]["topOccurrences"]
        ]
        return results

    def retrieve_document(self, doc_id: str) -> dict:
        """Return a document by it's ID (UUID format) from Weaviate
        @parameter doc_id : str - Document ID
        @returns dict - Document dict.
        """
        class_name = "VERBA_Document_" + schema_manager.strip_non_letters(
            self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].vectorizer
        )

        document = self.client.data_object.get_by_id(
            doc_id,
            class_name=class_name,
        )
        return document

    async def generate_answer(
        self, queries: list[str], contexts: list[str], conversation: dict
    ):
        semantic_result = None
        if self.enable_caching:
            semantic_query = self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].conversation_to_query(queries, conversation)
            (
                semantic_result,
                distance,
            ) = self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].retrieve_semantic_cache(self.client, semantic_query)

        if semantic_result is not None:
            return {
                "message": str(semantic_result),
                "finish_reason": "stop",
                "cached": True,
                "distance": distance,
            }

        else:
            full_text = await self.generator_manager.generators[
                self.generator_manager.selected_generator
            ].generate(queries, contexts, conversation)
            if self.enable_caching:
                self.embedder_manager.embedders[
                    self.embedder_manager.selected_embedder
                ].add_to_semantic_cache(self.client, semantic_query, full_text)
                self.set_suggestions(" ".join(queries))
            return full_text

    async def generate_stream_answer(
        self, queries: list[str], contexts: list[str], conversation: dict
    ):

        semantic_result = None

        if self.enable_caching:
            semantic_query = self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].conversation_to_query(queries, conversation)
            (
                semantic_result,
                distance,
            ) = self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].retrieve_semantic_cache(self.client, semantic_query)

        if semantic_result is not None:
            yield {
                "message": str(semantic_result),
                "finish_reason": "stop",
                "cached": True,
                "distance": distance,
            }

        else:
            full_text = ""
            async for result in self.generator_manager.generators[
                self.generator_manager.selected_generator
            ].generate_stream(queries, contexts, conversation):
                full_text += result["message"]
                yield result
            if self.enable_caching:
                self.set_suggestions(" ".join(queries))
                self.embedder_manager.embedders[
                    self.embedder_manager.selected_embedder
                ].add_to_semantic_cache(self.client, semantic_query, full_text)

    def reset(self):
        self.client.schema.delete_class("VERBA_Suggestion")
        # Check if all schemas exist for all possible vectorizers
        for vectorizer in schema_manager.VECTORIZERS:
            schema_manager.reset_schemas(self.client, vectorizer)

        for embedding in schema_manager.EMBEDDINGS:
            schema_manager.reset_schemas(self.client, embedding)

        for vectorizer in schema_manager.VECTORIZERS:
            schema_manager.init_schemas(self.client, vectorizer, False, True)

        for embedding in schema_manager.EMBEDDINGS:
            schema_manager.init_schemas(self.client, embedding, False, True)

    def reset_documents(self):
        # Check if all schemas exist for all possible vectorizers
        for vectorizer in schema_manager.VECTORIZERS:
            document_class_name = "VERBA_Document_" + schema_manager.strip_non_letters(
                vectorizer
            )
            chunk_class_name = "VERBA_Chunk_" + schema_manager.strip_non_letters(
                vectorizer
            )
            self.client.schema.delete_class(document_class_name)
            self.client.schema.delete_class(chunk_class_name)
            schema_manager.init_schemas(self.client, vectorizer, False, True)

        for embedding in schema_manager.EMBEDDINGS:
            document_class_name = "VERBA_Document_" + schema_manager.strip_non_letters(
                embedding
            )
            chunk_class_name = "VERBA_Chunk_" + schema_manager.strip_non_letters(
                embedding
            )
            self.client.schema.delete_class(document_class_name)
            self.client.schema.delete_class(chunk_class_name)
            schema_manager.init_schemas(self.client, embedding, False, True)

    def reset_cache(self):
        # Check if all schemas exist for all possible vectorizers
        for vectorizer in schema_manager.VECTORIZERS:
            class_name = "VERBA_Cache_" + schema_manager.strip_non_letters(vectorizer)
            self.client.schema.delete_class(class_name)
            schema_manager.init_schemas(self.client, vectorizer, False, True)

        for embedding in schema_manager.EMBEDDINGS:
            class_name = "VERBA_Cache_" + schema_manager.strip_non_letters(embedding)
            self.client.schema.delete_class(class_name)
            schema_manager.init_schemas(self.client, embedding, False, True)

    def reset_suggestion(self):
        self.client.schema.delete_class("VERBA_Suggestion")
        schema_manager.init_suggestion(self.client, "", False, True)



    def check_if_document_exits(self, document: Document) -> bool:
        """Return a document by it's ID (UUID format) from Weaviate
        @parameter document : Document - Document object
        @returns bool - Whether the doc name exist in the cluster.
        """
        class_name = "VERBA_Document_" + schema_manager.strip_non_letters(
            self.embedder_manager.embedders[
                self.embedder_manager.selected_embedder
            ].vectorizer
        )

        results = (
            self.client.query.get(
                class_name=class_name,
                properties=[
                    "doc_name",
                ],
            )
            .with_where(
                {
                    "path": ["doc_name"],
                    "operator": "Equal",
                    "valueText": document.name,
                }
            )
            .with_limit(1)
            .do()
        )

        if "data" in results:
            if results["data"]["Get"][class_name]:
                msg.warn(f"{document.name} already exists")
                return True
        else:
            msg.warn(f"Error occured while checking for duplicates: {results}")
        
        return False

    def check_verba_component(self, component: VerbaComponent) -> tuple[bool, str]:
        return component.check_available(
            self.environment_variables, self.installed_libraries
        )

    def delete_document_by_id(self, doc_id: str) -> None:
        self.embedder_manager.embedders[
            self.embedder_manager.selected_embedder
        ].remove_document_by_id(self.client, doc_id)

    def search_documents(
        self, query: str, doc_type: str, page: int, pageSize: int
    ) -> list:
        return self.embedder_manager.embedders[
            self.embedder_manager.selected_embedder
        ].search_documents(self.client, query, doc_type, page, pageSize)
