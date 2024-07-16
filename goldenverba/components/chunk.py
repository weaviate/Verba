class Chunk:
    def __init__(
        self,
        content: str = "",
        chunk_id: str = "",
        start: int = 0,
        end: int = 0,
        tokens: list[str] = [],
        meta: dict = {}
    ):
        self.content = content
        self.chunk_id = chunk_id
        self.start = start
        self.end = end
        self.tokens = tokens
        self.meta = meta

        self.vector = None
        self.score = None
        self.doc_uuid = None



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
