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

import InfoComponent from "../Navigation/InfoComponent";
import { MdCancel } from "react-icons/md";
import { MdOutlineRefresh } from "react-icons/md";
import { MdContentPaste } from "react-icons/md";
import { MdContentCopy } from "react-icons/md";
import { TbVectorTriangle } from "react-icons/tb";

import { FaDatabase } from "react-icons/fa";
import UserModalComponent from "../Navigation/UserModal";

import { RAGConfig } from "../RAG/types";
import ComponentStatus from "../Status/ComponentStatus";

interface DocumentExplorerProps {
  APIHost: string | null;
  selectedDocument: string | null;
  setSelectedDocument: (c: string | null) => void;
  settingConfig: SettingsConfiguration;
  production: boolean;
}

const DocumentExplorer: React.FC<DocumentExplorerProps> = ({
  APIHost,
  selectedDocument,
  settingConfig,
  setSelectedDocument,
  production,
}) => {
  const [selectedSetting, setSelectedSetting] = useState<
    "Content" | "Chunks" | "Metadata" | "Config" | "Vector Space" | "Graph"
  >("Content");

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* Search Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start ">
          <InfoComponent
            settingConfig={settingConfig}
            tooltip_text="Inspect your all information about your document, such as chunks, metadata and more."
            display_text="Explorer"
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
            <p>Vector Space</p>
          </button>

          <button
            onClick={() => {
              setSelectedSetting("Graph");
            }}
            className={`flex ${selectedSetting === "Graph" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <SlGraph size={15} />
            <p>Graph</p>
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
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 items-center h-full w-full overflow-auto"></div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        <div className="flex gap-3 justify-end">
          <button className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2">
            <FaInfoCircle size={15} />
            <p>View Source</p>
          </button>
          <button className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2">
            <FaInfoCircle size={15} />
            <p>View Metadata</p>
          </button>
          <button className="flex btn border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2">
            <MdCancel size={15} />
            <p>Delete</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentExplorer;
