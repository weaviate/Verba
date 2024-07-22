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
  document: VerbaDocument;
};

export type ChunksPayload = {
  error: string;
  chunks: VerbaChunk[];
};

export type VectorsPayload = {
  error: string;
  vectors: VerbaVector[];
};

export type VerbaDocument = {
  title: string;
  content: string;
  extension: string;
  fileSize: number;
  labels: string[];
  source: string;
  meta: any;
  tokens: string[];
};

export type VerbaChunk = {
  content: string;
  chunk_id: number;
  start: number;
  end: number;
  doc_uuid: string;
  is_response: boolean;
  pca: number[];
};

export type DocumentsPreviewPayload = {
  error: string;
  documents: DocumentPreview[];
  labels: string[];
  took: number;
};

export type DocumentPreview = {
  title: string;
  uuid: string;
  labels: string[];
};

export type FormattedDocument = {
  beginning: string;
  substring: string;
  ending: string;
};

export type VerbaVector = {
  x: number;
  y: number;
  z: number;
};
