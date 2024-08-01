"use client";
import React, { useState, useEffect } from "react";
import {
  DocumentChunk,
  DocumentPreview,
  DocumentsPreviewPayload,
} from "./types";
import { FaSearch } from "react-icons/fa";
import PulseLoader from "react-spinners/PulseLoader";
import { SettingsConfiguration } from "../Settings/types";
import { IoIosRefresh } from "react-icons/io";
import { FaTrash } from "react-icons/fa";
import { FaInfoCircle } from "react-icons/fa";
import { SlGraph } from "react-icons/sl";

import VectorView from "./VectorView";
import ChunkView from "./ChunkView";

import InfoComponent from "../Navigation/InfoComponent";
import { MdCancel } from "react-icons/md";
import { MdOutlineRefresh } from "react-icons/md";
import { MdContentPaste } from "react-icons/md";
import { MdContentCopy } from "react-icons/md";
import { TbVectorTriangle } from "react-icons/tb";
import ContentView from "./ContentView";

import { FaDatabase } from "react-icons/fa";
import UserModalComponent from "../Navigation/UserModal";

import { RAGConfig } from "../RAG/types";
import { ChunkScore } from "../Chat/types";
import ComponentStatus from "../Status/ComponentStatus";

import { VerbaDocument, DocumentPayload } from "./types";

interface DocumentExplorerProps {
  APIHost: string | null;
  selectedDocument: string | null;
  setSelectedDocument: (c: string | null) => void;
  settingConfig: SettingsConfiguration;
  production: boolean;
  chunkScores?: ChunkScore[];
}

const DocumentExplorer: React.FC<DocumentExplorerProps> = ({
  APIHost,
  selectedDocument,
  settingConfig,
  setSelectedDocument,
  production,
  chunkScores,
}) => {
  const [selectedSetting, setSelectedSetting] = useState<
    "Content" | "Chunks" | "Metadata" | "Config" | "Vector Space" | "Graph"
  >("Content");

  const [isFetching, setIsFetching] = useState(false);
  const [document, setDocument] = useState<VerbaDocument | null>(null);

  useEffect(() => {
    if (selectedDocument) {
      fetchSelectedDocument();
    } else {
      setDocument(null);
    }
  }, [selectedDocument]);

  const handleSourceClick = (url: string) => {
    // Open a new tab with the specified URL
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const fetchSelectedDocument = async () => {
    try {
      setIsFetching(true);

      const response = await fetch(APIHost + "/api/get_document", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          uuid: selectedDocument,
        }),
      });

      const data: DocumentPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setDocument(null);
          setSelectedDocument(null);
        } else {
          setDocument(data.document);
          setIsFetching(false);
        }
      }
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
    }
  };

  if (!selectedDocument) {
    return <div></div>;
  }

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* Search Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start ">
          <InfoComponent
            settingConfig={settingConfig}
            tooltip_text="Inspect your all information about your document, such as chunks, metadata and more."
            display_text={document ? document.title : "Loading..."}
          />
        </div>
        <div className="flex gap-3 justify-end">
          <button
            onClick={() => {
              setSelectedSetting("Content");
            }}
            className={`flex ${selectedSetting === "Content" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <MdContentPaste size={15} />
            <p>Content</p>
          </button>

          <button
            onClick={() => {
              setSelectedSetting("Chunks");
            }}
            className={`flex ${selectedSetting === "Chunks" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <MdContentCopy size={15} />
            <p>Chunks</p>
          </button>

          <button
            onClick={() => {
              setSelectedSetting("Vector Space");
            }}
            className={`flex ${selectedSetting === "Vector Space" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <TbVectorTriangle size={15} />
            <p>Vector</p>
          </button>

          <button
            onClick={() => {
              setSelectedDocument(null);
            }}
            className="flex btn btn-square border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2"
          >
            <MdCancel size={15} />
          </button>
        </div>
      </div>

      {/* Document List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 h-full w-full overflow-y-auto overflow-x-hidden">
        {selectedSetting === "Content" && (
          <ContentView
            document={document}
            settingConfig={settingConfig}
            APIHost={APIHost}
            selectedDocument={selectedDocument}
            chunkScores={chunkScores}
          />
        )}

        {selectedSetting === "Chunks" && (
          <ChunkView
            selectedDocument={selectedDocument}
            APIHost={APIHost}
            settingConfig={settingConfig}
          />
        )}

        {selectedSetting === "Vector Space" && (
          <VectorView
            APIHost={APIHost}
            selectedDocument={selectedDocument}
            settingConfig={settingConfig}
            chunkScores={chunkScores}
          />
        )}
      </div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        <div className="flex gap-3 justify-end">
          {selectedDocument && document && document.source && (
            <button
              onClick={() => {
                handleSourceClick(document.source);
              }}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
            >
              <FaInfoCircle size={15} />
              <p>View Source</p>
            </button>
          )}
          <button
            onClick={() => {
              setSelectedSetting("Metadata");
            }}
            className={`flex ${selectedSetting === "Metadata" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <FaInfoCircle size={15} />
            <p>View Metadata</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentExplorer;
