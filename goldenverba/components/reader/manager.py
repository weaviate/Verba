from wasabi import msg

from goldenverba.components.reader.document import Document
from goldenverba.components.reader.githubreader import GithubReader
from goldenverba.components.reader.interface import Reader
from goldenverba.components.reader.pdfreader import PDFReader
from goldenverba.components.reader.simplereader import SimpleReader
from goldenverba.components.reader.unstructuredpdf import UnstructuredPDF


class ReaderManager:
    def __init__(self):
        self.readers: dict[str, Reader] = {
            "SimpleReader": SimpleReader(),
            "PDFReader": PDFReader(),
            "GithubReader": GithubReader(),
            "UnstructuredPDF": UnstructuredPDF(),
        }
        self.selected_reader: Reader = self.readers["SimpleReader"]

    def load(
        self,
        bytes: list[str] = None,
        contents: list[str] = None,
        paths: list[str] = None,
        fileNames: list[str] = None,
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: bytes : list[str] - List of bytes
        @parameter: contents : list[str] - List of string content
        @parameter: paths : list[str] - List of paths to files
        @parameter: fileNames : list[str] - List of file names
        @parameter: document_type : str - Document type
        @returns list[Document] - Lists of documents.
        """
        if fileNames is None:
            fileNames = []
        if paths is None:
            paths = []
        if contents is None:
            contents = []
        if bytes is None:
            bytes = []
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
