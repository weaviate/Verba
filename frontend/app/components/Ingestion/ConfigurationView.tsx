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
import { FaHammer } from "react-icons/fa";

import { closeOnClick } from "./util";

import UserModalComponent from "../Navigation/UserModal";

import { FileMap, FileData } from "./types";
import { RAGConfig } from "../RAG/types";

import BasicSettingView from "./BasicSettingView";
import ComponentView from "./ComponentView";

interface ConfigurationViewProps {
  settingConfig: SettingsConfiguration;
  selectedFileData: string | null;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  setSelectedFileData: (f: string | null) => void;
  fileMap: FileMap;
  APIHost: string | null;

  setFileMap: React.Dispatch<React.SetStateAction<FileMap>>;
}

const ConfigurationView: React.FC<ConfigurationViewProps> = ({
  settingConfig,
  selectedFileData,
  fileMap,
  setFileMap,
  RAGConfig,
  setRAGConfig,
  setSelectedFileData,
  APIHost,
}) => {
  const [selectedSetting, setSelectedSetting] = useState<
    "Basic" | "Pipeline" | "Metadata"
  >("Basic");

  const applyToAll = () => {
    setFileMap((prevFileMap) => {
      if (selectedFileData) {
        const newRAGConfig: RAGConfig = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData].rag_config)
        );
        const newFileMap: FileMap = { ...prevFileMap };

        for (const fileID in prevFileMap) {
          const newFileData: FileData = JSON.parse(
            JSON.stringify(prevFileMap[fileID])
          );
          newFileData.rag_config = newRAGConfig;
          newFileData.source = prevFileMap[selectedFileData].source;
          newFileData.labels = prevFileMap[selectedFileData].labels;
          newFileData.overwrite = prevFileMap[selectedFileData].overwrite;
          newFileMap[fileID] = newFileData;
        }
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  const setAsDefault = async () => {
    if (selectedFileData) {
      setRAGConfig(fileMap[selectedFileData].rag_config);
    }
  };

  const resetConfig = () => {
    setFileMap((prevFileMap) => {
      if (selectedFileData && RAGConfig) {
        const newFileMap: FileMap = { ...prevFileMap };
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData])
        );
        newFileData.rag_config = RAGConfig;
        newFileMap[selectedFileData] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  const openApplyAllModal = () => {
    const modal = document.getElementById("apply_setting_to_all");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const openResetModal = () => {
    const modal = document.getElementById("reset_Setting");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const openDefaultModal = () => {
    const modal = document.getElementById("set_default_settings");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

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
              setSelectedSetting("Pipeline");
            }}
            className={`flex ${selectedSetting === "Pipeline" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <FaHammer size={15} />
            <p>Config</p>
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
        {selectedSetting === "Pipeline" && (
          <div className="flex flex-col gap-10 w-full">
            <ComponentView
              selectedFileData={selectedFileData}
              fileMap={fileMap}
              setFileMap={setFileMap}
              component_name="Reader"
            />
            <ComponentView
              selectedFileData={selectedFileData}
              fileMap={fileMap}
              setFileMap={setFileMap}
              component_name="Chunker"
            />
            <ComponentView
              selectedFileData={selectedFileData}
              fileMap={fileMap}
              setFileMap={setFileMap}
              component_name="Embedder"
            />
          </div>
        )}
      </div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        <div className="flex gap-3 justify-end">
          <button
            onClick={openApplyAllModal}
            className="flex btn border-none text-text-verba bg-secondary-verba hover:bg-button-hover-verba gap-2"
          >
            <VscSaveAll size={15} />
            <p>Apply to All</p>
          </button>
          <button
            onClick={openDefaultModal}
            className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
          >
            <IoSettingsSharp size={15} />
            <p>Set as Default</p>
          </button>
          <button
            onClick={openResetModal}
            className="flex btn border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2"
          >
            <MdCancel size={15} />
            <p>Reset</p>
          </button>
        </div>
      </div>
      <UserModalComponent
        modal_id={"apply_setting_to_all"}
        title={"Apply Pipeline Settings"}
        text={"Apply Pipeline Settings to all files?"}
        triggerString="Apply"
        triggerValue={null}
        triggerAccept={applyToAll}
      />
      <UserModalComponent
        modal_id={"reset_Setting"}
        title={"Reset Setting"}
        text={"Reset pipeline settings of this file?"}
        triggerString="Reset"
        triggerValue={null}
        triggerAccept={resetConfig}
      />

      <UserModalComponent
        modal_id={"set_default_settings"}
        title={"Set Default"}
        text={"Set current pipeline settings as default for future files?"}
        triggerString="Set"
        triggerValue={null}
        triggerAccept={setAsDefault}
      />
    </div>
  );
};

export default ConfigurationView;
