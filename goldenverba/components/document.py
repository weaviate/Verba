from goldenverba.components.chunk import Chunk


class Document:
    def __init__(
        self,
        title: str = "",
        content: str = "",
        extension: str = "",
        fileSize: int = 0,
        labels: list[str] = [],
        source: str = "",
        meta: dict = {},
    ):
        self.title = title
        self.content = content
        self.extension = extension
        self.fileSize = fileSize
        self.labels = labels
        self.source = source
        self.meta = meta
        self.chunks: list[Chunk] = []

    @staticmethod
    def to_json(document) -> dict:
        """Convert the Document object to a JSON dict."""
        doc_dict = {
            "text": document.text,
            "type": document.type,
            "name": document.name,
            "path": document.path,
            "link": document.link,
            "timestamp": document.timestamp,
            "reader": document.reader,
            "meta": document.meta,
            "chunks": [chunk.to_dict() for chunk in document.chunks],
        }
        return doc_dict

    @staticmethod
    def from_json(doc_dict: dict):
        """Convert a JSON string to a Document object."""
        document = Document(
            text=doc_dict.get("text", ""),
            type=doc_dict.get("type", ""),
            name=doc_dict.get("name", ""),
            path=doc_dict.get("path", ""),
            link=doc_dict.get("link", ""),
            timestamp=doc_dict.get("timestamp", ""),
            reader=doc_dict.get("reader", ""),
            meta=doc_dict.get("meta", {}),
        )
        # Assuming Chunk has a from_dict method
        document.chunks = [
            Chunk.from_dict(chunk_data) for chunk_data in doc_dict.get("chunks", [])
        ]
        return document
