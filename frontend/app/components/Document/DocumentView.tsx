"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";
import DocumentSearch from "./DocumentSearch";

import { RAGConfig } from "../RAG/types";
import DocumentExplorer from "./DocumentExplorer";

interface DocumentViewProps {
  settingConfig: SettingsConfiguration;
  APIHost: string | null;
  setCurrentPage: (p: any) => void;
  RAGConfig: RAGConfig | null;
  production: boolean;
}

const DocumentView: React.FC<DocumentViewProps> = ({
  APIHost,
  settingConfig,
  setCurrentPage,
  RAGConfig,
  production,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedDocument ? "hidden lg:flex lg:w-[45vw]" : "w-full lg:w-[45vw] lg:flex"}`}
      >
        <DocumentSearch
          production={production}
          APIHost={APIHost}
          setSelectedDocument={setSelectedDocument}
          settingConfig={settingConfig}
          selectedDocument={selectedDocument}
        />
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
        />
      </div>
    </div>
  );
};

export default DocumentView;
