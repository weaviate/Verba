"use client";
import React, { useState, useEffect } from "react";
import { FaInfoCircle } from "react-icons/fa";
import VectorView from "./VectorView";
import ChunkView from "./ChunkView";
import InfoComponent from "../Navigation/InfoComponent";
import { MdCancel } from "react-icons/md";
import { MdContentPaste } from "react-icons/md";
import { MdContentCopy } from "react-icons/md";
import { TbVectorTriangle } from "react-icons/tb";
import ContentView from "./ContentView";
import { IoMdAddCircle } from "react-icons/io";
import {
  VerbaDocument,
  DocumentPayload,
  Credentials,
  ChunkScore,
  Theme,
  DocumentFilter,
} from "@/app/types";

import { fetchSelectedDocument } from "@/app/api";

interface DocumentExplorerProps {
  selectedDocument: string | null;
  setSelectedDocument: (c: string | null) => void;
  chunkScores?: ChunkScore[];
  credentials: Credentials;
  selectedTheme: Theme;
  documentFilter: DocumentFilter[];
  setDocumentFilter: React.Dispatch<React.SetStateAction<DocumentFilter[]>>;
}

const DocumentExplorer: React.FC<DocumentExplorerProps> = ({
  credentials,
  selectedDocument,
  setSelectedDocument,
  chunkScores,
  selectedTheme,
  documentFilter,
  setDocumentFilter,
}) => {
  const [selectedSetting, setSelectedSetting] = useState<
    "Content" | "Chunks" | "Metadata" | "Config" | "Vector Space" | "Graph"
  >("Content");

  const [isFetching, setIsFetching] = useState(false);
  const [document, setDocument] = useState<VerbaDocument | null>(null);

  useEffect(() => {
    if (selectedDocument) {
      handleFetchSelectedDocument();
    } else {
      setDocument(null);
    }
  }, [selectedDocument]);

  const handleSourceClick = (url: string) => {
    // Open a new tab with the specified URL
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const handleFetchSelectedDocument = async () => {
    try {
      setIsFetching(true);

      const data: DocumentPayload | null = await fetchSelectedDocument(
        selectedDocument,
        credentials
      );

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
            tooltip_text="Inspect your all information about your document, such as chunks, metadata and more."
            display_text={document ? document.title : "Loading..."}
          />
        </div>
        <div className="flex gap-3 justify-end">
          <button
            onClick={() => {
              setSelectedSetting("Content");
            }}
            className={`flex ${selectedSetting === "Content" ? "bg-primary-verba hover:bg-button-hover-verba text-text-verba" : "bg-button-verba hover:text-text-verba hover:bg-button-hover-verba"} border-none btn text-text-alt-verba gap-2`}
          >
            <MdContentPaste size={15} />
            <p>Content</p>
          </button>

          <button
            onClick={() => {
              setSelectedSetting("Chunks");
            }}
            className={`flex ${selectedSetting === "Chunks" ? "bg-primary-verba hover:bg-button-hover-verba text-text-verba" : "bg-button-verba hover:text-text-verba hover:bg-button-hover-verba"} border-none btn text-text-alt-verba gap-2`}
          >
            <MdContentCopy size={15} />
            <p>Chunks</p>
          </button>

          <button
            onClick={() => {
              setSelectedSetting("Vector Space");
            }}
            className={`flex ${selectedSetting === "Vector Space" ? "bg-primary-verba hover:bg-button-hover-verba text-text-verba" : "bg-button-verba hover:text-text-verba hover:bg-button-hover-verba"} border-none btn text-text-alt-verba gap-2`}
          >
            <TbVectorTriangle size={15} />
            <p>Vector</p>
          </button>

          <button
            onClick={() => {
              setSelectedDocument(null);
            }}
            className="flex btn btn-square border-none text-text-verba bg-warning-verba hover:bg-button-hover-verba gap-2"
          >
            <MdCancel size={15} />
          </button>
        </div>
      </div>

      {/* Document List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 h-full w-full overflow-y-auto overflow-x-hidden">
        {selectedSetting === "Content" && (
          <ContentView
            selectedTheme={selectedTheme}
            document={document}
            credentials={credentials}
            selectedDocument={selectedDocument}
            chunkScores={chunkScores}
          />
        )}

        {selectedSetting === "Chunks" && (
          <ChunkView
            selectedTheme={selectedTheme}
            credentials={credentials}
            selectedDocument={selectedDocument}
          />
        )}

        {selectedSetting === "Vector Space" && (
          <VectorView
            credentials={credentials}
            selectedDocument={selectedDocument}
            chunkScores={chunkScores}
          />
        )}
      </div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-3">
          {documentFilter.some(
            (filter) => filter.uuid === selectedDocument
          ) && (
            <button
              onClick={() => {
                setDocumentFilter(
                  documentFilter.filter((f) => f.uuid !== selectedDocument)
                );
              }}
              className="btn border-none shadow-none text-text-verba bg-warning-verba hover:bg-button-hover-verba"
            >
              <MdCancel size={15} />
              <p>Remove from Chat</p>
            </button>
          )}
          {!documentFilter.some((filter) => filter.uuid === selectedDocument) &&
            document && (
              <button
                onClick={() => {
                  setDocumentFilter([
                    ...documentFilter,
                    { uuid: selectedDocument, title: document.title },
                  ]);
                }}
                className="btn border-none shadow-none text-text-verba bg-primary-verba hover:bg-button-hover-verba"
              >
                <IoMdAddCircle size={15} />
                <p>Add to Chat</p>
              </button>
            )}
        </div>
        <div className="flex gap-3">
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
            className={`flex ${selectedSetting === "Metadata" ? "bg-primary-verba hover:bg-button-hover-verba text-text-verba" : "bg-button-verba hover:text-text-verba hover:bg-button-hover-verba"} border-none btn text-text-alt-verba gap-2`}
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
