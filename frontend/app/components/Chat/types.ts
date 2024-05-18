import { DocumentChunk } from "../Document/types";

export interface Message {
  type: "user" | "system";
  content: string;
  cached?: boolean;
  distance?: string;
}

export type QueryPayload = {
  chunks: DocumentChunk[];
  context: string;
  error: string;
  took: number;
};

export type Segment =
  | { type: "text"; content: string }
  | { type: "code"; language: string; content: string };
