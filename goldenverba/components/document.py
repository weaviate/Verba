from goldenverba.server.types import FileConfig
from goldenverba.components.chunk import Chunk
from spacy.tokens import Doc
from spacy.language import Language
import spacy
import json

from langdetect import detect

SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Simplified Chinese",
    "zh-hant": "Traditional Chinese",
    "fr": "French",
    "de": "German",
    "nl": "Dutch",
}


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
        raise ValueError(f"Unsupported language: {language}")

    # Add sentence segmentation to languages
    if language == "en":
        nlp.add_pipe("sentencizer", config={"punct_chars": None})
    else:
        nlp.add_pipe("sentencizer")  #
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


def split_text_by_language(text: str):
    """Separate text into language parts based on character ranges"""
    chinese_simplified = "".join(
        [char for char in text if "\u4e00" <= char <= "\u9fff"]
    )
    chinese_traditional = "".join(
        [
            char
            for char in text
            if "\u3400" <= char <= "\u4dbf" or "\u4e00" <= char <= "\u9fff"
        ]
    )
    english_part = "".join([char for char in text if char.isascii()])
    other_text = "".join(
        [char for char in text if not (char.isascii() or "\u4e00" <= char <= "\u9fff")]
    )

    return chinese_simplified, chinese_traditional, english_part, other_text


def process_mixed_language(content: str):
    """Process mixed language text"""
    chinese_simplified, chinese_traditional, english_text, other_text = (
        split_text_by_language(content)
    )

    docs = []

    if chinese_simplified:
        nlp_zh = load_nlp_for_language("zh")
        docs.append(nlp_zh(chinese_simplified))

    if chinese_traditional:
        nlp_zh_hant = load_nlp_for_language("zh-hant")
        docs.append(nlp_zh_hant(chinese_traditional))

    if english_text:
        nlp_en = load_nlp_for_language("en")
        docs.append(nlp_en(english_text))

    if other_text:
        detected_lang = detect_language(other_text)
        if detected_lang in SUPPORTED_LANGUAGES:
            nlp_other = load_nlp_for_language(detected_lang)
            docs.append(nlp_other(other_text))

    # Merge all processed documents
    doc = Doc.from_docs(docs)
    return doc


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
            print("TOOO BIG!")
            docs = []
            detected_language = detect_language(content[0:MAX_BATCH_SIZE])
            if detected_language in SUPPORTED_LANGUAGES:
                nlp = load_nlp_for_language(detected_language)
            else:
                nlp = process_mixed_language

            for i in range(0, len(content), MAX_BATCH_SIZE):
                docs.append(nlp(content[i : i + MAX_BATCH_SIZE]))

            # Merged all processed docs
            doc = Doc.from_docs(docs)
        else:
            # Process smaller content, directly based on language
            detected_language = detect_language(content)
            if detected_language in SUPPORTED_LANGUAGES:
                nlp = load_nlp_for_language(detected_language)
                doc = nlp(content)
            else:
                # Process mixed language content
                doc = process_mixed_language(content)

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
