import { DocumentChunk } from "../Document/types";

export interface Message {
    type: "user" | "system";
    content: string;
    cached?: boolean;
    distance?: string;
}

export type QueryPayload = {
    chunks: DocumentChunk[]
    context: string;
}

export type Segment =
    | { type: "text"; content: string }
    | { type: "code"; language: string; content: string };