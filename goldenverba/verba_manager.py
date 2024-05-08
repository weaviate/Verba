import os
import ssl

import weaviate
from dotenv import load_dotenv, find_dotenv
from wasabi import msg
from weaviate.embedded import EmbeddedOptions

import goldenverba.components.schema.schema_generation as schema_manager

from goldenverba.components.chunk import Chunk
from goldenverba.components.document import Document
from goldenverba.components.types import FileData

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
        self.environment_variables = {}
        self.installed_libraries = {}
        self.weaviate_type = ""
        self.client = self.setup_client()
        self.enable_caching = True

        self.verify_installed_libraries()
        self.verify_variables()

        # Check if all schemas exist for all possible vectorizers
        for vectorizer in schema_manager.VECTORIZERS:
            schema_manager.init_schemas(self.client, vectorizer, False, True)

        for embedding in schema_manager.EMBEDDINGS:
            schema_manager.init_schemas(self.client, embedding, False, True)

    def import_data(
        self, fileData: list[FileData], textValues: list[str], logging: list[dict]
    ) -> list[Document]:

        loaded_documents, logging = self.reader_manager.load(
            fileData, textValues, logging
        )

        filtered_documents = []

        # Check if document names exist in DB
        for document in loaded_documents:
            if not self.check_if_document_exits(document):
                filtered_documents.append(document)
            else:
                logging.append(
                    {"type": "WARNING", "message": f"{document.name} already exists."}
                )

        modified_documents, logging = self.chunker_manager.chunk(
            filtered_documents, logging
        )

        logging = self.embedder_manager.embed(
            modified_documents, client=self.client, logging=logging
        )

        return modified_documents, logging

    def reader_set_reader(self, reader: str) -> bool:
        self.reader_manager.set_reader(reader)

    def reader_get_readers(self) -> dict[str, Reader]:
        return self.reader_manager.get_readers()

    def chunker_set_chunker(self, chunker: str) -> bool:
        return self.chunker_manager.set_chunker(chunker)

    def chunker_get_chunker(self) -> dict[str, Chunker]:
        return self.chunker_manager.get_chunkers()

    def embedder_set_embedder(self, embedder: str) -> bool:
        return self.embedder_manager.set_embedder(embedder)

    def embedder_get_embedder(self) -> dict[str, Embedder]:
        return self.embedder_manager.get_embedders()

    def retriever_set_retriever(self, retriever: str) -> bool:
        return self.retriever_manager.set_retriever(retriever)

    def retriever_get_retriever(self) -> dict[str, Retriever]:
        return self.retriever_manager.get_retrievers()

    def generator_set_generator(self, generator: str) -> bool:
        return self.generator_manager.set_generator(generator)

    def generator_get_generator(self) -> dict[str, Generator]:
        return self.generator_manager.get_generators()

    def setup_client(self):
        """
        @returns Optional[Client] - The Weaviate Client.
        """
        msg.info("Setting up client")

        additional_header = {}
        client = None

        openai_header_key_name = "X-OpenAI-Api-Key"

        # Check OpenAI ENV KEY
        try:
            import openai

            openai_key = os.environ.get("OPENAI_API_KEY", "")
            if "OPENAI_API_TYPE" in os.environ:
                openai.api_type = os.getenv("OPENAI_API_TYPE")
            if "OPENAI_BASE_URL" in os.environ:
                openai.api_base = os.getenv("OPENAI_BASE_URL")
            if "OPENAI_API_VERSION" in os.environ:
                openai.api_version = os.getenv("OPENAI_API_VERSION")

            if os.getenv("OPENAI_API_TYPE") == "azure":
                openai_header_key_name = "X-Azure-Api-Key"

            if openai_key != "":
                additional_header[openai_header_key_name] = openai_key
                self.environment_variables["OPENAI_API_KEY"] = True
                openai.api_key = openai_key
            else:
                self.environment_variables["OPENAI_API_KEY"] = False

        except Exception:
            self.environment_variables["OPENAI_API_KEY"] = False

        cohere_key = os.environ.get("COHERE_API_KEY", "")
        if cohere_key != "":
            additional_header["X-Cohere-Api-Key"] = cohere_key

        # Check Google Key
        google_key = os.environ.get("GOOGLE_API_KEY", "")
        self.environment_variables["GOOGLE_API_KEY"] = False
        if google_key != "":
            additional_header["X-Palm-Api-Key"] = google_key
            self.environment_variables["GOOGLE_API_KEY"] = True

        google_project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")

        # Check Verba URL ENV
        weaviate_url = os.environ.get("WEAVIATE_URL_VERBA", "")
        if weaviate_url != "":
            weaviate_key = os.environ.get("WEAVIATE_API_KEY_VERBA", "")
            if weaviate_key != "":
                self.environment_variables["WEAVIATE_API_KEY_VERBA"] = True
                auth_config = weaviate.AuthApiKey(api_key=weaviate_key)
                msg.info("Auth information provided")
                client = weaviate.Client(
                    url=weaviate_url,
                    additional_headers=additional_header,
                    auth_client_secret=auth_config,
                )
            else:
                msg.info("No Auth information provided")
                client = weaviate.Client(
                    url=weaviate_url,
                    additional_headers=additional_header,
                )
            self.environment_variables["WEAVIATE_URL_VERBA"] = True
            self.weaviate_type = "Weaviate Cluster"

        # Use Weaviate Embedded
        else:
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            if google_project != "":
                additional_env_vars = {
                    "ENABLE_MODULES": "text2vec-openai,generative-openai,qna-openai,text2vec-cohere,text2vec-palm",
                    "GOOGLE_CLOUD_PROJECT": google_project,
                }
            else:
                additional_env_vars = {
                    "ENABLE_MODULES": "text2vec-openai,generative-openai,qna-openai,text2vec-cohere",
                }

            msg.info("Using Weaviate Embedded")
            self.weaviate_type = "Weaviate Embedded"
            client = weaviate.Client(
                additional_headers=additional_header,
                embedded_options=EmbeddedOptions(
                    additional_env_vars=additional_env_vars
                ),
            )

        if client is not None:
            msg.good("Connected to Weaviate")

            # Batch Configuration
            def batch_callback(logs: dict):
                if logs is not None:
                    for result in logs:
                        if "result" in result and "errors" in result["result"]:
                            if "error" in result["result"]["errors"]:
                                msg.fail(result["result"])

            client.batch.configure(callback=batch_callback)

        else:
            msg.fail("Connection to Weaviate failed")

        return client

    def verify_installed_libraries(self) -> None:
        """
        Checks which libraries are installed and fills out the self.installed_libraries dictionary for the frontend to access, this will be displayed in the status page.
        """
        try:
            import pypdf

            self.installed_libraries["pypdf"] = True
        except Exception:
            self.installed_libraries["pypdf"] = False

        try:
            import tiktoken

            self.installed_libraries["tiktoken"] = True
        except Exception:
            self.installed_libraries["tiktoken"] = False

        try:
            import openai

            self.installed_libraries["openai"] = True
        except Exception:
            self.installed_libraries["openai"] = False

        try:
            import vertexai

            self.installed_libraries["vertexai"] = True
        except Exception:
            self.installed_libraries["vertexai"] = False

        try:
            import transformers

            self.installed_libraries["transformers"] = True
        except Exception:
            self.installed_libraries["transformers"] = False

        try:
            import accelerate

            self.installed_libraries["accelerate"] = True
        except Exception:
            self.installed_libraries["accelerate"] = False

        try:
            import torch

            if torch.cuda.is_available():
                msg.info("CUDA is available. Using CUDA...")
            elif torch.backends.mps.is_available():
                msg.info("MPS is available. Using MPS...")
            else:
                msg.info("Neither CUDA nor MPS is available. Using CPU...")

            self.installed_libraries["torch"] = True
        except Exception:
            self.installed_libraries["torch"] = False

    def verify_variables(self) -> None:
        """
        Checks which environment variables are installed and fills out the self.environment_variables dictionary for the frontend to access.
        """

        # Ollama URL
        if os.environ.get("OLLAMA_URL", "") != "":
            self.environment_variables["OLLAMA_URL"] = True
        else:
            self.environment_variables["OLLAMA_URL"] = False

        if os.environ.get("OLLAMA_MODEL", "") != "":
            self.environment_variables["OLLAMA_MODEL"] = True
        else:
            self.environment_variables["OLLAMA_MODEL"] = False

        # OpenAI API Key
        if os.environ.get("OPENAI_API_KEY", "") != "":
            self.environment_variables["OPENAI_API_KEY"] = True
        else:
            self.environment_variables["OPENAI_API_KEY"] = False

        if os.environ.get("OPENAI_BASE_URL", "") != "":
            self.environment_variables["OPENAI_BASE_URL"] = True
        else:
            self.environment_variables["OPENAI_BASE_URL"] = False

        # Cohere API Key
        if os.environ.get("COHERE_API_KEY", "") != "":
            self.environment_variables["COHERE_API_KEY"] = True
        else:
            self.environment_variables["COHERE_API_KEY"] = False

        # Github Token Key
        if os.environ.get("GITHUB_TOKEN", "") != "":
            self.environment_variables["GITHUB_TOKEN"] = True
        else:
            self.environment_variables["GITHUB_TOKEN"] = False

        # Unstructured Token Key
        if os.environ.get("UNSTRUCTURED_API_KEY", "") != "":
            self.environment_variables["UNSTRUCTURED_API_KEY"] = True
        else:
            self.environment_variables["UNSTRUCTURED_API_KEY"] = False

        # OpenAI API Type, should be set to "azure" if using Azure OpenAI
        if os.environ.get("OPENAI_API_TYPE", "") != "":
            self.environment_variables["OPENAI_API_TYPE"] = True
        else:
            self.environment_variables["OPENAI_API_TYPE"] = False

        # OpenAI API Version
        if os.environ.get("OPENAI_API_VERSION", "") != "":
            self.environment_variables["OPENAI_API_VERSION"] = True
        else:
            self.environment_variables["OPENAI_API_VERSION"] = False

        # GOOGLE_CLOUD_PROJECT
        if os.environ.get("GOOGLE_CLOUD_PROJECT", "") != "":
            self.environment_variables["GOOGLE_CLOUD_PROJECT"] = True
        else:
            self.environment_variables["GOOGLE_CLOUD_PROJECT"] = False

        # GOOGLE_APPLICATION_CREDENTIALS
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "") != "":
            self.environment_variables["GOOGLE_APPLICATION_CREDENTIALS"] = True
        else:
            self.environment_variables["GOOGLE_APPLICATION_CREDENTIALS"] = False

        # Azure openai ressource name, mandatory when using Azure, should be XXX when endpoint is https://XXX.openai.azure.com
        if os.environ.get("AZURE_OPENAI_RESOURCE_NAME", "") != "":
            self.environment_variables["AZURE_OPENAI_RESOURCE_NAME"] = True
        else:
            self.environment_variables["AZURE_OPENAI_RESOURCE_NAME"] = False

        # Model used for embeddings. mandatory when using Azure. Typically "text-embedding-ada-002"
        if os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL", "") != "":
            self.environment_variables["AZURE_OPENAI_EMBEDDING_MODEL"] = True
        else:
            self.environment_variables["AZURE_OPENAI_EMBEDDING_MODEL"] = False

        # Model used for queries. mandatory when using Azure, but can also be used to change the model used for queries when using OpenAI.
        if os.environ.get("OPENAI_MODEL", "") != "":
            self.environment_variables["OPENAI_MODEL"] = True
        else:
            self.environment_variables["OPENAI_MODEL"] = False

        if os.environ.get("OPENAI_API_TYPE", "") == "azure":
            if not (
                self.environment_variables["OPENAI_BASE_URL"]
                and self.environment_variables["AZURE_OPENAI_RESOURCE_NAME"]
                and self.environment_variables["AZURE_OPENAI_EMBEDDING_MODEL"]
                and self.environment_variables["OPENAI_MODEL"]
            ):
                raise EnvironmentError(
                    "Missing environment variables. When using Azure OpenAI, you need to set OPENAI_BASE_URL, AZURE_OPENAI_RESOURCE_NAME, AZURE_OPENAI_EMBEDDING_MODEL and OPENAI_MODEL. Please check documentation."
                )

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
            msg.error(f"Couldn't retrieve information about Collections, if you're using Weaviate Embedded, try to reset `~/.local/share/weaviate` ({str(e)})")

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

    def reset_config(self):
        self.client.schema.delete_class("VERBA_Config")
        schema_manager.init_config(self.client, "", False, True)

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

        if results["data"]["Get"][class_name]:
            msg.warn(f"{document.name} already exists")
            return True
        else:
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
