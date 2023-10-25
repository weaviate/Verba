from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.component import VerbaComponent
from goldenverba.components.embedding.interface import Embedder

import tiktoken

from weaviate import Client


class Retriever(VerbaComponent):
    """
    Interface for Verba Retrievers
    """

    def __init__(self):
        super().__init__()

    def retrieve(
        self,
        queries: list[str],
        client: Client,
        embedder: Embedder,
    ) -> tuple[list[Chunk], str]:
        """Ingest data into Weaviate
        @parameter: queries : list[str] - List of queries
        @parameter: client : Client - Weaviate client
        @parameter: embedder : Embedder - Current selected Embedder
        @returns tuple(list[Chunk],str) - List of retrieved chunks and the context string
        """
        raise NotImplementedError("load method must be implemented by a subclass.")

    def sort_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        return sorted(chunks, key=lambda chunk: (chunk.doc_uuid, int(chunk.chunk_id)))

    def cutoff_text(self, text: str) -> str:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        # Tokenize the input text
        encoded_tokens = encoding.encode(text, disallowed_special=())

        # Check if we need to truncate
        if len(encoded_tokens) > 2500:
            encoded_tokens = encoded_tokens[:2500]
            truncated_text = encoding.decode(encoded_tokens)
            return truncated_text
        else:
            return text
