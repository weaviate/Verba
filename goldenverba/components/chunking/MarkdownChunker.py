import contextlib

with contextlib.suppress(Exception):
    from langchain_text_splitters import MarkdownHeaderTextSplitter
    from langchain_core.documents import Document as LangChainDocument

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.interfaces import Embedding


HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]


def get_header_values(
    split_doc: LangChainDocument,
) -> list[str]:
    """
    Get the text values of the headers in the LangChain Document resulting from a split.
    """
    # This function uses an explicit list of header keys because the LangChain Document
    # metadata is a dictionary with arbitrary entries, some of which may not be headers.
    header_keys = [header_key for _, header_key in HEADERS_TO_SPLIT_ON]

    return [
        header_value
        for header_key in header_keys
        if (header_value := split_doc.metadata.get(header_key)) is not None
    ]


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
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:

        text_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=HEADERS_TO_SPLIT_ON
        )

        char_end_i = -1
        for document in documents:

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            for i, split_doc in enumerate(text_splitter.split_text(document.content)):

                chunk_text = ""

                # Add header content to retain context and improve retrieval
                header_values = get_header_values(split_doc)
                for header_value in header_values:
                    chunk_text += header_value + "\n"

                # append page content (always there)
                chunk_text += split_doc.page_content

                char_start_i = char_end_i + 1
                char_end_i = char_start_i + len(chunk_text)

                document.chunks.append(
                    Chunk(
                        content=chunk_text,
                        chunk_id=i,
                        start_i=None,  # not implemented as text splitter augments the document
                        end_i=None,
                        content_without_overlap=chunk_text,
                    )
                )

        return documents
