from goldenverba.components.reader.document import Document
from goldenverba.components.reader.interface import InputForm
from goldenverba.components.component import VerbaComponent


class Chunker(VerbaComponent):
    """
    Interface for Verba Chunking
    """

    def __init__(self):
        super().__init__()
        self.input_form = InputForm.CHUNKER.value  # Default for all Chunkers
        self.default_units = 100
        self.default_overlap = 50

    def chunk(documents: list[Document], units: int, overlap: int) -> list[Document]:
        """Chunk verba documents into chunks based on units and overlap
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: units : int - How many units per chunk (words, sentences, etc.)
        @parameter: overlap : int - How much overlap between the chunks
        @returns list[str] - List of documents that contain the chunks
        """
        raise NotImplementedError("chunk method must be implemented by a subclass.")
