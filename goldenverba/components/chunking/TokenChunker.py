import contextlib

from tqdm import tqdm
from wasabi import msg

with contextlib.suppress(Exception):
    import tiktoken

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document


class TokenChunker(Chunker):
    """
    TokenChunker for Verba built with tiktoken.
    """

    def __init__(self):
        super().__init__()
        self.name = "TokenChunker"
        self.requires_library = ["tiktoken"]
        self.description = "Chunks documents by word tokens. Choose between the chunk size and their overlap."
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def chunk(self, documents: list[Document], logging: list[dict]) -> list[Document]:

        for document in tqdm(
            documents, total=len(documents), desc="Chunking documents"
        ):
            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            encoded_tokens = self.encoding.encode(document.text, disallowed_special=())

            if (
                self.config["units"].value > len(encoded_tokens)
                or self.config["units"].value < 1
            ):
                doc_chunk = Chunk(
                    text=document.text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=0,
                )

            if self.config["overlap"].value >= self.config["units"].value:
                msg.warn(
                    f"Overlap value is greater than unit (Units {self.config['units'].value}/ Overlap {self.config['overlap'].value})"
                )
                logging.append(
                    {
                        "type": "ERROR",
                        "message": f"Overlap value is greater than unit (Units {self.config['units'].value}/ Overlap {self.config['overlap'].value})",
                    }
                )
                self.config["overlap"].value = self.config["units"].value - 1

            i = 0
            split_id_counter = 0
            while i < len(encoded_tokens):
                # Overlap
                start_i = i
                end_i = min(i + self.config["units"].value, len(encoded_tokens))

                chunk_tokens = encoded_tokens[start_i:end_i]
                chunk_text = self.encoding.decode(chunk_tokens)

                doc_chunk = Chunk(
                    text=chunk_text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=split_id_counter,
                )
                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(encoded_tokens):
                    break

                i += (
                    self.config["units"].value - self.config["overlap"].value
                )  # Step forward, considering overlap

        return documents, logging
