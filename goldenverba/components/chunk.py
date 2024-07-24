class Chunk:
    def __init__(
        self,
        content: str = "",
        chunk_id: str = "",
    ):
        self.content = content
        self.chunk_id = chunk_id
        self.vector = None
        self.doc_uuid = None
        self.pca = [0,0,0]

    def to_json(self) -> dict:
        """Convert the Chunk object to a dictionary."""
        return {
            "content": self.content,
            "chunk_id": self.chunk_id,
            "doc_uuid": self.doc_uuid,
            "pca": self.pca
        }

    @classmethod
    def from_json(cls, data: dict):
        """Construct a Chunk object from a dictionary."""
        chunk = cls(
            content=data.get("content", ""),
            chunk_id=data.get("chunk_id", 0)
        )
        chunk.doc_uuid = data.get("doc_uuid", ""),
        chunk.pca = data.get("pca", [0,0,0]),
        return chunk
