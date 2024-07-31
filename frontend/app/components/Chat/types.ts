import { DocumentChunk } from "../Document/types";

export interface Message {
  type: "user" | "system" | "error" | "retrieval";
  content: string | DocumentScore[];
  cached?: boolean;
  distance?: string;
}

export type QueryPayload = {
  error: string;
  documents: DocumentScore[];
  context: string;
};

export type DataCountPayload = {
  datacount: number;
};

export type DocumentScore = {
  title: string;
  uuid: string;
  score: number;
  chunks: ChunkScore[];
};

export type ChunkScore = {
  uuid: string;
  chunk_id: number;
  score: number;
  embedder: string;
};

export type Segment =
  | { type: "text"; content: string }
  | { type: "code"; language: string; content: string };
