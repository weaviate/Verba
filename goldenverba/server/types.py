from pydantic import BaseModel


class QueryPayload(BaseModel):
    query: str


class ConversationItem(BaseModel):
    type: str
    content: str
    typewriter: bool


class GeneratePayload(BaseModel):
    query: str
    context: str
    conversation: list[ConversationItem]


class GeneratedMessage(BaseModel):
    message: str
    finish_reason: str
    cached: bool
    distance: float


class SearchQueryPayload(BaseModel):
    query: str
    doc_type: str


class GetDocumentPayload(BaseModel):
    document_id: str


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


class GetComponentPayload(BaseModel):
    component: str


class SetComponentPayload(BaseModel):
    component: str
    selected_component: str
