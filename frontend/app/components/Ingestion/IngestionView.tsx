"use client";

import React, { useState, useEffect, use } from "react";

import FileSelectionView from "./FileSelectionView";
import ConfigurationView from "./ConfigurationView";
import { SettingsConfiguration } from "../Settings/types";

import { FileMap } from "./types";
import { RAGConfig } from "../RAG/types";

import { FileData } from "./types";

interface IngestionViewProps {
  settingConfig: SettingsConfiguration;
  RAGConfig: RAGConfig | null;
  setRAGConfig: (r_: RAGConfig | null) => void;
}

const IngestionView: React.FC<IngestionViewProps> = ({
  settingConfig,
  RAGConfig,
  setRAGConfig,
}) => {
  const [fileMap, setFileMap] = useState<FileMap>({});
  const [selectedFileData, setSelectedFileData] = useState<string | null>(null);

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div className="flex w-1/2">
        <FileSelectionView
          settingConfig={settingConfig}
          fileMap={fileMap}
          setFileMap={setFileMap}
          RAGConfig={RAGConfig}
          setRAGConfig={setRAGConfig}
          selectedFileData={selectedFileData}
          setSelectedFileData={setSelectedFileData}
        />
      </div>

      <div className="flex w-1/2">
        {selectedFileData && (
          <ConfigurationView
            settingConfig={settingConfig}
            selectedFileData={selectedFileData}
            fileMap={fileMap}
            setFileMap={setFileMap}
            setSelectedFileData={setSelectedFileData}
          />
        )}
      </div>
    </div>
  );
};

export default IngestionView;
