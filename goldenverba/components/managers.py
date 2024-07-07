from wasabi import msg
from weaviate import Client

from goldenverba.components.document import Document
from goldenverba.components.chunk import Chunk
from goldenverba.components.types import FileData
from goldenverba.components.interfaces import (
    Reader,
    Chunker,
    Embedder,
    Retriever,
    Generator,
)

from goldenverba.components.reader.BasicReader import BasicReader
from goldenverba.components.reader.GitReader import GitHubReader
from goldenverba.components.reader.GitLabReader import GitLabReader
from goldenverba.components.reader.UnstructuredAPI import UnstructuredReader

from goldenverba.components.chunking.TokenChunker import TokenChunker

from goldenverba.components.embedding.ADAEmbedder import ADAEmbedder
from goldenverba.components.embedding.CohereEmbedder import CohereEmbedder
from goldenverba.components.embedding.MiniLMEmbedder import MiniLMEmbedder
from goldenverba.components.embedding.GoogleEmbedder import GoogleEmbedder
from goldenverba.components.embedding.OllamaEmbedder import OllamaEmbedder
from goldenverba.components.embedding.AllMPNetEmbedder import AllMPNetEmbedder
from goldenverba.components.embedding.MixedbreadEmbedder import MixedbreadEmbedder

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


class ReaderManager:
    def __init__(self):
        self.readers: dict[str, Reader] = {
            "BasicReader": BasicReader(),
            "GitHubReader": GitHubReader(),
            "GitLabReader": GitLabReader(),
            "UnstructuredAPI": UnstructuredReader(),
        }
        self.selected_reader: str = "BasicReader"

    def load(
        self, fileData: list[FileData], textValues: list[str], logging: list[dict]
    ) -> tuple[list[Document], list[str]]:

        start_time = time.time()  # Start timing

        if len(fileData) > 0:
            logging.append(
                {
                    "type": "INFO",
                    "message": f"Importing {len(fileData)} files with {self.selected_reader}",
                }
            )
        else:
            logging.append(
                {
                    "type": "INFO",
                    "message": f"Importing {textValues} with {self.selected_reader}",
                }
            )

        documents, logging = self.readers[self.selected_reader].load(
            fileData, textValues, logging
        )

        elapsed_time = round(time.time() - start_time, 2)  # Calculate elapsed time

        msg.good(f"Loaded {len(documents)} documents in {elapsed_time}s")
        logging.append(
            {
                "type": "SUCCESS",
                "message": f"Loaded {len(documents)} documents in {elapsed_time}s",
            }
        )

        return documents, logging

    def set_reader(self, reader: str):
        if reader in self.readers:
            msg.info(f"Setting READER to {reader}")
            self.selected_reader = reader
        else:
            msg.warn(f"Reader {reader} not found")

    def get_readers(self) -> dict[str, Reader]:
        return self.readers


class ChunkerManager:
    def __init__(self):
        self.chunker: dict[str, Chunker] = {
            "TokenChunker": TokenChunker(),
        }
        self.selected_chunker: str = "TokenChunker"

    def chunk(self, documents: list[Document], logging: list[dict]) -> list[Document]:
        logging.append(
            {
                "type": "INFO",
                "message": f"Starting Chunking with {self.selected_chunker}",
            }
        )
        start_time = time.time()  # Start timing
        chunked_docs, logging = self.chunker[self.selected_chunker].chunk(
            documents, logging
        )
        if self.check_chunks(chunked_docs):
            elapsed_time = round(time.time() - start_time, 2)  # Calculate elapsed time
            msg.good(
                f"Chunking completed with {sum([len(document.chunks) for document in chunked_docs])} chunks in {elapsed_time}s"
            )
            logging.append(
                {
                    "type": "SUCCESS",
                    "message": f"Chunking completed with {sum([len(document.chunks) for document in chunked_docs])} chunks in {elapsed_time}s",
                }
            )
            return chunked_docs, logging
        return []

    def set_chunker(self, chunker: str) -> bool:
        if chunker in self.chunker:
            msg.info(f"Setting CHUNKER to {chunker}")
            self.selected_chunker = chunker
            return True
        else:
            msg.warn(f"Chunker {chunker} not found")
            return False

    def get_chunkers(self) -> dict[str, Chunker]:
        return self.chunker

    def check_chunks(self, documents: list[Document]) -> bool:
        """Checks token count of chunks which are hardcapped to 1000 tokens per chunk
        @parameter: documents : list[Document] - List of Verba documents
        @returns bool - Whether the chunks are within the token range.
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        for document in documents:
            chunks = document.chunks
            for chunk in chunks:
                tokens = encoding.encode(chunk.text, disallowed_special=())
                chunk.set_tokens(tokens)
                if len(tokens) > 1000:
                    raise Exception(
                        "Chunk detected with more than 1000 tokens which exceeds the maximum size. Please reduce size of your chunk."
                    )

        return True


class EmbeddingManager:
    def __init__(self):
        self.embedders: dict[str, Embedder] = {
            "GoogleEmbedder": GoogleEmbedder(),
            "MiniLMEmbedder": MiniLMEmbedder(),
            "AllMPNetEmbedder": AllMPNetEmbedder(),
            "MixedbreadEmbedder": MixedbreadEmbedder(),
            "ADAEmbedder": ADAEmbedder(),
            "CohereEmbedder": CohereEmbedder(),
            "OllamaEmbedder": OllamaEmbedder(),
        }
        self.selected_embedder: str = "ADAEmbedder"


    def embed(
        self,
        documents: list[Document],
        client: Client,
        logging: list[dict],
        batch_size: int = 100,
    ) -> bool:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        start_time = time.time()  # Start timing
        logging.append(
            {
                "type": "INFO",
                "message": f"Starting Embedding with {self.selected_embedder}",
            }
        )
        successful_embedding = self.embedders[self.selected_embedder].embed(
            documents, client, logging
        )
        elapsed_time = round(time.time() - start_time, 2)  # Calculate elapsed time
        msg.good(
            f"Embedding completed with {len(documents)} Documents and {sum([len(document.chunks) for document in documents])} chunks in {elapsed_time}s"
        )
        logging.append(
            {
                "type": "SUCCESS",
                "message": f"Embedding completed with {len(documents)} Documents and {sum([len(document.chunks) for document in documents])} chunks in {elapsed_time}s",
            }
        )
        return successful_embedding

    def set_embedder(self, embedder: str) -> bool:
        if embedder in self.embedders:
            msg.info(f"Setting EMBEDDER to {embedder}")
            self.selected_embedder = embedder
            return True
        else:
            msg.warn(f"Embedder {embedder} not found")
            return False

    def get_embedders(self) -> dict[str, Embedder]:
        return self.embedders


class RetrieverManager:
    def __init__(self):
        self.retrievers: dict[str, Retriever] = {
            "WindowRetriever": WindowRetriever(),
        }
        self.selected_retriever: str = "WindowRetriever"

    def retrieve(
        self,
        queries: list[str],
        client: Client,
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
