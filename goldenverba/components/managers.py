from wasabi import msg

import weaviate
from weaviate.client import WeaviateClient
from weaviate.auth import AuthApiKey
from weaviate.classes.query import Filter, Sort, MetadataQuery
from weaviate.collections.classes.data import DataObject
from weaviate.classes.aggregate import GroupByAggregate

import os
import asyncio
import json
import re

from sklearn.decomposition import PCA

import numpy as np

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
from goldenverba.server.helpers import LoggerManager
from goldenverba.server.types import FileConfig, FileStatus

# Import Readers
from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.reader.GitReader import GitHubReader
from goldenverba.components.reader.LabReader import GitLabReader
from goldenverba.components.reader.UnstructuredAPI import UnstructuredReader
from goldenverba.components.reader.HTMLReader import HTMLReader
from goldenverba.components.reader.FirecrawlReader import FirecrawlReader

# Import Chunkers
from goldenverba.components.chunking.TokenChunker import TokenChunker
from goldenverba.components.chunking.RecursiveChunker import RecursiveChunker
from goldenverba.components.chunking.HTMLChunker import HTMLChunker
from goldenverba.components.chunking.MarkdownChunker import MarkdownChunker
from goldenverba.components.chunking.CodeChunker import CodeChunker
from goldenverba.components.chunking.JSONChunker import JSONChunker
from goldenverba.components.chunking.SemanticChunker import SemanticChunker

# Import Embedders
from goldenverba.components.embedding.OpenAIEmbedder import OpenAIEmbedder
from goldenverba.components.embedding.CohereEmbedder import CohereEmbedder
from goldenverba.components.embedding.GoogleEmbedder import GoogleEmbedder
from goldenverba.components.embedding.OllamaEmbedder import OllamaEmbedder
from goldenverba.components.embedding.SentenceTransformersEmbedder import SentenceTransformersEmbedder

# Import Retrievers
from goldenverba.components.retriever.WindowRetriever import WindowRetriever

# Import Generators
from goldenverba.components.generation.GeminiGenerator import GeminiGenerator
from goldenverba.components.generation.CohereGenerator import CohereGenerator
from goldenverba.components.generation.GPT3Generator import GPT3Generator
from goldenverba.components.generation.GPT4Generator import GPT4Generator
from goldenverba.components.generation.OllamaGenerator import OllamaGenerator

try:
    import tiktoken
except Exception:
    msg.warn("tiktoken not installed, your base installation might be corrupted.")

### Add new components here ###

readers = [BasicReader(), HTMLReader(), GitHubReader(), GitLabReader(), UnstructuredReader(), FirecrawlReader()]
chunkers = [TokenChunker(), RecursiveChunker(), SemanticChunker(), HTMLChunker(), MarkdownChunker(), CodeChunker(), JSONChunker()]
embedders = [OpenAIEmbedder(), SentenceTransformersEmbedder(),  OllamaEmbedder(), CohereEmbedder()]
retrievers = [WindowRetriever()]


### ----------------------- ###


class WeaviateManager:
    def __init__(self):
        self.client : WeaviateClient = None
        self.document_collection_name = "VERBA_DOCUMENTS"
        self.config_collection_name = "VERBA_CONFIG"
        self.suggestion_collection_name = "VERBA_SUGGESTION"
        self.embedding_table = {}

    ### Connection Handling

    async def connect_to_cluster(self, w_url, w_key):
        if w_url is not None and w_key is not None:
            msg.info(f"Connecting to Weaviate Cluster {w_url} with Auth")
            self.client = weaviate.use_async_with_weaviate_cloud(
                cluster_url=w_url,
                auth_credentials=AuthApiKey(w_key),
            )
            await self.client.connect()
        elif w_url is not None and w_key is None:
            if "localhost" in w_url:
                msg.info(f"Connecting to Local Weaviate {w_url} without Auth")
                self.client = weaviate.use_async_with_local()
                await self.client.connect()
            else:
                msg.info(f"Connecting to Weaviate Cluster {w_url} without Auth")
                self.client = weaviate.use_async_with_weaviate_cloud(cluster_url=w_url)
                await self.client.connect()

    async def connect_to_docker(self):
        msg.info(f"Connecting to Weaviate Docker")
        self.client = weaviate.use_async_with_custom()
        await self.client.connect()

    async def connect_to_embedded(self):
        msg.info(f"Connecting to Weaviate Embedded")
        #TODO Wait for update to do use_async_with_embedded
        self.client = await weaviate.connect_to_embedded()
        await self.client.connect()

    async def connect(self):
        try:
            weaviate_url = os.environ.get("WEAVIATE_URL_VERBA", None)
            weaviate_key = os.environ.get("WEAVIATE_API_KEY_VERBA", None)

            if weaviate_url is not None:
                await self.connect_to_cluster(weaviate_url, weaviate_key)
            else:
                await self.connect_to_embedded()
        
            if self.client is not None and await self.client.is_ready():
                msg.good("Succesfully Connected to Weaviate")

        except Exception as e:
            msg.fail(f"Couldn't connect to Weaviate, check your URL/API KEY: {str(e)}")

    async def disconnect(self):
        try:
            await self.client.close()
        except Exception as e:
            msg.fail(f"Couldn't disconnect Weaviate: {str(e)}")

    ### Collection Handling

    async def verify_collection(self, collection_name: str):
        if not await self.client.collections.exists(collection_name):
            msg.info(f"Collection: {collection_name} does not exist, creating new collection.")
            await self.client.collections.create(
                name=collection_name
            )
        else:
            document_collection = self.client.collections.get(collection_name)
            response = await document_collection.aggregate.over_all(total_count=True)
            if response.total_count > 0:
                msg.info(f"Collection: {collection_name} exists with {response.total_count} objects stored")

    async def verify_embedding_collections(self, environment_variables, libraries):
        for embedder in embedders:
            if embedder.check_available(environment_variables,libraries):
                if "Model" in embedder.config:
                    for _embedder in embedder.config["Model"].values:
                        self.embedding_table[_embedder] = "VERBA_Embedding_"+re.sub(r"[^a-zA-Z0-9]", "_", _embedder)
                        await self.verify_collection(self.embedding_table[_embedder])

    async def verify_collections(self, environment_variables, libraries):
        await self.verify_collection(self.document_collection_name)
        await self.verify_collection(self.suggestion_collection_name)
        await self.verify_collection(self.config_collection_name)
        await self.verify_embedding_collections(environment_variables, libraries)

    ### Configuration Handling

    async def get_config(self, uuid: str) -> dict:
        config_collection = self.client.collections.get(self.config_collection_name)
        if await config_collection.data.exists(uuid):
            config = await config_collection.query.fetch_object_by_id(uuid)
            return json.loads(config.properties["config"])
        else:
            return None
        
    async def set_config(self, uuid: str, config: dict):
        config_collection = self.client.collections.get(self.config_collection_name)
        if await config_collection.data.exists(uuid):
            if await config_collection.data.delete_by_id(uuid):
                await config_collection.data.insert(properties={"config":json.dumps(config)}, uuid=uuid)
        else:
            await config_collection.data.insert(properties={"config":json.dumps(config)}, uuid=uuid)

    async def reset_config(self, uuid: str):
        config_collection = self.client.collections.get(self.config_collection_name)
        if await config_collection.data.exists(uuid):
            await config_collection.data.delete_by_id(uuid)

    ### Import Handling
            
    async def import_document(self, document: Document, embedder: str):
        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        document_collection = self.client.collections.get(self.document_collection_name)
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])

        ### Import Document
        document_obj = Document.to_json(document)
        doc_uuid = await document_collection.data.insert(document_obj)

        chunk_ids = []

        try:
            ### Batch Import Of Chunks
            #with embedder_collection.batch.dynamic() as batch:
            #    for chunk in document.chunks:
            #        chunk.doc_uuid = doc_uuid
            #        chunk_obj = Chunk.to_dict(chunk)
            #        chunk_ids.append(batch.add_object(properties=chunk_obj, vector=chunk.vector))

            for chunk in document.chunks:
                chunk.doc_uuid = doc_uuid

            chunk_response = await embedder_collection.data.insert_many([DataObject(properties=chunk.to_json(), vector=chunk.vector) for chunk in document.chunks])
            chunk_ids = [chunk_response.uuids[uuid] for uuid in chunk_response.uuids]

            if chunk_response.has_errors:
                raise Exception(f"Failed to ingest chunks into Weaviate: {chunk_response.errors}")
            
            if doc_uuid and chunk_response:
                response = await embedder_collection.aggregate.over_all(filters=Filter.by_property("doc_uuid").equal(doc_uuid), total_count=True)
                if response.total_count != len(document.chunks):
                    await document_collection.data.delete_by_id(doc_uuid)
                    for _id in chunk_ids:
                        await embedder_collection.data.delete_by_id(_id)
                    raise Exception(f"Chunk Mismatch detected after importing: Imported:{response.total_count} | Existing: {len(document.chunks)}")

        except Exception as e:
            if doc_uuid:
                await self.delete_document(doc_uuid)
            raise Exception(f"Chunk import failed with : {str(e)}")
    
    ### Document CRUD
        
    async def exist_document_name(self, name: str) -> str:

        document_collection = self.client.collections.get(self.document_collection_name)
        aggregation = await document_collection.aggregate.over_all(total_count=True)
        
        if aggregation.total_count == 0:
            return None
        else:
            documents = await document_collection.query.fetch_objects(filters=Filter.by_property("title").equal(name))
            if len(documents.objects) > 0:
                return documents.objects[0].uuid
            
        return None

    async def delete_document(self, uuid: str):

        document_collection = self.client.collections.get(self.document_collection_name)

        if not await document_collection.data.exists(uuid):
            return

        document_obj =  await document_collection.query.fetch_object_by_id(uuid)
        embedding_config = json.loads(document_obj.properties.get("meta")["Embedder"])
        embedder = embedding_config["config"]["Model"]["value"]

        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")

        if await document_collection.data.delete_by_id(uuid):
            embedder_collection = self.client.collections.get(self.embedding_table[embedder])
            await embedder_collection.data.delete_many(where=Filter.by_property("doc_uuid").equal(uuid))

    async def delete_all_documents(self):
        document_collection = self.client.collections.get(self.document_collection_name)
        async for item in document_collection.iterator():
            await self.delete_document(item.uuid)

    async def get_documents(self, query: str, pageSize: int, page: int, labels: list[str]) -> list[dict]:
        offset = pageSize * (page - 1)
        document_collection = self.client.collections.get(self.document_collection_name)

        if len(labels) > 0:
            filter = Filter.by_property("labels").contains_all(labels)
        else:
            filter = None

        response = await document_collection.aggregate.over_all(total_count=True, filters=filter)


        if response.total_count == 0:
            return []

        if query == "":
            response = await document_collection.query.fetch_objects(limit=pageSize, offset=offset, sort=Sort.by_property("title", ascending=True), filters=filter)
        else:
            response = await document_collection.query.bm25(query=query, limit=pageSize, offset=offset, filters=filter)

        return [{"title":doc.properties["title"], "uuid":str(doc.uuid), "labels":doc.properties["labels"]} for doc in response.objects]
    
    async def get_document(self, uuid: str) -> list[dict]:
        document_collection = self.client.collections.get(self.document_collection_name)

        if await document_collection.data.exists(uuid):
            response = await document_collection.query.fetch_object_by_id(uuid)
            return response.properties
        else:
            return None

    ### Labels
        
    async def get_labels(self) -> list[str]:
        document_collection = self.client.collections.get(self.document_collection_name)
        aggregation = await document_collection.aggregate.over_all(group_by=GroupByAggregate(prop="labels"), total_count=True)
        return [aggregation_group.grouped_by.value for aggregation_group in aggregation.groups]

    ### Chunks Retrieval

    async def get_chunk(self, uuid: str, embedder: str) -> list[dict]:
        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])
        if await embedder_collection.data.exists(uuid):
            response = await embedder_collection.query.fetch_object_by_id(uuid)
            response.properties["doc_uuid"] = str(response.properties["doc_uuid"])
            return response.properties
        else:
            return None
        
    async def get_chunks(self, uuid:str, page:int, pageSize:int) -> list[dict]:

        offset = pageSize * (page - 1)

        document = await self.get_document(uuid)
        if document is None:
            return document
        
        embedding_config = json.loads(document.get("meta")["Embedder"])
        embedder = embedding_config["config"]["Model"]["value"]

        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])

        weaviate_chunks = await embedder_collection.query.fetch_objects(filters=Filter.by_property("doc_uuid").equal(uuid), limit=pageSize, offset=offset, sort=Sort.by_property("chunk_id", ascending=True))
        chunks = [obj.properties for obj in weaviate_chunks.objects]
        for chunk in chunks:
            chunk["doc_uuid"] = str(chunk["doc_uuid"])
        return chunks
    
    async def get_vectors(self, uuid:str, showAll: bool ) -> dict:

        document = await self.get_document(uuid)            
        embedding_config = json.loads(document.get("meta")["Embedder"])
        embedder = embedding_config["config"]["Model"]["value"]

        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])

        if not showAll:
            weaviate_chunks = await embedder_collection.query.fetch_objects(
                filters=Filter.by_property("doc_uuid").equal(uuid),
                limit=5000,
                sort=Sort.by_property("chunk_id", ascending=True),
                include_vector=True
            )
            dimensions = len(weaviate_chunks.objects[0].vector["default"])
    
            chunks = [
                {"vector": {"x": pca[0], "y": pca[1], "z": pca[2]},
                "uuid": str(item.uuid),
                "chunk_id": item.properties["chunk_id"]}
                for item in weaviate_chunks.objects
                if (pca := item.properties["pca"]) is not None
            ]
            return {"embedder": embedder, "dimensions":dimensions, "groups": [{"name": document["title"], "chunks": chunks}]}
        
        # Generate PCA for all embeddings
        else:
            vector_map = {}
            vector_list, vector_ids, vector_chunk_uuids, vector_chunk_ids = [], [], [], []
            dimensions = 0

            async for item in embedder_collection.iterator(include_vector=True):
                doc_uuid = item.properties["doc_uuid"]
                chunk_uuid = item.uuid
                if doc_uuid not in vector_map:
                    _document = await self.get_document(doc_uuid)
                    vector_map[doc_uuid] = {"name": _document["title"], "chunks": []}
                vector_list.append(item.vector["default"])
                dimensions = len(item.vector["default"])
                vector_ids.append(doc_uuid)
                vector_chunk_uuids.append(chunk_uuid)
                vector_chunk_ids.append(item.properties["chunk_id"])

            if len(vector_ids) > 3:
                pca = PCA(n_components=3)
                generated_pca_embeddings = pca.fit_transform(vector_list)
                pca_embeddings = [pca_.tolist() for pca_ in generated_pca_embeddings]

                for pca_embedding, _uuid, _chunk_uuid, _chunk_id in zip(pca_embeddings, vector_ids, vector_chunk_uuids, vector_chunk_ids):
                    vector_map[_uuid]["chunks"].append({
                        "vector": {"x": pca_embedding[0], "y": pca_embedding[1], "z": pca_embedding[2]},
                        "uuid": str(_chunk_uuid),
                        "chunk_id": _chunk_id
                    })

                return {"embedder": embedder, "dimensions":dimensions,  "groups": list(vector_map.values())}
            else:
                return {"embedder": embedder, "dimensions":dimensions, "groups": []}

    async def hybrid_chunks(self, embedder:str, query: str, vector: list[float], limit_mode: str, limit: int):
        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])
        if limit_mode == "Autocut":
            chunks = await embedder_collection.query.hybrid(query=query,vector=vector,auto_limit=limit, return_metadata=MetadataQuery(score=True, explain_score=False))
        else:
            chunks = await embedder_collection.query.hybrid(query=query,vector=vector,limit=limit, return_metadata=MetadataQuery(score=True, explain_score=False))

        return chunks.objects

    async def get_chunk_by_ids(self, embedder:str, doc_uuid: str, ids: list[int]):
        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])
        weaviate_chunks = await embedder_collection.query.fetch_objects(filters=(Filter.by_property("doc_uuid").equal(doc_uuid) & Filter.by_property("chunk_id").contains_any(ids) ))
        return weaviate_chunks.objects

    ### Metadata Retrieval

    async def get_datacount(self, embedder: str) -> int:
        if embedder not in self.embedding_table:
            raise Exception(f"{embedder} not found in Embedding Table")
        embedder_collection = self.client.collections.get(self.embedding_table[embedder])
        response = await embedder_collection.aggregate.over_all(group_by=GroupByAggregate(prop="doc_uuid"), total_count=True)
        return len(response.groups)




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
                config = fileConfig.rag_config["Reader"].components[reader].config
                documents : list[Document] = await self.readers[reader].load(config, fileConfig)
                for document in documents:
                    document.meta["Reader"] = fileConfig.rag_config["Reader"].components[reader].model_dump_json()
                elapsed_time = round(loop.time() - start_time, 2)
                if len(documents) == 1:
                    await logger.send_report(fileConfig.fileID, FileStatus.LOADING, f"Loaded {fileConfig.filename}", took=elapsed_time)
                else:
                    await logger.send_report(fileConfig.fileID, FileStatus.LOADING, f"Loaded {fileConfig.filename} with {len(documents)} documents", took=elapsed_time)
                await logger.send_report(fileConfig.fileID, FileStatus.CHUNKING, "", took=0)
                return documents
            else:
                raise Exception(f"{reader} Reader not found")

        except Exception as e:
            raise Exception(f"Reader {reader} failed with: {str(e)}")

class ChunkerManager:
    def __init__(self):
        self.chunkers: dict[str, Chunker] = { chunker.name : chunker for chunker in chunkers }

    async def chunk(self, chunker: str, fileConfig: FileConfig, documents: list[Document], embedder: Embedding, logger: LoggerManager) -> list[Document]:
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 
            if chunker in self.chunkers:
                config = fileConfig.rag_config["Chunker"].components[chunker].config
                embedder_config = fileConfig.rag_config["Embedder"].components[embedder.name].config
                chunked_documents = await self.chunkers[chunker].chunk(config=config, documents=documents, embedder=embedder, embedder_config=embedder_config)
                for chunked_document in chunked_documents:
                    chunked_document.meta["Chunker"] = fileConfig.rag_config["Chunker"].components[chunker].model_dump_json()
                elapsed_time = round(loop.time() - start_time, 2)
                if len(documents) == 1:
                    await logger.send_report(fileConfig.fileID, FileStatus.CHUNKING, f"Split {fileConfig.filename} into {len(chunked_documents[0].chunks)} chunks", took=elapsed_time)
                else:
                    await logger.send_report(fileConfig.fileID, FileStatus.CHUNKING, f"Chunked all {len(chunked_documents)} documents with a total of {sum([len(document.chunks) for document in chunked_documents])} chunks", took=elapsed_time)

                await logger.send_report(fileConfig.fileID, FileStatus.EMBEDDING, "", took=0)
                return chunked_documents
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
        documents: list[Document],
        logger: LoggerManager
    ) -> list[Document]:
        """Vectorizes chunks
        @parameter: documents : Document - Verba document
        @returns Document - Document with vectorized chunks
        """
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time() 
            if embedder in self.embedders:
                config = fileConfig.rag_config["Embedder"].components[embedder].config

                for document in documents:
                    content = [chunk.content for chunk in document.chunks]
                    embeddings = await self.embedders[embedder].vectorize(config, content)

                    if len(embeddings) >= 3:
                        pca = PCA(n_components=3)
                        generated_pca_embeddings = pca.fit_transform(embeddings)
                        pca_embeddings = [pca_.tolist() for pca_ in generated_pca_embeddings]
                    else:
                        pca_embeddings = [embedding[0:3] for embedding in embeddings]

                    for vector, chunk, pca_ in zip(embeddings,document.chunks, pca_embeddings):
                        chunk.vector = vector
                        chunk.pca = pca_

                    document.meta["Embedder"] = fileConfig.rag_config["Embedder"].components[embedder].model_dump_json()

                elapsed_time = round(loop.time() - start_time, 2)
                await logger.send_report(fileConfig.fileID, FileStatus.EMBEDDING, f"Vectorized all chunks", took=elapsed_time)
                await logger.send_report(fileConfig.fileID, FileStatus.INGESTING, "", took=0)
                return documents
            else:
                raise Exception(f"{embedder} Embedder not found")
        except Exception as e:
            raise e
        
    async def vectorize_query(
        self,
        embedder: str,
        content: str,
        rag_config: dict
    ) -> list[float]:
        try:
            if embedder in self.embedders:
                config = rag_config["Embedder"].components[embedder].config
                embeddings = await self.embedders[embedder].vectorize(config, [content])
                return embeddings[0]
            else:
                raise Exception(f"{embedder} Embedder not found")
        except Exception as e:
            raise e

class RetrieverManager:
    def __init__(self):
        self.retrievers: dict[str, Retriever] = { retriever.name : retriever for retriever in retrievers }

    async def retrieve(
        self,
        retriever: str,
        query: str,
        vector: list[float],
        rag_config: dict,
        weaviate_manager: WeaviateManager,
    ):
        try:
            if retriever not in self.retrievers:
                raise Exception(f"Retriever {retriever} not found")
            
            embedder_model = rag_config["Embedder"].components[rag_config["Embedder"].selected].config["Model"].value
            config = rag_config["Retriever"].components[retriever].config
            documents, context = await self.retrievers[retriever].retrieve(query, vector, config, weaviate_manager, embedder_model)
            return (documents, context)
        
        except Exception as e:
            raise e



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

    
        



       





        




