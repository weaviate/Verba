import { DocumentChunk } from "../Document/types";

export interface Message {
  type: "user" | "system" | "error";
  content: string;
  cached?: boolean;
  distance?: string;
}

export type QueryPayload = {
  error: string;
  documents: DocumentScore[];
};

export type DocumentScore = {
  title: string;
  uuid: string;
  score: number;
  chunks: ChunkScore[];
};

export type ChunkScore = {
  uuid: string;
  score: number;
};

export type Segment =
  | { type: "text"; content: string }
  | { type: "code"; language: string; content: string };
