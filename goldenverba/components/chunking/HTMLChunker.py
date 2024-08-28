import contextlib

with contextlib.suppress(Exception):
    from langchain_text_splitters import HTMLHeaderTextSplitter

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.interfaces import Embedding


class HTMLChunker(Chunker):
    """
    HTMLChunker for Verba using LangChain.
    """

    def __init__(self):
        super().__init__()
        self.name = "HTML"
        self.requires_library = ["langchain_text_splitters "]
        self.description = "Split documents based on HTML tags using LangChain"

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:

        text_splitter = HTMLHeaderTextSplitter(
            headers_to_split_on=[
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3"),
                ("h4", "Header 4"),
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
