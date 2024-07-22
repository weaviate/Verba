class Chunk:
    def __init__(
        self,
        content: str = "",
        chunk_id: str = "",
        start: int = 0,
        end: int = 0,
    ):
        self.content = content
        self.chunk_id = chunk_id
        self.start = start
        self.end = end
        self.vector = None
        self.score = None
        self.doc_uuid = None
        self.is_response = False
        self.pca = [0,0,0]



    def to_dict(self) -> dict:
        """Convert the Chunk object to a dictionary."""
        return {
            "content": self.content,
            "chunk_id": self.chunk_id,
            "start": self.start,
            "end": self.end,
            "doc_uuid": self.doc_uuid,
            "is_response": self.is_response,
            "pca": self.pca
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Construct a Chunk object from a dictionary."""
        chunk = cls(
            content=data.get("content", ""),
            chunk_id=data.get("chunk_id", ""),
            start=data.get("start", 0),
            end=data.get("end", 0),
        )
        chunk.pca = data.get("pca", [0,0,0]),
        return chunk
