from wasabi import msg
from tqdm import tqdm

try:
    import tiktoken
except:
    pass

from goldenverba.components.chunking.interface import Chunker
from goldenverba.components.chunking.chunk import Chunk
from goldenverba.components.reader.document import Document


class TokenChunker(Chunker):
    """
    TokenChunker for Verba built with tiktoken
    """

    def __init__(self):
        super().__init__()
        self.name = "TokenChunker"
        self.requires_library = ["tiktoken"]
        self.default_units = 250
        self.default_overlap = 50
        self.description = "Chunk documents by tokens powered by tiktoken. You can specify how many tokens should overlap between chunks to improve retrieval."
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def chunk(
        self, documents: list[Document], units: int, overlap: int
    ) -> list[Document]:
        """Chunk verba documents into chunks based on units and overlap
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks
        """
        for document in tqdm(
            documents, total=len(documents), desc="Chunking documents"
        ):
            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            encoded_tokens = self.encoding.encode(document.text, disallowed_special=())

            if units > len(encoded_tokens) or units < 1:
                doc_chunk = Chunk(
                    text=document.text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=0,
                )

            if overlap >= units:
                msg.warn(
                    f"Overlap value is greater than unit (Units {units}/ Overlap {overlap})"
                )
                continue

            i = 0
            split_id_counter = 0
            while i < len(encoded_tokens):
                # Overlap
                start_i = i
                end_i = min(i + units, len(encoded_tokens))

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

                i += units - overlap  # Step forward, considering overlap

        return documents
