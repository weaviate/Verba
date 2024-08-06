import contextlib

from wasabi import msg

with contextlib.suppress(Exception):
    import langchain_text_splitters
    from langchain_text_splitters import MarkdownHeaderTextSplitter

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding


class MarkdownChunker(Chunker):
    """
    MarkdownChunker for Verba using LangChain.
    """

    def __init__(self):
        super().__init__()
        self.name = "Markdown"
        self.requires_library = ["langchain_text_splitters"]
        self.description = (
            "Split documents based on markdown formatting using LangChain"
        )

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding,
        embedder_config: dict,
    ) -> list[Document]:

        text_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )

        for document in documents:

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            for i, chunk in enumerate(text_splitter.split_text(document.content)):

                document.chunks.append(
                    Chunk(
                        content=chunk.page_content,
                        chunk_id=i,
                        start_i=0,
                        end_i=0,
                        content_without_overlap=chunk.page_content,
                    )
                )

        return documents
