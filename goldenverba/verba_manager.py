import os
import ssl
from typing import Optional, List, TypedDict
from weaviate.collections.classes.internal import Object
from weaviate.classes.query import Filter
from verba_types import SuggestionType, DocumentType
import weaviate
from weaviate.connect import ConnectionParams
from dotenv import load_dotenv
from wasabi import msg
import weaviate


import goldenverba.components.schema.schema_generation as schema_manager
from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.chunking.interface import Chunker
from goldenverba.components.chunking.manager import ChunkerManager
from goldenverba.components.component import VerbaComponent
from goldenverba.components.embedding.interface import Embedder
from goldenverba.components.embedding.manager import EmbeddingManager
from goldenverba.components.generation.interface import Generator
from goldenverba.components.generation.manager import GeneratorManager
from goldenverba.components.reader.document import Document
from goldenverba.components.reader.interface import Reader
from goldenverba.components.reader.manager import ReaderManager
from goldenverba.components.retriever.interface import Retriever
from goldenverba.components.retriever.manager import RetrieverManager

from goldenverba.components.schema.schema_generation import (
    EMBEDDINGS,
    VECTORIZERS,
    strip_non_letters,
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

        self.verify_installed_libraries()
        self.verify_variables()

        # Check if all schemas exist for all possible vectorizers

        schema_manager.init_schemas(self.client, False, True)
        schema_manager.init_schemas(self.client, False, True)

    def import_data(
        self,
        bytes: list[str],
        contents: list[str],
        paths: list[str],
        fileNames: list[str],
        document_type: str,
        units: int = 100,
        overlap: int = 50,
    ) -> list[Document]:
        loaded_documents = self.reader_manager.load(
            bytes, contents, paths, fileNames, document_type
        )

        filtered_documents = []

        # Check if document names exist in DB
        for document in loaded_documents:
            if not self.check_if_document_exists(document):
                filtered_documents.append(document)

        modified_documents = self.chunker_manager.chunk(
            filtered_documents, units, overlap
        )

        if self.embedder_manager.embed(modified_documents, client=self.client):
            msg.good("Embedding successful")
            return modified_documents
        else:
            msg.fail("Embedding failed")
            return []

    def reader_set_reader(self, reader: str) -> bool:
        available, message = self.check_verba_component(
            self.reader_manager.readers[reader]
        )

        if available:
            msg.good(f"Set Reader to {reader}")
            return self.reader_manager.set_reader(reader)
        else:
            msg.warn(message)
            return False

    def reader_get_readers(self) -> dict[str, Reader]:
        return self.reader_manager.get_readers()

    def chunker_set_chunker(self, chunker: str) -> bool:
        available, message = self.check_verba_component(
            self.chunker_manager.chunker[chunker]
        )
        if available:
            msg.good(f"Set Chunker to {chunker}")
            return self.chunker_manager.set_chunker(chunker)
        else:
            msg.warn(message)
            return False

    def chunker_get_chunker(self) -> dict[str, Chunker]:
        return self.chunker_manager.get_chunkers()

    def embedder_set_embedder(self, embedder: str) -> bool:
        available, message = self.check_verba_component(
            self.embedder_manager.embedders[embedder]
        )
        if available:
            msg.good(f"Set Embedder to {embedder}")
            return self.embedder_manager.set_embedder(embedder)
        else:
            msg.warn(message)
            return False

    def embedder_get_embedder(self) -> dict[str, Embedder]:
        return self.embedder_manager.get_embedders()

    def retriever_set_retriever(self, retriever: str) -> bool:
        available, message = self.check_verba_component(
            self.retriever_manager.retrievers[retriever]
        )
        if available:
            msg.good(f"Set Retriever to {retriever}")
            return self.retriever_manager.set_retriever(retriever)
        else:
            msg.warn(message)
            return False

    def retriever_get_retriever(self) -> dict[str, Retriever]:
        return self.retriever_manager.get_retrievers()

    def generator_set_generator(self, generator: str) -> bool:
        available, message = self.check_verba_component(
            self.generator_manager.generators[generator]
        )
        if available:
            msg.good(f"Set Generator to {generator}")
            return self.generator_manager.set_generator(generator)
        else:
            msg.warn(message)
            return False

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

        # Check Verba URL ENV
        weaviate_url = os.environ.get("WEAVIATE_URL_VERBA", "")
        weaviate_url_grpc = os.environ.get("WEAVIATE_GRPC_URL_VERBA", "")
        if weaviate_url != "" and weaviate_url_grpc != "":
            weaviate_key = os.environ.get("WEAVIATE_API_KEY_VERBA", "")
            if weaviate_key != "":
                self.environment_variables["WEAVIATE_API_KEY_VERBA"] = True
                auth_config = weaviate.auth.AuthApiKey(api_key=weaviate_key)
                msg.info("Auth information provided")
                msg.info(weaviate_url)
                client = weaviate.WeaviateClient(
                    connection_params=ConnectionParams.from_params(
                        http_host=weaviate_url,
                        http_port=443,
                        http_secure=True,
                        grpc_host=weaviate_url_grpc,
                        grpc_port=443,
                        grpc_secure=True,
                    ),
                    auth_client_secret=auth_config,
                    additional_headers=additional_header,
                )
                client.connect()
                msg.info(client)

            else:
                msg.info("No Auth information provided")
                client = weaviate.WeaviateClient(
                    connection_params=ConnectionParams.from_params(
                        http_host=weaviate_url,
                        http_port=8099,
                        http_secure=False,
                        grpc_host=weaviate_url,
                        grpc_port=50052,
                        grpc_secure=False,
                    ),
                    additional_headers=additional_header,
                )
                client.connect()
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

            msg.info("Using Weaviate Embedded")
            self.weaviate_type = "Weaviate Embedded"
            client = weaviate.connect_to_embedded(headers=additional_header)

        if client is not None:
            msg.good("Connected to Weaviate")

            # Batch Configuration
            def batch_callback(logs: List[dict]):
                if logs is not None:
                    for result in logs:
                        if "result" in result and "errors" in result["result"]:
                            if "error" in result["result"]["errors"]:
                                msg.fail(result["result"])

            # TODO: migrate
            # client.batch.configure(callback=batch_callback)

        else:
            msg.fail("Connection to Weaviate failed")

        return client

    def verify_installed_libraries(self) -> None:
        """
        Checks which libraries are installed and fills out the self.installed_libraries dictionary for the frontend to access, this will be displayed in the status page.
        """
        try:
            import PyPDF2

            self.installed_libraries["PyPDF2"] = True
        except Exception:
            self.installed_libraries["PyPDF2"] = False

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
            import cohere

            self.installed_libraries["cohere"] = True
        except Exception:
            self.installed_libraries["cohere"] = False

        try:
            import huggingface_hub
            from huggingface_hub import login

            login(token=os.environ.get("HF_TOKEN", ""), add_to_git_credential=True)

            self.installed_libraries["huggingface_hub"] = True
        except Exception:
            self.installed_libraries["huggingface_hub"] = False

        try:
            import transformers

            self.installed_libraries["transformers"] = True
        except Exception:
            self.installed_libraries["transformers"] = False

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

        # HuggingFace Key
        if os.environ.get("HF_TOKEN", "") != "":
            self.environment_variables["HF_TOKEN"] = True
        else:
            self.environment_variables["HF_TOKEN"] = False

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

        # LLAMA2-7B-CHAT-HF
        if os.environ.get("LLAMA2-7B-CHAT-HF", "") == "True":
            self.environment_variables["LLAMA2-7B-CHAT-HF"] = True
        else:
            self.environment_variables["LLAMA2-7B-CHAT-HF"] = False

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
        schema_info = self.client.collections.list_all()
        schemas: dict[str, int] = {}

        for _, classconfig in schema_info.items():

            count = (
                self.client.collections.get(classconfig.name)
                .aggregate.over_all(total_count=True)
                .total_count
            )

            if count is None:
                count = 0

            schemas[classconfig.name] = count

        return schemas

    def get_suggestions(self, query: str) -> list[str]:
        """Retrieve suggestions based on user query
        @parameter query : str - User query
        @returns list[str] - List of possible autocomplete suggestions.
        """

        query_results = self.client.collections.get("Suggestion").query.bm25(
            query=query, limit=3, return_properties=SuggestionType
        )

        results = [
            result.properties.get("suggestion") for result in query_results.objects
        ]

        if not results:
            return []

        return results

    def set_suggestions(self, query: str):
        """Adds suggestions to the suggestion class
        @parameter query : str - Query to save in suggestions.
        """
        # Don't set new suggestions when in production
        production_key = os.environ.get("VERBA_PRODUCTION", "")
        if production_key == "True":
            return

        suggestions_collection = self.client.collections.get("Suggestion")

        check_results = suggestions_collection.query.fetch_objects(
            filters=Filter.by_property("suggestion").equal(query), limit=1
        )
        if (len(check_results.objects) > 0) and (
            query == check_results.objects[0].properties.get("suggestion")
        ):
            return
        vectors = {
            vectorizer.name: [0.0]
            # else chunk.vector
            for vectorizer in VECTORIZERS
            if vectorizer.name
            != self.embedder_manager.selected_embedder.vectorizer.name
        }
        suggestions_collection.data.insert(
            properties={"suggestion": query}, vector=vectors
        )

        msg.info("Added query to suggestions")

    def retrieve_chunks(self, queries: list[str]) -> list[Chunk]:
        chunks, context = self.retriever_manager.retrieve(
            queries,
            self.client,
            self.embedder_manager.selected_embedder,
            self.generator_manager.selected_generator,
        )
        return chunks, context

    def retrieve_all_documents(self, doc_type: str) -> List[Object[DocumentType, None]]:
        """Return all documents from Weaviate
        @returns list - Document list.
        """

        documents_collection = self.client.collections.get("Document")

        vectorizer = self.embedder_manager.selected_embedder.vectorizer

        if doc_type == "":
            query_results = documents_collection.query.fetch_objects(
                filters=Filter.by_property("doc_type").equal(doc_type),
                limit=10000,
                return_properties=DocumentType,
                # target_vector=vectorizer.name,
            )
        else:
            query_results = documents_collection.query.fetch_objects(
                filters=Filter.by_property("doc_type").equal(doc_type),
                limit=10000,
                return_properties=DocumentType,
                # target_vector=vectorizer.name,
            )

        results = query_results.objects
        return results

    def retrieve_document(self, doc_id: str) -> dict:
        """Return a document by it's ID (UUID format) from Weaviate
        @parameter doc_id : str - Document ID
        @returns dict - Document dict.
        """

        documents_class = self.client.collections.get("Document")
        document = documents_class.query.fetch_object_by_id(doc_id)

        return_dict = {}

        for key, value in document.properties.items():
            return_dict[key] = value
        return return_dict

    async def generate_answer(
        self, queries: list[str], contexts: list[str], conversation: dict
    ):
        semantic_query = self.embedder_manager.selected_embedder.conversation_to_query(
            queries, conversation
        )
        (
            semantic_result,
            distance,
        ) = self.embedder_manager.selected_embedder.retrieve_semantic_cache(
            self.client, semantic_query
        )

        if semantic_result is not None:
            return {
                "message": str(semantic_result),
                "finish_reason": "stop",
                "cached": True,
                "distance": distance,
            }

        else:
            full_text = await self.generator_manager.selected_generator.generate(
                queries, contexts, conversation
            )
            self.embedder_manager.selected_embedder.add_to_semantic_cache(
                self.client, semantic_query, full_text
            )
            self.set_suggestions(" ".join(queries))
            return full_text

    async def generate_stream_answer(
        self, queries: list[str], contexts: list[str], conversation: dict
    ):
        semantic_query = self.embedder_manager.selected_embedder.conversation_to_query(
            queries, conversation
        )
        (
            semantic_result,
            distance,
        ) = self.embedder_manager.selected_embedder.retrieve_semantic_cache(
            self.client, semantic_query
        )

        if semantic_result is not None:
            yield {
                "message": str(semantic_result),
                "finish_reason": "stop",
                "cached": True,
                "distance": distance,
            }

        else:
            full_text = ""
            async for (
                result
            ) in self.generator_manager.selected_generator.generate_stream(
                queries, contexts, conversation
            ):
                full_text += result["message"]
                yield result
            self.set_suggestions(" ".join(queries))
            self.embedder_manager.selected_embedder.add_to_semantic_cache(
                self.client, semantic_query, full_text
            )

    def reset(self):
        self.client.collections._delete("Suggestion")
        # Check if all schemas exist for all possible vectorizers

        schema_manager.reset_schemas(self.client)

        schema_manager.init_schemas(self.client, False, True)

        schema_manager.init_schemas(self.client, False, True)

    def reset_cache(self):

        self.client.collections._delete("Cache")

        schema_manager.init_schemas(self.client, vectorizer, False, True)

    def reset_suggestion(self):
        self.client.collections._delete("Suggestion")
        schema_manager.init_suggestion(self.client, "", False, True)

    def check_if_document_exists(self, document: Document) -> bool:
        """Return a document by it's ID (UUID format) from Weaviate
        @parameter document : Document - Document object
        @returns bool - Whether the doc name exist in the cluster.
        """

        vectorizer = self.embedder_manager.selected_embedder.vectorizer

        results = self.client.collections.get("Document").query.fetch_objects(
            filters=Filter.by_property("doc_name").equal(document.name),
            limit=1,
            return_properties=DocumentType,
            # target_vector=vectorizer.name,
        )

        if len(results.objects) > 0:
            msg.warn(f"{document.name} already exists")
            return True
        else:
            return False

    def check_verba_component(self, component: VerbaComponent) -> tuple[bool, str]:
        for library in component.requires_library:
            if library in self.installed_libraries:
                if not self.installed_libraries[library]:
                    return (False, f"{library} not installed")
            else:
                return (False, f"{library} not installed")

        for env in component.requires_env:
            if env in self.environment_variables:
                if not self.environment_variables[env]:
                    return (False, f"{env} not set")
            else:
                return (False, f"{env} not set")

        return (True, "Available")

    def delete_document_by_id(self, doc_id: str) -> None:
        self.embedder_manager.selected_embedder.remove_document_by_id(
            self.client, doc_id
        )

    def search_documents(self, query: str, doc_type: str) -> list:
        return self.embedder_manager.selected_embedder.search_documents(
            self.client, query, doc_type
        )
