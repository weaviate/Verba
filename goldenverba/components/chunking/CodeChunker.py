import contextlib

from wasabi import msg

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
            "Chunk Size": InputConfig(
                type="number", value=500, description="Choose how many characters per chunks", values=[]
            ),
            "Overlap": InputConfig(
                type="number",
                value=100,
                description="Choose how many characters should overlap between chunks", values=[]
            ),
            "Language": InputConfig(
                type="dropdown",
                value="python",
                description="Select programming language", values=[e.value for e in Language]
            ),
        }

    async def chunk(self, config: dict, documents: list[Document], embedder: Embedding, embedder_config: dict) -> list[Document]:

        units = int(config["Chunk Size"].value)   
        overlap = int(config["Overlap"].value)
        Language = config["Language"].value

        text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language, chunk_size=units, chunk_overlap=overlap
)

        for document in documents:

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            for i, chunk in enumerate(text_splitter.split_text(document.content)):

                document.chunks.append(Chunk(
                    content=chunk,
                    chunk_id=i,
                ))

        return documents