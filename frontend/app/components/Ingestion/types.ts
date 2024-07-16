import { RAGConfig } from "../RAG/types";

export type FileData = {
  fileID: string;
  filename: string;
  isURL: boolean;
  overwrite: boolean;
  extension: string;
  source: string;
  content: string;
  labels: string[];
  file_size: number;
  status_report: StatusReportMap;
  status:
    | "READY"
    | "STARTING"
    | "LOADING"
    | "CHUNKING"
    | "EMBEDDING"
    | "INGESTING"
    | "NER"
    | "EXTRACTION"
    | "SUMMARIZING"
    | "WAITING"
    | "DONE"
    | "ERROR";
  rag_config: RAGConfig;
};

export type StatusReportMap = {
  [key: string]: StatusReport;
};

export type StatusReport = {
  fileID: string;
  status:
    | "READY"
    | "STARTING"
    | "LOADING"
    | "CHUNKING"
    | "EMBEDDING"
    | "INGESTING"
    | "NER"
    | "EXTRACTION"
    | "SUMMARIZING"
    | "DONE"
    | "WAITING"
    | "ERROR";
  message: string;
  took: number;
};

export const statusColorMap = {
  DONE: "bg-secondary-verba",
  ERROR: "bg-warning-verba",
  READY: "bg-button-verba",
  STARTING: "bg-button-verba",
  CHUNKING: "bg-button-verba",
  LOADING: "bg-button-verba",
  EMBEDDING: "bg-button-verba",
  INGESTING: "bg-button-verba",
  NER: "bg-button-verba",
  EXTRACTION: "bg-button-verba",
  SUMMARIZING: "bg-button-verba",
  WAITING: "bg-button-verba",
};

export const statusTextMap = {
  DONE: "Finished",
  ERROR: "Failed",
  READY: "Ready",
  STARTING: "Importing...",
  CHUNKING: "Chunking...",
  LOADING: "Loading...",
  EMBEDDING: "Embedding...",
  INGESTING: "Weaviating...",
  NER: "Extracting NER...",
  EXTRACTION: "Extraction REL...",
  SUMMARIZING: "Summarizing...",
  WAITING: "Waiting...",
};

export type FileMap = {
  [key: string]: FileData;
};

export type MetaData = {
  content: string;
  enable_ner: boolean;
  ner_labels: string[];
};
