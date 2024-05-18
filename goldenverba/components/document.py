from goldenverba.components.chunk import Chunk


class Document:
    def __init__(
        self,
        text: str = "",
        type: str = "",
        name: str = "",
        path: str = "",
        link: str = "",
        timestamp: str = "",
        reader: str = "",
        meta: dict = None,
    ):
        if meta is None:
            meta = {}
        self._text = text
        self._type = type
        self._name = name
        self._path = path
        self._link = link
        self._timestamp = timestamp
        self._reader = reader
        self._meta = meta
        self.chunks: list[Chunk] = []

    @property
    def text(self):
        return self._text

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def link(self):
        return self._link

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def reader(self):
        return self._reader

    @property
    def meta(self):
        return self._meta

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
