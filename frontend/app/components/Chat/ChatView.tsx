"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";
import ChatInterface from "./ChatInterface";

import DocumentExplorer from "../Document/DocumentExplorer";

import { Credentials, RAGConfig, ChunkScore } from "@/app/api_types";

interface ChatViewProps {
  settingConfig: SettingsConfiguration;
  credentials: Credentials;
  production: boolean;
  currentPage: string;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
}

const ChatView: React.FC<ChatViewProps> = ({
  credentials,
  settingConfig,
  production,
  currentPage,
  RAGConfig,
  setRAGConfig,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [selectedChunkScore, setSelectedChunkScore] = useState<ChunkScore[]>(
    []
  );
  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedDocument ? "hidden lg:flex lg:w-[45vw]" : "w-full lg:w-[45vw] lg:flex"}`}
      >
        <ChatInterface
          credentials={credentials}
          settingConfig={settingConfig}
          setSelectedDocument={setSelectedDocument}
          setSelectedChunkScore={setSelectedChunkScore}
          currentPage={currentPage}
          RAGConfig={RAGConfig}
          setRAGConfig={setRAGConfig}
        />
      </div>

      <div
        className={`${selectedDocument ? "lg:w-[55vw] w-full flex" : "hidden lg:flex lg:w-[55vw]"}`}
      >
        <DocumentExplorer
          credentials={credentials}
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
