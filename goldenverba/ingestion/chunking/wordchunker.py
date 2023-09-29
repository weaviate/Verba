from wasabi import msg

try:
    import spacy
except:
    pass

from goldenverba.ingestion.chunking.interface import Chunker
from goldenverba.ingestion.chunking.chunk import Chunk
from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import InputForm


class WordChunker(Chunker):
    """
    WordChunker for Verba built with spaCy
    """

    def __init__(self):
        self.name = "WordChunker"
        self.requires_env = []
        self.requires_library = ["spacy"]
        self.input_form = InputForm.CHUNKER.value
        self.description = "Chunk documents by words. You can specify how many words should overlap between chunks to improve retrieval."
        try:
            self.nlp = spacy.blank("en")
        except:
            self.nlp = None

    def chunk(
        self, documents: list[Document], units: int, overlap: int
    ) -> list[Document]:
        """Chunk verba documents into chunks based on units and overlap
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks
        """
        for document in documents:
            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            doc = self.nlp(document.text)

            if units > len(doc) or units < 1:
                msg.warn(
                    f"Unit value either exceeds length of actual document or is below 1 ({units}/{len(doc)})"
                )
                continue

            if overlap >= units:
                msg.warn(
                    f"Overlap value is greater than unit (Units {units}/ Overlap {overlap})"
                )
                continue

            i = 0
            split_id_counter = 0
            while i < len(doc):
                # Overlap
                start_i = i
                end_i = i + units
                if end_i > len(doc):
                    end_i = len(doc)  # Adjust for the last chunk

                doc_chunk = Chunk(
                    text=doc[start_i:end_i].text,
                    doc_name=document.name,
                    doc_type=document.type,
                    chunk_id=split_id_counter,
                )
                document.chunks.append(doc_chunk)
                split_id_counter += 1

                # Exit loop if this was the last possible chunk
                if end_i == len(doc):
                    break

                i += units - overlap  # Step forward, considering overlap

        return documents
