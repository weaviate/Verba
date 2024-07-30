import contextlib

from wasabi import msg

with contextlib.suppress(Exception):
    import tiktoken

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding


class TokenChunker(Chunker):
    """
    TokenChunker for Verba built with spacy.
    """

    def __init__(self):
        super().__init__()
        self.name = "Token"
        self.description = "Splits documents based on word tokens"
        self.config = {
            "Tokens": InputConfig(
                type="number", value=250, description="Choose how many Token per chunks", values=[]
            ),
            "Overlap": InputConfig(
                type="number",
                value=50,
                description="Choose how many Tokens should overlap between chunks", values=[]
            )
        }

    async def chunk(self, config: dict, documents: list[Document], embedder: Embedding, embedder_config: dict) -> list[Document]:

        units = int(config["Tokens"].value)
        overlap = int(config["Overlap"].value)

        for document in documents:

            doc = document.spacy_doc

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            # If Split Size is higher than actual Token Count or if Split Size is Zero
            if (
                units > len(doc)
                or units == 0
            ):
                document.chunks.append(Chunk(
                    content=document.content,
                    chunk_id=0,
                    start_i=0,
                    end_i=len(doc),
                ))

            if overlap >= units:
                msg.warn(f"Overlap value is greater than unit (Units {config['units'].value}/ Overlap {config['overlap'].value})")
                overlap = units - 1

            i = 0
            split_id_counter = 0
            while i < len(doc):
                # Overlap
                start_i = i
                end_i = min(i + units, len(doc))

                chunk_text = doc[start_i:end_i].text

                doc_chunk = Chunk(
                    content=chunk_text,
                    chunk_id=split_id_counter,
                    start_i=start_i,
                    end_i=end_i,
                )

                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(doc):
                    break

                i += (
                    units - overlap
                )  # Step forward, considering overlap

        return documents
