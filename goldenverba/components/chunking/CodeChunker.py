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
            "Chunk Size": InputConfig(
                type="number",
                value=500,
                description="Choose how many characters per chunk",
                values=[],
            ),
            "Chunk Overlap": InputConfig(
                type="number",
                value=50,
                description="Choose how many characters overlap between chunks",
                values=[],
            ),
        }

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:

        language = config["Language"].value
        chunk_size = config["Chunk Size"].value
        chunk_overlap = config["Chunk Overlap"].value

        text_splitter = RecursiveCharacterTextSplitter.from_language(language=language, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        for document in documents:

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue
            
            char_end_i = -1
            for i, chunk in enumerate(text_splitter.split_text(document.content)):
                
                if chunk_overlap == 0:
                    char_start_i = char_end_i + 1
                    char_end_i = char_start_i + len(chunk)
                else:
                    # not implemented, requires complex calculations as to whether the overlap contained a 'good' chunk
                    char_start_i = None
                    char_end_i = None

                document.chunks.append(
                    Chunk(
                        content=chunk,
                        chunk_id=i,
                        start_i=char_start_i,
                        end_i=char_end_i,
                        content_without_overlap=chunk,
                    )
                )

        return documents
