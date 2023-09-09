from goldenverba.ingestion.reader.manager import ReaderManager
from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.reader.interface import Reader


class VerbaManager:
    def __init__(self) -> None:
        self.reader_manager = ReaderManager()

    def reader_load(
        self,
        paths: list[str] = [],
        document_type: str = "Documentation",
    ) -> list[Document]:
        return self.reader_manager.load(paths, document_type)

    def reader_set_reader(self, reader: str) -> bool:
        return self.reader_manager.set_reader(reader)

    def reader_get_readers(self) -> dict[str, Reader]:
        return self.reader_manager.get_readers()
