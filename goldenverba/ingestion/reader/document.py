import pickle
from goldenverba.ingestion.chunking.chunk import Chunk


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
        meta: dict = {},
    ):
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

    @classmethod
    def serialize_to_verba(cls, document, file_path: str) -> None:
        """Serialize the document to a binary .verba file"""
        if not file_path.endswith(".verba"):
            raise ValueError("The file extension must be .verba")
        with open(file_path, "wb") as f:
            pickle.dump(document, f)

    @classmethod
    def deserialize_verba(cls, file_path: str):
        """Deserialize a .verba file to a Document object"""
        if not file_path.endswith(".verba"):
            raise ValueError("The file extension must be .verba")
        with open(file_path, "rb") as f:
            document = pickle.load(f)
        return document
