"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";
import { RAGConfig } from "../RAG/types";
import ChatInterface from "./ChatInterface";

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
          RAGConfig={RAGConfig}
        />{" "}
      </div>

      <div
        className={`${selectedDocument ? "lg:w-[55vw] w-full flex" : "hidden lg:flex lg:w-[55vw]"}`}
      ></div>
    </div>
  );
};

export default ChatView;
