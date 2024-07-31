import os
import ssl
import time
import importlib
import math
import json

from spacy.tokens import Doc
import spacy

import weaviate
from dotenv import load_dotenv, find_dotenv
from wasabi import msg
from weaviate.embedded import EmbeddedOptions
import asyncio

from goldenverba.server.helpers import LoggerManager

from goldenverba.components.chunk import Chunk
from goldenverba.components.document import Document
from goldenverba.server.types import ImportStreamPayload, FileConfig,FileStatus, ChunkScore

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

    async def connect(self):
        await self.weaviate_manager.connect()
        await self.weaviate_manager.verify_collections(self.environment_variables, self.installed_libraries)

    async def disconnect(self):
        await self.weaviate_manager.disconnect()

    # Import

    async def import_document(self, fileConfig: FileConfig, logger: LoggerManager):
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 

            duplicate_uuid = await self.weaviate_manager.exist_document_name(fileConfig.filename)
            if duplicate_uuid is not None and not fileConfig.overwrite:
                raise Exception(f"{fileConfig.filename} already exists in Verba")
            elif duplicate_uuid is not None and fileConfig.overwrite:
                await self.weaviate_manager.delete_document(duplicate_uuid)
                await logger.send_report(fileConfig.fileID, status=FileStatus.STARTING, message=f"Overwriting {fileConfig.filename}", took=0)
            else:
                await logger.send_report(fileConfig.fileID, status=FileStatus.STARTING, message="Starting Import", took=0)

            documents = await asyncio.create_task(self.reader_manager.load(fileConfig.rag_config["Reader"].selected, fileConfig, logger))

            for document in documents:
                duplicate_uuid = await self.weaviate_manager.exist_document_name(document.title)
                if duplicate_uuid is not None and not fileConfig.overwrite:
                    raise Exception(f"{document.title} already exists in Verba")
                elif duplicate_uuid is not None and fileConfig.overwrite:
                    await self.weaviate_manager.delete_document(duplicate_uuid)

            chunk_task = asyncio.create_task(self.chunker_manager.chunk(fileConfig.rag_config["Chunker"].selected, fileConfig, documents, self.embedder_manager.embedders[fileConfig.rag_config["Embedder"].selected], logger))
            chunked_documents = await chunk_task

            embedding_task = asyncio.create_task(self.embedder_manager.vectorize(fileConfig.rag_config["Embedder"].selected, fileConfig, chunked_documents, logger))
            vectorized_documents = await embedding_task

            for document in vectorized_documents:
                ingesting_task = asyncio.create_task(self.weaviate_manager.import_document(document,fileConfig.rag_config["Embedder"].components[fileConfig.rag_config["Embedder"].selected].config["Model"].value))
                await ingesting_task

            if len(vectorized_documents) > 1:
                await logger.send_report(fileConfig.fileID, status=FileStatus.INGESTING, message=f"Imported {fileConfig.filename} and it's {len(vectorized_documents)} documents into Weaviate", took=round(loop.time() - start_time, 2))
            else:
                await logger.send_report(fileConfig.fileID, status=FileStatus.INGESTING, message=f"Imported {fileConfig.filename} and {len(vectorized_documents[0].chunks)} chunks into Weaviate", took=round(loop.time() - start_time, 2))
            
            await logger.send_report(fileConfig.fileID, status=FileStatus.DONE, message=f"Import for {fileConfig.filename} completed successfully", took=round(loop.time() - start_time, 2))

        except Exception as e:
            await logger.send_report(fileConfig.fileID, status=FileStatus.ERROR, message=f"Import for {fileConfig.filename} failed: {str(e)}", took=0)
            return 

    # Configuration

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

        retrievers = self.retriever_manager.retrievers
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

    async def set_config(self, config: dict):
        msg.info("Saving Configuration")
        await self.weaviate_manager.set_config(self.config_uuid, config)

    async def load_config(self):
        """Check if a Configuration File exists in the database, if yes, check if corrupted. Returns a valid configuration file"""
        loaded_config = await self.weaviate_manager.get_config(self.config_uuid)
        new_config = self.create_config()

        if loaded_config is not None:
            if self.verify_config(loaded_config, new_config):
                msg.info("Using Existing Configuration")
                return loaded_config
            else:
                msg.info("Using New Configuration")
                await self.set_config(new_config)
                return new_config
        else:
            msg.info("Using New Configuration")
            return new_config
    
    def verify_config(self, a: dict, b: dict) -> bool:
        # Check Settings ( RAG & Settings )
        try:
            if len(list(a.keys())) != len(list(b.keys())):
                msg.fail(f"Config Validation Failed: {len(list(a.keys()))} != {len(list(b.keys()))}")
                return False  

            if "RAG" not in a or "RAG" not in b:
                msg.fail(f"Config Validation Failed, RAG is missing: {list(a.keys())} != {list(b.keys())}")
                return False
            
            if len(list(a["RAG"].keys())) != len(list(b["RAG"].keys())):
                msg.fail(f"Config Validation Failed, RAG component count mismatch {len(list(a['RAG'].keys()))} != {len(list(b['RAG'].keys()))}")
                return False  

            for a_component_key, b_component_key in zip(a["RAG"], b["RAG"]):
                if a_component_key != b_component_key:
                    msg.fail(f"Config Validation Failed, component name mismatch: {a_component_key} != {b_component_key}")
                    return False
                
                a_component = a["RAG"][a_component_key]["components"]
                b_component = b["RAG"][b_component_key]["components"]

                if len(a_component) != len(b_component):
                    msg.fail(f"Config Validation Failed, {a_component_key} component count mismatch: {len(a_component)} != {len(b_component)}")
                    return False

                for a_rag_component_key, b_rag_component_key in zip(a_component,b_component):
                    if a_rag_component_key != b_rag_component_key:
                        msg.fail(f"Config Validation Failed, component name mismatch: {a_rag_component_key} != {b_rag_component_key}")
                        return False
                    a_rag_component = a_component[a_rag_component_key]
                    b_rag_component = b_component[b_rag_component_key]

                    a_config = a_rag_component["config"]
                    b_config = b_rag_component["config"]

                    if len(a_config) != len(b_config):
                        msg.fail(f"Config Validation Failed, component config count mismatch: {len(a_config)} != {len(b_config)}")
                        return False
                    
                    for a_config_key, b_config_key in zip(a_config, b_config):
                        if a_config_key != b_config_key:
                                msg.fail(f"Config Validation Failed, component name mismatch: {a_config_key} != {b_config_key}")
                                return False
                        
                        a_setting = a_config[a_config_key]
                        b_setting = b_config[b_config_key]

                        if a_setting['description'] != b_setting['description']:
                            msg.fail(f"Config Validation Failed, description mismatch: {a_setting['description']} != {b_setting['description']}")
                            return False
                        
                        if a_setting['values'] != b_setting['values']:
                            msg.fail(f"Config Validation Failed, values mismatch: {a_setting['values']} != {b_setting['values']}")
                            return False

            return True

        except Exception as e:
            msg.fail(f"Config Validation failed: {str(e)}")
            return False
            
    def reset_config(self):
        msg.info("Resetting Configuration")
        self.weaviate_manager.reset_config(self.config_uuid)

    # Environment and Libraries

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

    # Document Content Retrieval
                
    async def get_content(self, uuid: str, page: int, chunkScores: list[ChunkScore]):

        document = await self.weaviate_manager.get_document(uuid)

        nlp = spacy.blank("en")
        config = {"punct_chars": None}
        nlp.add_pipe("sentencizer", config=config)

        doc = nlp(document["content"])

        batch_size = 2000

        content_pieces = []

        if len(chunkScores) > 0:
            if page > len(chunkScores):
                page = 0

            total_batches = len(chunkScores)
            chunk = await self.weaviate_manager.get_chunk(chunkScores[page].uuid, chunkScores[page].embedder)

            start_index = int(chunk["start_i"])
            end_index = int(chunk["end_i"])

            before_start_index = max(start_index-(batch_size/2),0)
            before_end_index = max(start_index-1,0)

            after_start_index = min(end_index+1,len(doc))
            after_end_index = min(end_index+(batch_size/2),len(doc))

            content_pieces.append({"content":doc[before_start_index:before_end_index].text, "chunk_id": 0, "score": 0, "type": "text"})
            content_pieces.append({"content":doc[start_index:end_index].text, "chunk_id": chunkScores[page].chunk_id, "score": chunkScores[page].score, "type": "extract"})
            content_pieces.append({"content":doc[after_start_index:after_end_index].text, "chunk_id": 0, "score": 0, "type": "text"})


        else:
            start_index = page * batch_size
            end_index = start_index + batch_size

            total_batches = math.ceil(len(doc) / batch_size)

            if start_index >= len(doc):
                return ("", total_batches)  # or handle as needed (e.g., return None or raise an error)
            
            content_pieces.append({"content":doc[start_index:end_index].text, "chunk_id": 0, "score": 0, "type": "text"})
            
        return (content_pieces, total_batches)

    # Retrieval Augmented Generation

    async def retrieve_chunks(self, query: str, rag_config: dict):
        retriever = rag_config["Retriever"].selected
        embedder = rag_config["Embedder"].selected

        vector = await self.embedder_manager.vectorize_query(embedder, query, rag_config)

        documents, context = await self.retriever_manager.retrieve(retriever, query, vector, rag_config, self.weaviate_manager)

        return (documents, context)


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
