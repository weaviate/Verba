import contextlib

from tqdm import tqdm
from wasabi import msg

with contextlib.suppress(Exception):
    import tiktoken

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document

from goldenverba.server.types import FileConfig
from goldenverba.server.ImportLogger import LoggerManager


class TokenChunker(Chunker):
    """
    TokenChunker for Verba built with tiktoken.
    """

    def __init__(self):
        super().__init__()
        self.name = "Token"
        self.requires_library = ["tiktoken"]
        self.description = "Splits documents based on word tokens"
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    async def chunk(self, config: dict, document: Document) -> Document:

        units = int(config["units"].value)
        overlap = int(config["overlap"].value)

        # Skip if document already contains chunks
        if len(document.chunks) > 0:
            return document

        encoded_tokens = self.encoding.encode(document.content, disallowed_special=())

        # If Split Size is higher than actual Token Count or if Split Size is Zero
        if (
            units > len(encoded_tokens)
            or units == 0
        ):
            doc_chunk = Chunk(
                content=document.text,
                chunk_id=0,
                start=0,
                end=len(encoded_tokens)-1,
                tokens=encoded_tokens,
                meta={}
            )

        if overlap >= units:
            msg.warn(f"Overlap value is greater than unit (Units {config['units'].value}/ Overlap {config['overlap'].value})")
            overlap = units - 1

        i = 0
        split_id_counter = 0
        while i < len(encoded_tokens):
            # Overlap
            start_i = i
            end_i = min(i + units, len(encoded_tokens))

            chunk_tokens = encoded_tokens[start_i:end_i]
            chunk_text = self.encoding.decode(chunk_tokens)

            doc_chunk = Chunk(
                content=chunk_text,
                chunk_id=split_id_counter,
                start=start_i,
                end=end_i,
                tokens=encoded_tokens,
                meta={}
            )

            document.chunks.append(doc_chunk)
            split_id_counter += 1

            # Exit loop if this was the last possible chunk
            if end_i == len(encoded_tokens):
                break

            i += (
                units - overlap
            )  # Step forward, considering overlap

        return document
