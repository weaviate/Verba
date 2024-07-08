import { RAGConfig } from "../RAG/types";

export type FileData = {
  filename: string;
  isURL: boolean;
  extension: string;
  content: string;
  labels: string[];
  rag_config: RAGConfig;
  status:
    | "READY"
    | "LOADING"
    | "CHUNKING"
    | "EMBEDDING"
    | "NER"
    | "SUMMARIZING"
    | "DONE"
    | "ERROR";
};

export type FileMap = {
  [key: string]: FileData;
};

export type MetaData = {
  content: string;
  enable_ner: boolean;
  ner_labels: string[];
};
