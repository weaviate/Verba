"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";
import { RAGConfig } from "../RAG/types";
import ChatInterface from "./ChatInterface";

import DocumentExplorer from "../Document/DocumentExplorer";
import { ChunkScore } from "./types";

interface ChatViewProps {
  settingConfig: SettingsConfiguration;
  APIHost: string | null;
  setCurrentPage: (p: any) => void;
  RAGConfig: RAGConfig | null;
  production: boolean;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
}

const ChatView: React.FC<ChatViewProps> = ({
  APIHost,
  settingConfig,
  setCurrentPage,
  RAGConfig,
  production,
  setRAGConfig,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [selectedChunkScore, setSelectedChunkScore] = useState<ChunkScore[]>(
    []
  );

  const _RAGConfig = { ...RAGConfig };

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedDocument ? "hidden lg:flex lg:w-[45vw]" : "w-full lg:w-[45vw] lg:flex"}`}
      >
        {" "}
        <ChatInterface
          setRAGConfig={setRAGConfig}
          APIHost={APIHost}
          settingConfig={settingConfig}
          RAGConfig={_RAGConfig}
          selectedDocument={selectedDocument}
          setSelectedDocument={setSelectedDocument}
          setSelectedChunkScore={setSelectedChunkScore}
        />{" "}
      </div>

      <div
        className={`${selectedDocument ? "lg:w-[55vw] w-full flex" : "hidden lg:flex lg:w-[55vw]"}`}
      >
        <DocumentExplorer
          production={production}
          APIHost={APIHost}
          setSelectedDocument={setSelectedDocument}
          settingConfig={settingConfig}
          selectedDocument={selectedDocument}
          chunkScores={selectedChunkScore}
        />
      </div>
    </div>
  );
};

export default ChatView;
