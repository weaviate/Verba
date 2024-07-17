"use client";

import React, { useState, useEffect, use } from "react";
import InfoComponent from "../Navigation/InfoComponent";
import { SettingsConfiguration } from "../Settings/types";
import { IoMdAddCircle } from "react-icons/io";
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";
import { PiChartPieSliceFill } from "react-icons/pi";
import { IoSettingsSharp } from "react-icons/io5";
import { FaLayerGroup } from "react-icons/fa";
import { MdOutlineDataset } from "react-icons/md";
import { VscSave } from "react-icons/vsc";
import { VscSaveAll } from "react-icons/vsc";
import { HiDocumentReport } from "react-icons/hi";

import { closeOnClick } from "./util";

import UserModalComponent from "../Navigation/UserModal";
import ReportView from "./ReportView";

import { FileMap, FileData } from "./types";
import { RAGConfig } from "../RAG/types";

import BasicSettingView from "./BasicSettingView";
import ComponentView from "./ComponentView";

interface ConfigurationViewProps {
  settingConfig: SettingsConfiguration;
  selectedFileData: string | null;
  setSelectedFileData: (f: string | null) => void;
  fileMap: FileMap;
  setFileMap: React.Dispatch<React.SetStateAction<FileMap>>;
}

const ConfigurationView: React.FC<ConfigurationViewProps> = ({
  settingConfig,
  selectedFileData,
  fileMap,
  setFileMap,
  setSelectedFileData,
}) => {
  const [selectedSetting, setSelectedSetting] = useState<
    "Basic" | "Chunking" | "Embedding" | "Metadata" | "Report"
  >("Basic");

  useEffect(() => {
    if (selectedFileData) {
      if (fileMap[selectedFileData].status != "READY") {
        setSelectedSetting("Report");
      } else if (
        selectedSetting === "Report" &&
        fileMap[selectedFileData].status === "READY"
      ) {
        setSelectedSetting("Basic");
      }
    }
  }, [fileMap, selectedFileData]);

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* FileSelection Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start ">
          <InfoComponent
            settingConfig={settingConfig}
            tooltip_text="Configure all import settings related to chunking, embedding, adding meta data and more. You can save made changes individually or apply them to all other files"
            display_text="Import Config"
          />
        </div>
        {selectedFileData && fileMap[selectedFileData].status === "READY" ? (
          <div className="flex gap-3 justify-end">
            <button
              onClick={() => {
                setSelectedSetting("Basic");
              }}
              className={`flex ${selectedSetting === "Basic" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
            >
              <IoSettingsSharp size={15} />
              <p>Overview</p>
            </button>

            <button
              onClick={() => {
                setSelectedSetting("Chunking");
              }}
              className={`flex ${selectedSetting === "Chunking" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
            >
              <PiChartPieSliceFill size={15} />
              <p>Chunking</p>
            </button>

            <button
              onClick={() => {
                setSelectedSetting("Embedding");
              }}
              className={`flex ${selectedSetting === "Embedding" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
            >
              <FaLayerGroup size={15} />
              <p>Embedding</p>
            </button>

            <button
              onClick={() => {
                setSelectedSetting("Metadata");
              }}
              className={`flex ${selectedSetting === "Metadata" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
            >
              <MdOutlineDataset size={15} />
              <p>Metadata</p>
            </button>

            <button
              onClick={() => {
                setSelectedFileData(null);
              }}
              className="flex btn btn-square border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2"
            >
              <MdCancel size={15} />
            </button>
          </div>
        ) : (
          <div className="flex gap-3 justify-end">
            <button
              onClick={() => {
                setSelectedSetting("Report");
              }}
              className={`flex ${selectedSetting === "Report" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
            >
              <HiDocumentReport size={15} />
              <p>Report</p>
            </button>
            <button
              onClick={() => {
                setSelectedFileData(null);
              }}
              className="flex btn btn-square border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2"
            >
              <MdCancel size={15} />
            </button>
          </div>
        )}
      </div>

      {/* File List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 items-center h-full w-full overflow-auto">
        {selectedSetting === "Basic" && (
          <BasicSettingView
            selectedFileData={selectedFileData}
            setSelectedFileData={setSelectedFileData}
            fileMap={fileMap}
            setFileMap={setFileMap}
          />
        )}
        {selectedSetting === "Chunking" && (
          <ComponentView
            selectedFileData={selectedFileData}
            fileMap={fileMap}
            setFileMap={setFileMap}
            component_name="Chunker"
          />
        )}
        {selectedSetting === "Embedding" && (
          <ComponentView
            selectedFileData={selectedFileData}
            fileMap={fileMap}
            setFileMap={setFileMap}
            component_name="Embedder"
          />
        )}
        {selectedSetting === "Report" && (
          <ReportView selectedFileData={selectedFileData} fileMap={fileMap} />
        )}
      </div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        {selectedFileData && fileMap[selectedFileData].status === "READY" && (
          <div className="flex gap-3 justify-end">
            <button className="flex btn border-none text-text-verba bg-secondary-verba hover:bg-button-hover-verba gap-2">
              <VscSaveAll size={15} />
              <p>Apply to All</p>
            </button>
            <button className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2">
              <IoSettingsSharp size={15} />
              <p>Set as Default</p>
            </button>
            <button className="flex btn border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2">
              <MdCancel size={15} />
              <p>Reset</p>
            </button>
          </div>
        )}
      </div>
      <UserModalComponent
        modal_id={"apply_setting_to_all"}
        title={"Set as Default"}
        text={"Set current settings as Default and apply to all files?"}
        triggerString="Save as Default"
        triggerValue={null}
        triggerAccept={null}
      />
    </div>
  );
};

export default ConfigurationView;
