from goldenverba.ingestion.reader.pathreader import PathReader
from goldenverba.ingestion.reader.simplereader import SimpleReader
from goldenverba.ingestion.reader.interface import Reader
from goldenverba.ingestion.reader.document import Document

from wasabi import msg


class ReaderManager:
    def __init__(self):
        self.readers: dict[str, Reader] = {
            "SimpleReader": SimpleReader(),
            "PathReader": PathReader(),
        }
        self.selected_reader: Reader = self.readers["SimpleReader"]

    def load(
        self,
        paths: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Load data from text sources
        @parameter: paths : list[str] - List of paths to resources
        @parameter: document_type : str - Document type
        @returns list[Document] - List of Documents
        """
        return self.selected_reader.load(paths, document_type)

    def set_reader(self, reader: str) -> bool:
        if reader in self.readers:
            self.selected_reader = self.readers[reader]
            return True
        else:
            msg.warn(f"Reader {reader} not found")
            return False

    def get_readers(self) -> dict[str, Reader]:
        return self.readers
