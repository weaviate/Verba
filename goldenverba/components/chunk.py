class Chunk:
    def __init__(
        self,
        text: str = "",
        doc_name: str = "",
        doc_type: str = "",
        doc_uuid: str = "",
        chunk_id: str = "",
    ):
        self._text = text
        self._doc_name = doc_name
        self._doc_type = doc_type
        self._doc_uuid = doc_uuid
        self._chunk_id = chunk_id
        self._tokens = 0
        self._vector = None
        self._score = 0

    @property
    def text(self):
        return self._text

    @property
    def text_no_overlap(self):
        return self._text_no_overlap

    @property
    def doc_name(self):
        return self._doc_name

    @property
    def doc_type(self):
        return self._doc_type

    @property
    def doc_uuid(self):
        return self._doc_uuid

    @property
    def chunk_id(self):
        return self._chunk_id

    @property
    def tokens(self):
        return self._tokens

    @property
    def vector(self):
        return self._vector

    @property
    def score(self):
        return self._score

    def set_uuid(self, uuid):
        self._doc_uuid = uuid

    def set_tokens(self, token):
        self._tokens = token

    def set_vector(self, vector):
        self._vector = vector

    def set_score(self, score):
        self._score = score

    def to_dict(self) -> dict:
        """Convert the Chunk object to a dictionary."""
        return {
            "text": self.text,
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "doc_uuid": self.doc_uuid,
            "chunk_id": self.chunk_id,
            "tokens": self.tokens,
            "vector": self.vector,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Construct a Chunk object from a dictionary."""
        chunk = cls(
            text=data.get("text", ""),
            doc_name=data.get("doc_name", ""),
            doc_type=data.get("doc_type", ""),
            doc_uuid=data.get("doc_uuid", ""),
            chunk_id=data.get("chunk_id", ""),
        )
        chunk.set_tokens(data.get("tokens", 0))
        chunk.set_vector(data.get("vector", None))
        chunk.set_score(data.get("score", 0))
        return chunk
