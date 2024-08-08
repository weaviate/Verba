from pydantic import BaseModel
from enum import Enum


class ConversationItem(BaseModel):
    type: str
    content: str


class SearchQueryPayload(BaseModel):
    query: str
    labels: list[str]
    page: int
    pageSize: int


class ChunksPayload(BaseModel):
    uuid: str
    page: int
    pageSize: int


class GetDocumentPayload(BaseModel):
    uuid: str


class GetChunkPayload(BaseModel):
    uuid: str
    embedder: str


class GetVectorPayload(BaseModel):
    uuid: str
    showAll: bool


class ResetPayload(BaseModel):
    resetMode: str


class ConnectPayload(BaseModel):
    deployment: str
    weaviateURL: str
    weaviateAPIKey: str


class DataBatchPayload(BaseModel):
    chunk: str
    isLastChunk: bool
    total: int
    fileID: str
    order: int


class LoadPayload(BaseModel):
    reader: str
    chunker: str
    embedder: str
    fileBytes: list[str]
    fileNames: list[str]
    filePath: str
    document_type: str
    chunkUnits: int
    chunkOverlap: int


class ImportPayload(BaseModel):
    data: list
    textValues: list[str]
    config: dict


class GetComponentPayload(BaseModel):
    component: str


class SetComponentPayload(BaseModel):
    component: str
    selected_component: str


# Import


class FileStatus(str, Enum):
    READY = "READY"
    CREATE_NEW = "CREATE_NEW"
    STARTING = "STARTING"
    LOADING = "LOADING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INGESTING = "INGESTING"
    NER = "NER"
    EXTRACTION = "EXTRACTION"
    SUMMARIZING = "SUMMARIZING"
    DONE = "DONE"
    ERROR = "ERROR"


class ConfigSetting(BaseModel):
    type: str
    value: str | int
    description: str
    values: list[str]


class RAGComponentConfig(BaseModel):
    name: str
    variables: list[str]
    library: list[str]
    description: str
    config: dict[str, ConfigSetting]
    type: str
    available: bool


class RAGComponentClass(BaseModel):
    selected: str
    components: dict[str, RAGComponentConfig]


class StatusReport(BaseModel):
    fileID: str
    status: str
    message: str
    took: float


class CreateNewDocument(BaseModel):
    new_file_id: str
    filename: str
    original_file_id: str


class FileConfig(BaseModel):
    fileID: str
    filename: str
    isURL: bool
    overwrite: bool
    extension: str
    source: str
    content: str
    labels: list[str]
    rag_config: dict[str, RAGComponentClass]
    file_size: int
    status: FileStatus
    status_report: dict


class ImportStreamPayload(BaseModel):
    fileMap: dict[str, FileConfig]


class VerbaConfig(BaseModel):
    RAG: dict[str, RAGComponentClass]
    SETTING: dict


class QueryPayload(BaseModel):
    query: str
    config: VerbaConfig


class DatacountPayload(BaseModel):
    embedding_model: str


class ChunkScore(BaseModel):
    uuid: str
    score: float
    chunk_id: int
    embedder: str


class GetContentPayload(BaseModel):
    uuid: str
    page: int
    chunkScores: list[ChunkScore]


class GeneratePayload(BaseModel):
    query: str
    context: str
    conversation: list[ConversationItem]
    rag_config: dict[str, RAGComponentClass]


class ConfigPayload(BaseModel):
    config: VerbaConfig
