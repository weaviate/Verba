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
        self.tokens: list[str] = []
        self.chunks: list[Chunk] = []

    @staticmethod
    def to_json(document) -> dict:
        """Convert the Document object to a JSON dict."""
        doc_dict = {
            "title": document.title,
            "content": document.content,
            "extension": document.extension,
            "fileSize": document.fileSize,
            "labels": document.labels,
            "source": document.source,
            "meta": document.meta,
            "tokens": document.tokens
        }
        return doc_dict

    @staticmethod
    def from_json(doc_dict: dict):
        """Convert a JSON string to a Document object."""

        if "title" in doc_dict and "content" in doc_dict and "extension" in doc_dict and "fileSize" in doc_dict and "labels" in doc_dict and "source" in doc_dict and "meta" in doc_dict:
            document = Document(
                title=doc_dict.get("title", ""),
                content=doc_dict.get("content", ""),
                extension=doc_dict.get("extension", ""),
                fileSize=doc_dict.get("fileSize", 0),
                labels=doc_dict.get("labels", []),
                source=doc_dict.get("source", ""),
                meta=doc_dict.get("meta", {}),
            )
            document.tokens = doc_dict.get("tokens", [])
            return document
        else:
            return None
