from goldenverba.server.types import FileConfig
from goldenverba.components.chunk import Chunk
from spacy.tokens import Doc
from spacy.language import Language
import spacy
import json

from langdetect import detect


def load_nlp_for_language(language: str):
    """Load SpaCy models based on language"""
    if language == "en":
        nlp = spacy.blank("en")
    elif language == "zh":
        nlp = spacy.blank("zh")
    elif language == "zh-hant":
        nlp = spacy.blank("zh-hant")
    elif language == "fr":
        nlp = spacy.blank("fr")
    elif language == "de":
        nlp = spacy.blank("de")
    elif language == "nl":
        nlp = spacy.blank("nl")
    else:
        nlp = spacy.blank("en")

    nlp.add_pipe("sentencizer")

    return nlp


def detect_language(text: str) -> str:
    """Automatically detect language"""
    try:
        detected_lang = detect(text)
        if detected_lang == "zh-cn":
            return "zh"
        elif detected_lang == "zh-tw" or detected_lang == "zh-hk":
            return "zh-hant"
        return detected_lang
    except:
        return "unknown"


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
        metadata: str = "",
    ):
        self.title = title
        self.content = content
        self.extension = extension
        self.fileSize = fileSize
        self.labels = labels
        self.source = source
        self.meta = meta
        self.metadata = metadata
        self.chunks: list[Chunk] = []

        MAX_BATCH_SIZE = 500000

        if len(content) > MAX_BATCH_SIZE:
            # Process content in batches
            docs = []
            detected_language = detect_language(content[0:MAX_BATCH_SIZE])
            nlp = load_nlp_for_language(detected_language)

            for i in range(0, len(content), MAX_BATCH_SIZE):
                docs.append(nlp(content[i : i + MAX_BATCH_SIZE]))

            # Merged all processed docs
            doc = Doc.from_docs(docs)
        else:
            # Process smaller content, directly based on language
            detected_language = detect_language(content)
            nlp = load_nlp_for_language(detected_language)
            doc = nlp(content)

        self.spacy_doc = doc

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
            "meta": json.dumps(document.meta),
            "metadata": document.metadata,
        }
        return doc_dict

    @staticmethod
    def from_json(doc_dict: dict, nlp):
        """Convert a JSON string to a Document object."""

        if (
            "title" in doc_dict
            and "content" in doc_dict
            and "extension" in doc_dict
            and "fileSize" in doc_dict
            and "labels" in doc_dict
            and "source" in doc_dict
            and "meta" in doc_dict
            and "metadata" in doc_dict
        ):
            document = Document(
                title=doc_dict.get("title", ""),
                content=doc_dict.get("content", ""),
                extension=doc_dict.get("extension", ""),
                fileSize=doc_dict.get("fileSize", 0),
                labels=doc_dict.get("labels", []),
                source=doc_dict.get("source", ""),
                meta=doc_dict.get("meta", {}),
                metadata=doc_dict.get("metadata", ""),
            )
            return document
        else:
            return None


def create_document(content: str, fileConfig: FileConfig) -> Document:
    """Create a Document object from the file content."""
    return Document(
        title=fileConfig.filename,
        content=content,
        extension=fileConfig.extension,
        labels=fileConfig.labels,
        source=fileConfig.source,
        fileSize=fileConfig.file_size,
        metadata=fileConfig.metadata,
        meta={},
    )
