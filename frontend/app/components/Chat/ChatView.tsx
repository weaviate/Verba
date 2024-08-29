"use client";

import React, { useState } from "react";
import ChatInterface from "./ChatInterface";

import DocumentExplorer from "../Document/DocumentExplorer";

import {
  Credentials,
  RAGConfig,
  ChunkScore,
  Theme,
  DocumentFilter,
} from "@/app/types";

interface ChatViewProps {
  selectedTheme: Theme;
  credentials: Credentials;
  production: "Local" | "Demo" | "Production";
  currentPage: string;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  documentFilter: DocumentFilter[];
  setDocumentFilter: React.Dispatch<React.SetStateAction<DocumentFilter[]>>;
}

const ChatView: React.FC<ChatViewProps> = ({
  credentials,
  selectedTheme,
  production,
  currentPage,
  RAGConfig,
  setRAGConfig,
  documentFilter,
  setDocumentFilter,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [selectedChunkScore, setSelectedChunkScore] = useState<ChunkScore[]>(
    []
  );
  return (
    <div className="flex md:flex-row flex-col justify-center gap-3 md:h-[80vh] ">
      <div
        className={`${selectedDocument ? "hidden md:flex md:w-[45vw]" : "w-full md:w-[45vw] md:flex"}`}
      >
        <ChatInterface
          production={production}
          credentials={credentials}
          selectedTheme={selectedTheme}
          setSelectedDocument={setSelectedDocument}
          setSelectedChunkScore={setSelectedChunkScore}
          currentPage={currentPage}
          RAGConfig={RAGConfig}
          setRAGConfig={setRAGConfig}
          documentFilter={documentFilter}
          setDocumentFilter={setDocumentFilter}
        />
      </div>

      <div
        className={`${selectedDocument ? "md:w-[55vw] w-full flex" : "hidden md:flex md:w-[55vw]"}`}
      >
        <DocumentExplorer
          credentials={credentials}
          documentFilter={documentFilter}
          setDocumentFilter={setDocumentFilter}
          setSelectedDocument={setSelectedDocument}
          selectedTheme={selectedTheme}
          selectedDocument={selectedDocument}
          chunkScores={selectedChunkScore}
        />
      </div>
    </div>
  );
};

export default ChatView;
