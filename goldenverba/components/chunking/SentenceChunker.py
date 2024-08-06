import contextlib

from wasabi import msg

with contextlib.suppress(Exception):
    import tiktoken

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding


class SentenceChunker(Chunker):
    """
    SentenceChunker for Verba built with spacy.
    """

    def __init__(self):
        super().__init__()
        self.name = "Sentence"
        self.description = "Splits documents based on word tokens"
        self.config = {
            "Sentences": InputConfig(
                type="number",
                value=5,
                description="Choose how many Sentences per chunks",
                values=[],
            ),
            "Overlap": InputConfig(
                type="number",
                value=1,
                description="Choose how many Sentences should overlap between chunks",
                values=[],
            ),
        }

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding,
        embedder_config: dict,
    ) -> list[Document]:

        units = int(config["Sentences"].value)
        overlap = int(config["Overlap"].value)

        for document in documents:

            doc = document.spacy_doc

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            sentences = [sent.text for sent in doc.sents]

            # If Split Size is higher than actual Token Count or if Split Size is Zero
            if units > len(sentences) or units == 0:
                document.chunks.append(
                    Chunk(
                        content=document.content,
                        chunk_id=0,
                        start_i=0,
                        end_i=len(doc),
                        content_without_overlap=document.content,
                    )
                )

            if overlap >= units:
                msg.warn(
                    f"Overlap value is greater than unit (Units {config['Sentences'].value}/ Overlap {config['Overlap'].value})"
                )
                overlap = units - 1

            i = 0
            split_id_counter = 0
            while i < len(sentences):
                start_i = i
                end_i = min(i + units, len(sentences))
                overlap_start = max(0, end_i - overlap)

                chunk_text = "".join(sentences[start_i:end_i])
                chunk_text_without_overlap = "".join(sentences[start_i:overlap_start])

                doc_chunk = Chunk(
                    content=chunk_text,
                    chunk_id=split_id_counter,
                    start_i=start_i,
                    end_i=end_i,
                    content_without_overlap=chunk_text_without_overlap,
                )

                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(doc):
                    break

                i += units - overlap  # Step forward, considering overlap

        return documents
