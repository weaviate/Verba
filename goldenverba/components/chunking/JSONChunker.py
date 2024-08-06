import contextlib

from wasabi import msg
import json

with contextlib.suppress(Exception):
    from langchain_text_splitters import (
        RecursiveJsonSplitter,
    )

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding


class JSONChunker(Chunker):
    """
    JSONChunker for Verba using LangChain.
    """

    def __init__(self):
        super().__init__()
        self.name = "JSON"
        self.requires_library = ["langchain_text_splitters "]
        self.description = "Split json files using LangChain"
        self.config = {
            "Chunk Size": InputConfig(
                type="number",
                value=500,
                description="Choose how many characters per chunks",
                values=[],
            ),
        }

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding,
        embedder_config: dict,
    ) -> list[Document]:

        units = int(config["Chunk Size"].value)

        text_splitter = RecursiveJsonSplitter(max_chunk_size=units)

        for document in documents:

            json_obj = json.loads(document.content)

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            for i, chunk in enumerate(text_splitter.split_text(json_obj)):

                document.chunks.append(
                    Chunk(
                        content=chunk,
                        chunk_id=i,
                        start_i=0,
                        end_i=0,
                        content_without_overlap=chunk,
                    )
                )

        return documents
