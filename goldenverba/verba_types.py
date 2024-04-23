from typing import TypedDict
from dataclasses import dataclass

# from weaviate.collections.classes.config_named_vectors import _NamedVectorConfigCreate
from typing import Union, Any


class SuggestionType(TypedDict):
    suggestion: str
    system: str
    query: str


class DocumentType(TypedDict):
    doc_type: str
    doc_name: str
    doc_link: str


class ChunkType(TypedDict):
    text: str
    doc_name: str
    doc_type: str
    doc_uuid: str
    chunk_id: int


class CacheType(TypedDict):
    query: str
    system: str


@dataclass
class VectorizerType:
    name: str
    config_class: Any


@dataclass
class EmbeddingType:
    name: str


VectorizerOrEmbeddingType = Union[VectorizerType, EmbeddingType]
