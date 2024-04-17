from typing import TypedDict
from dataclasses import dataclass
from weaviate import _NamedVectorConfigCreate
from typing import Union


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


@dataclass
class VectorizerType:
    name: str
    config_class: _NamedVectorConfigCreate


@dataclass
class EmbeddingType:
    name: str


VectorizerOrEmbeddingType = Union[VectorizerType, EmbeddingType]
