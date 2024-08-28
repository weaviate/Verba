import contextlib

with contextlib.suppress(Exception):
    from langchain_text_splitters import (
        Language,
        RecursiveCharacterTextSplitter,
    )

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding


class CodeChunker(Chunker):
    """
    CodeChunker for Verba using LangChain.
    """

    def __init__(self):
        super().__init__()
        self.name = "Code"
        self.requires_library = ["langchain_text_splitters "]
        self.description = "Split code based on programming language using LangChain"
        self.config = {
            "Language": InputConfig(
                type="dropdown",
                value="python",
                description="Select programming language",
                values=[e.value for e in Language],
            ),
        }

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:

        Language = config["Language"].value

        text_splitter = RecursiveCharacterTextSplitter.from_language(language=Language)

        for document in documents:

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            for i, chunk in enumerate(text_splitter.split_text(document.content)):

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
