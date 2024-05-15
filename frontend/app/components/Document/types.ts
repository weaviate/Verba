export type DocumentChunk = {
  text: string;
  doc_name: string;
  chunk_id: number;
  doc_uuid: string;
  doc_type: string;
  score: number;
};

export type DocumentPayload = {
  error: string;
  document: Document;
};

export type AllDocumentsPayload = {
  error: string;
  documents: Document[];
  doc_types: string[];
  current_embedder: string;
  took: number;
};

export type Document = {
  text: string;
  name: string;
  chunks: number;
  uuid: string;
  type: string;
  class: string;
  timestamp: string;
  link: string;
};

export type FormattedDocument = {
  beginning: string;
  substring: string;
  ending: string;
};
