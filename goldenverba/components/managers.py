from wasabi import msg
import weaviate
import re
from weaviate.client import WeaviateClient
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import Filter, Sort
from weaviate.collections.classes.data import DataObject
import os
import asyncio
import json

from goldenverba.components.document import Document
from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import (
    Reader,
    Chunker,
    Embedder,
    Embedding,
    Retriever,
    Generator,
)
from goldenverba.server.ImportLogger import LoggerManager
from goldenverba.server.types import FileConfig, FileStatus

from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.reader.GitReader import GitHubReader
from goldenverba.components.reader.LabReader import GitLabReader
from goldenverba.components.reader.UnstructuredAPI import UnstructuredReader

from goldenverba.components.chunking.TokenChunker import TokenChunker
from goldenverba.components.embedding.OpenAIEmbedder import OpenAIEmbedder
from goldenverba.components.embedding.CohereEmbedder import CohereEmbedder
from goldenverba.components.embedding.GoogleEmbedder import GoogleEmbedder
from goldenverba.components.embedding.OllamaEmbedder import OllamaEmbedder
from goldenverba.components.embedding.SentenceTransformersEmbedder import SentenceTransformersEmbedder

from goldenverba.components.retriever.WindowRetriever import WindowRetriever

from goldenverba.components.generation.GeminiGenerator import GeminiGenerator
from goldenverba.components.generation.CohereGenerator import CohereGenerator
from goldenverba.components.generation.GPT3Generator import GPT3Generator
from goldenverba.components.generation.GPT4Generator import GPT4Generator
from goldenverba.components.generation.OllamaGenerator import OllamaGenerator

import time

try:
    import tiktoken
except Exception:
    msg.warn("tiktoken not installed, your base installation might be corrupted.")

### Add new components here ###

readers = [BasicReader(), GitHubReader(), GitLabReader(), UnstructuredReader()]
chunkers = [TokenChunker()]
embedders = [OpenAIEmbedder(), SentenceTransformersEmbedder(), CohereEmbedder(), OllamaEmbedder(), GoogleEmbedder()]

### ----------------------- ###

class ReaderManager:
    def __init__(self):
        self.readers: dict[str, Reader] = { reader.name : reader for reader in readers }

    async def load(
        self, reader: str, fileConfig: FileConfig,  logger: LoggerManager
    ) -> list[Document]:
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 
            if reader in self.readers:
                config = fileConfig.rag_config["Reader"].components[reader]
                document : Document = await self.readers[reader].load(fileConfig)
                document.meta["Reader"] = config.model_dump_json()
                elapsed_time = round(loop.time() - start_time, 2)
                await logger.send_report(fileConfig.fileID, FileStatus.LOADING, f"Loaded {fileConfig.filename}", took=elapsed_time)
                await logger.send_report(fileConfig.fileID, FileStatus.CHUNKING, "", took=0)
                return document
            else:
                raise Exception(f"{reader} Reader not found")

        except Exception as e:
            raise e

class ChunkerManager:
    def __init__(self):
        self.chunkers: dict[str, Chunker] = { chunker.name : chunker for chunker in chunkers }

    async def chunk(self, chunker: str, fileConfig: FileConfig, document: Document, logger: LoggerManager) -> Document:
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 
            if chunker in self.chunkers:
                config = fileConfig.rag_config["Chunker"].components[chunker].config
                chunked_document = await self.chunkers[chunker].chunk(config, document)
                chunked_document.meta["Chunker"] = fileConfig.rag_config["Chunker"].components[chunker].model_dump_json()
                elapsed_time = round(loop.time() - start_time, 2)
                await logger.send_report(fileConfig.fileID, FileStatus.CHUNKING, f"Split {fileConfig.filename} into {len(document.chunks)} chunks", took=elapsed_time)
                await logger.send_report(fileConfig.fileID, FileStatus.EMBEDDING, "", took=0)
                return chunked_document
            else:
                raise Exception(f"{chunker} Chunker not found")
        except Exception as e:
            raise e

class EmbeddingManager:
    def __init__(self):
        self.embedders: dict[str, Embedding] = { embedder.name : embedder for embedder in embedders }

    async def vectorize(
        self,
        embedder: str,
        fileConfig: FileConfig,
        document: Document,
        logger: LoggerManager
    ) -> Document:
        """Vectorizes chunks
        @parameter: documents : Document - Verba document
        @returns Document - Document with vectorized chunks
        """
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 
            if embedder in self.embedders:
                config = fileConfig.rag_config["Embedder"].components[embedder].config
                content = [chunk.content for chunk in document.chunks]
                embeddings = await self.embedders[embedder].vectorize(config, content)
                for vector, chunk in zip(embeddings,document.chunks):
                    chunk.vector = vector
                document.meta["Embedder"] = fileConfig.rag_config["Embedder"].components[embedder].model_dump_json()
                elapsed_time = round(loop.time() - start_time, 2)
                await logger.send_report(fileConfig.fileID, FileStatus.EMBEDDING, f"Vectorized all chunks", took=elapsed_time)
                await logger.send_report(fileConfig.fileID, FileStatus.INGESTING, "", took=0)
                return document
            else:
                raise Exception(f"{embedder} Embedder not found")
        except Exception as e:
            raise e

class RetrieverManager:
    def __init__(self):
        self.retrievers: dict[str, Retriever] = {
            "WindowRetriever": WindowRetriever(),
        }
        self.selected_retriever: str = "WindowRetriever"

    def retrieve(
        self,
        queries: list[str],
        client,
        embedder: Embedder,
        generator: Generator,
    ) -> list[Chunk]:
        """Ingest data into Weaviate
        @parameter: queries : list[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns list[Chunk] - List of retrieved chunks.
        """
        chunks, context = self.retrievers[self.selected_retriever].retrieve(
            queries, client, embedder
        )
        managed_context = self.retrievers[self.selected_retriever].cutoff_text(
            context, generator.context_window
        )
        return chunks, managed_context

    def set_retriever(self, retriever: str) -> bool:
        if retriever in self.retrievers:
            msg.info(f"Setting RETRIEVER to {retriever}")
            self.selected_retriever = retriever
            return True
        else:
            msg.warn(f"Retriever {retriever} not found")
            return False

    def get_retrievers(self) -> dict[str, Retriever]:
        return self.retrievers

class GeneratorManager:
    def __init__(self):
        self.generators: dict[str, Generator] = {
            "Gemini": GeminiGenerator(),
            "GPT4-O": GPT4Generator(),
            "GPT3": GPT3Generator(),
            "Ollama": OllamaGenerator(),
            "Command R+": CohereGenerator(),
        }
        self.selected_generator: str = "GPT3"

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = None,
    ):
        """Generate a stream of response dicts based on a list of queries and list of contexts, and includes conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns Iterator[dict] - Token response generated by the Generator in this format {system:TOKEN, finish_reason:stop or empty}.
        """
        if conversation is None:
            conversation = {}
        async for result in self.generators[self.selected_generator].generate_stream(
            queries,
            context,
            self.truncate_conversation_dicts(
                conversation,
                int(self.generators[self.selected_generator].context_window * 0.375),
            ),
        ):
            yield result

    def truncate_conversation_dicts(
        self, conversation_dicts: list[dict[str, any]], max_tokens: int
    ) -> list[dict[str, any]]:
        """
        Truncate a list of conversation dictionaries to fit within a specified maximum token limit.

        @parameter conversation_dicts: List[Dict[str, any]] - A list of conversation dictionaries that may contain various keys, where 'content' key is present and contains text data.
        @parameter max_tokens: int - The maximum number of tokens that the combined content of the truncated conversation dictionaries should not exceed.

        @returns List[Dict[str, any]]: A list of conversation dictionaries that have been truncated so that their combined content respects the max_tokens limit. The list is returned in the original order of conversation with the most recent conversation being truncated last if necessary.

        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        accumulated_tokens = 0
        truncated_conversation_dicts = []

        # Start with the newest conversations
        for item_dict in reversed(conversation_dicts):
            item_tokens = encoding.encode(item_dict["content"], disallowed_special=())

            # If adding the entire new item exceeds the max tokens
            if accumulated_tokens + len(item_tokens) > max_tokens:
                # Calculate how many tokens we can add from this item
                remaining_space = max_tokens - accumulated_tokens
                truncated_content = encoding.decode(item_tokens[:remaining_space])

                # Create a new truncated item dictionary
                truncated_item_dict = {
                    "type": item_dict["type"],
                    "content": truncated_content,
                    "typewriter": item_dict["typewriter"],
                }

                truncated_conversation_dicts.append(truncated_item_dict)
                break

            truncated_conversation_dicts.append(item_dict)
            accumulated_tokens += len(item_tokens)

        # The list has been built in reverse order so we reverse it again
        return list(reversed(truncated_conversation_dicts))

    def set_generator(self, generator: str) -> bool:
        if generator in self.generators:
            msg.info(f"Setting GENERATOR to {generator}")
            self.selected_generator = generator
            return True
        else:
            msg.warn(f"Generator {generator} not found")
            return False

    def get_generators(self) -> dict[str, Generator]:
        return self.generators

class WeaviateManager:
    def __init__(self):
        self.client : WeaviateClient = None
        self.document_collection_name = "VERBA_DOCUMENTS"
        self.config_collection_name = "VERBA_CONFIG"
        self.suggestion_collection_name = "VERBA_SUGGESTION"
        self.embedding_table = {}

    ### Connection Handling

    def connect_to_cluster(self, w_url, w_key):
        if w_url is not None and w_key is not None:
            msg.info(f"Connecting to Weaviate Cluster {w_url} with Auth")
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=w_url,
                auth_credentials=AuthApiKey(w_key),
            )
        elif w_url is not None and w_key is None:
            msg.info(f"Connecting to Weaviate Cluster {w_url} without Auth")
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=w_url,
            )

    def connect_to_docker(self):
        msg.info(f"Connecting to Weaviate Docker")
        self.client = weaviate.connect_to_local()

    def connect_to_embedded(self):
        msg.info(f"Connecting to Weaviate Embedded")
        self.client = weaviate.connect_to_embedded()

    def connect(self):
        try:
            weaviate_url = os.environ.get("WEAVIATE_URL_VERBA", None)
            weaviate_key = os.environ.get("WEAVIATE_API_KEY_VERBA", None)

            if weaviate_url is not None and weaviate_key is not None:
                self.connect_to_cluster(weaviate_url, weaviate_key)
            else:
                self.connect_to_embedded()
        
            if self.client is not None and self.client.is_ready():
                msg.good("Succesfully Connected to Weaviate")

        except Exception as e:
            msg.fail(f"Couldn't connect to Weaviate, check your URL/API KEY: {str(e)}")

    ### Collection Handling

    def verify_collection(self, collection_name: str):
        if not self.client.collections.exists(collection_name):
            msg.info(f"Collection: {collection_name} does not exist, creating new collection.")
            self.client.collections.create(
                name=collection_name
            )
        else:
            document_collection = self.client.collections.get(collection_name)
            response = document_collection.aggregate.over_all(total_count=True)
            if response.total_count > 0:
                msg.info(f"Collection: {collection_name} exists with {response.total_count} objects stored")

    def verify_embedding_collections(self, environment_variables, libraries):
        for embedder in embedders:
            if embedder.check_available(environment_variables,libraries):
                if "Model" in embedder.config:
                    for _embedder in embedder.config["Model"].values:
                        self.embedding_table[_embedder] = "VERBA_Embedding_"+re.sub(r"[^a-zA-Z0-9]", "_", _embedder)
                        self.verify_collection(self.embedding_table[_embedder])

    def verify_collections(self, environment_variables, libraries):
        self.verify_collection(self.document_collection_name)
        self.verify_collection(self.suggestion_collection_name)
        self.verify_collection(self.config_collection_name)
        self.verify_embedding_collections(environment_variables, libraries)

    ### Configuration Handling

    def get_config(self, uuid: str) -> dict:
        config_collection = self.client.collections.get(self.config_collection_name)
        if config_collection.data.exists(uuid):
            config = config_collection.query.fetch_object_by_id(uuid)
            return json.loads(config.properties["config"])
        else:
            return None
        
    def set_config(self, uuid: str, config: dict):
        config_collection = self.client.collections.get(self.config_collection_name)
        if config_collection.data.exists(uuid):
            config_collection.data.delete_by_id(uuid)
        config_collection.data.insert(properties={"config":json.dumps(config)}, uuid=uuid)

    def reset_config(self, uuid: str):
        config_collection = self.client.collections.get(self.config_collection_name)
        if config_collection.data.exists(uuid):
            config_collection.data.delete_by_id(uuid)

    ### Import Handling
            
    async def import_document(self, document: Document, embedder: str):
        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        document_collection = self.client.collections.get(self.document_collection_name)
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])

        ### Import Document
        document_obj = Document.to_json(document)
        doc_uuid = document_collection.data.insert(document_obj)

        chunk_ids = []

        try:
            ### Batch Import Of Chunks
            with embedder_collection.batch.dynamic() as batch:
                for chunk in document.chunks:
                    chunk.doc_uuid = doc_uuid
                    chunk_obj = Chunk.to_dict(chunk)
                    chunk_ids.append(batch.add_object(properties=chunk_obj, vector=chunk.vector))

            #chunk_response = await embedder_collection.data.insert_many([DataObject(properties=chunk.to_dict(), vector=chunk.vector) for chunk in document.chunks])

        except Exception as e:
            msg.warn(f"Import of Chunks failed: {str(e)}")

        response = embedder_collection.aggregate.over_all(filters=Filter.by_property("doc_uuid").equal(doc_uuid), total_count=True)
        if response.total_count != len(document.chunks):
            document_collection.data.delete_by_id(doc_uuid)
            for _id in chunk_ids:
                embedder_collection.data.delete_by_id(_id)
            raise Exception(f"Chunk Mismatch detected after importing: Imported:{response.total_count} | Existing: {len(document.chunks)}")
    
    ### Document CRUD
        
    async def exist_document_name(self, name: str) -> str:
        if len(self.client.collections.get(self.document_collection_name).query.fetch_objects(filters=Filter.by_property("title").equal(name)).objects) > 0:
            return self.client.collections.get(self.document_collection_name).query.fetch_objects(filters=Filter.by_property("title").equal(name)).objects[0].uuid
        else:
            return None
        
    async def delete_document(self, uuid: str):
        if not self.client.collections.get(self.document_collection_name).data.exists(uuid):
            return

        document_obj =  self.client.collections.get(self.document_collection_name).query.fetch_object_by_id(uuid)
        embedding_config = json.loads(document_obj.properties.get("meta")["Embedder"])
        embedder = embedding_config["config"]["Model"]["value"]

        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")

        self.client.collections.get(self.document_collection_name).data.delete_by_id(uuid)
        for chunk in self.client.collections.get(self.embedding_table[embedder]).query.fetch_objects(filters=Filter.by_property("doc_uuid").equal(uuid)).objects:
            self.client.collections.get(self.embedding_table[embedder]).data.delete_by_id(chunk.uuid)

    async def get_documents(self, query: str, pageSize: int, page: int) -> list[dict]:
        offset = pageSize * (page - 1)
        document_collection = self.client.collections.get(self.document_collection_name)

        if query == "":
            response = document_collection.query.fetch_objects(limit=pageSize, offset=offset, sort=Sort.by_property("title", ascending=True))
        else:
            response = document_collection.query.bm25(query=query, limit=pageSize, offset=offset)

        return [{"title":doc.properties["title"], "uuid":str(doc.uuid), "labels":doc.properties["labels"]} for doc in response.objects]





        




