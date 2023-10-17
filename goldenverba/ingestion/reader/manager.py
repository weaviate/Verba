from goldenverba.ingestion.reader.simplereader import SimpleReader
from goldenverba.ingestion.reader.pathreader import PathReader
from goldenverba.ingestion.reader.interface import Reader
from goldenverba.ingestion.reader.document import Document

from wasabi import msg


class ReaderManager:
    def __init__(self):
        self.readers: dict[str, Reader] = {
            "SimpleReader": SimpleReader(),
            "PDFReader": PathReader(),
        }
        self.selected_reader: Reader = self.readers["SimpleReader"]

    def load(
        self,
        bytes: list[str] = [],
        contents: list[str] = [],
        paths: list[str] = [],
        fileNames: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: bytes : list[str] - List of bytes
        @parameter: contents : list[str] - List of string content
        @parameter: paths : list[str] - List of paths to files
        @parameter: fileNames : list[str] - List of file names
        @parameter: document_type : str - Document type
        @returns list[str] - List of strings
        """
        return self.selected_reader.load(
            bytes, contents, paths, fileNames, document_type
        )

    def set_reader(self, reader: str) -> bool:
        if reader in self.readers:
            self.selected_reader = self.readers[reader]
            return True
        else:
            msg.warn(f"Reader {reader} not found")
            return False

    def get_readers(self) -> dict[str, Reader]:
        return self.readers
