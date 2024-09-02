"use client";

import React, { useState, useCallback } from "react";
import InfoComponent from "../Navigation/InfoComponent";
import { MdCancel } from "react-icons/md";
import { IoSettingsSharp } from "react-icons/io5";
import { VscSaveAll } from "react-icons/vsc";
import { FaHammer } from "react-icons/fa";

import { updateRAGConfig } from "@/app/api";

import UserModalComponent from "../Navigation/UserModal";

import { FileMap, FileData } from "@/app/types";
import { RAGConfig } from "@/app/types";

import { Credentials, RAGComponentConfig } from "@/app/types";

import VerbaButton from "../Navigation/VerbaButton";

import BasicSettingView from "./BasicSettingView";
import ComponentView from "./ComponentView";

interface ConfigurationViewProps {
  selectedFileData: string | null;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  setSelectedFileData: (f: string | null) => void;
  fileMap: FileMap;
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;

  setFileMap: React.Dispatch<React.SetStateAction<FileMap>>;
}

const ConfigurationView: React.FC<ConfigurationViewProps> = ({
  selectedFileData,
  fileMap,
  addStatusMessage,
  setFileMap,
  RAGConfig,
  setRAGConfig,
  setSelectedFileData,
  credentials,
}) => {
  const [selectedSetting, setSelectedSetting] = useState<
    "Basic" | "Pipeline" | "Metadata"
  >("Basic");

  const applyToAll = () => {
    addStatusMessage("Applying config to all files", "INFO");
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
    addStatusMessage("Setting current config as default", "SUCCESS");
    if (selectedFileData) {
      const response = await updateRAGConfig(
        fileMap[selectedFileData].rag_config,
        credentials
      );
      if (response) {
        // Update local state if the API call was successful
        setRAGConfig(fileMap[selectedFileData].rag_config);
        // You might want to show a success message to the user
      } else {
        // Handle error
        console.error("Failed to set RAG config:");
      }
    }
  };

  const resetConfig = () => {
    addStatusMessage("Resetting pipeline settings", "WARNING");
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

  const updateConfig = useCallback(
    (
      component_n: string,
      configTitle: string,
      value: string | boolean | string[]
    ) => {
      setFileMap((prevFileMap) => {
        if (selectedFileData) {
          const newFileMap = { ...prevFileMap };
          const selectedFile = newFileMap[selectedFileData];
          const componentConfig =
            selectedFile.rag_config[component_n].components[
              selectedFile.rag_config[component_n].selected
            ].config;

          // Update the specific config value directly
          if (typeof value === "string" || typeof value === "boolean") {
            componentConfig[configTitle].value = value;
          } else {
            componentConfig[configTitle].values = value;
          }

          return newFileMap;
        }
        return prevFileMap;
      });
    },
    [selectedFileData]
  );

  const selectComponent = (component_n: string, selected_component: string) => {
    setFileMap((prevFileMap) => {
      if (selectedFileData) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData])
        );
        const newRAGConfig: RAGConfig = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData].rag_config)
        );
        newRAGConfig[component_n].selected = selected_component;
        newFileData.rag_config = newRAGConfig;
        const newFileMap: FileMap = { ...prevFileMap };
        newFileMap[selectedFileData] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  const saveComponentConfig = useCallback(
    async (
      component_n: string,
      selected_component: string,
      component_config: RAGComponentConfig
    ) => {
      if (!RAGConfig) return;

      addStatusMessage("Saving " + selected_component + " config", "SUCCESS");

      const newRAGConfig = JSON.parse(JSON.stringify(RAGConfig));
      newRAGConfig[component_n].selected = selected_component;
      newRAGConfig[component_n].components[selected_component] =
        component_config;
      const response = await updateRAGConfig(newRAGConfig, credentials);
      if (response) {
        setRAGConfig(newRAGConfig);
      }
    },
    [RAGConfig, credentials]
  );

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* FileSelection Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start ">
          <InfoComponent
            tooltip_text="Configure all import settings related to chunking, embedding, adding meta data and more. You can save made changes individually or apply them to all other files"
            display_text="Import Config"
          />
        </div>
        <div className="flex gap-3 justify-end">
          <VerbaButton
            title="Overview"
            selected={selectedSetting === "Basic"}
            selected_color="bg-secondary-verba"
            onClick={() => {
              setSelectedSetting("Basic");
            }}
            Icon={IoSettingsSharp}
          />

          <VerbaButton
            title="Config"
            selected={selectedSetting === "Pipeline"}
            selected_color="bg-secondary-verba"
            onClick={() => {
              setSelectedSetting("Pipeline");
            }}
            Icon={FaHammer}
          />

          <VerbaButton
            onClick={() => {
              setSelectedFileData(null);
            }}
            Icon={MdCancel}
          />
        </div>
      </div>

      {/* File List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 items-center h-full w-full overflow-auto">
        {selectedSetting === "Basic" && (
          <BasicSettingView
            selectedFileData={selectedFileData}
            addStatusMessage={addStatusMessage}
            fileMap={fileMap}
            selectComponent={selectComponent}
            updateConfig={updateConfig}
            saveComponentConfig={saveComponentConfig}
            setFileMap={setFileMap}
            blocked={
              selectedFileData
                ? fileMap[selectedFileData].block ?? false
                : undefined
            }
          />
        )}
        {selectedSetting === "Pipeline" && selectedFileData && (
          <div className="flex flex-col gap-10 w-full">
            <ComponentView
              RAGConfig={fileMap[selectedFileData].rag_config}
              component_name="Chunker"
              selectComponent={selectComponent}
              updateConfig={updateConfig}
              saveComponentConfig={saveComponentConfig}
              blocked={fileMap[selectedFileData].block}
              skip_component={false}
            />
            <ComponentView
              RAGConfig={fileMap[selectedFileData].rag_config}
              component_name="Embedder"
              selectComponent={selectComponent}
              updateConfig={updateConfig}
              saveComponentConfig={saveComponentConfig}
              blocked={fileMap[selectedFileData].block}
              skip_component={false}
            />
          </div>
        )}
      </div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        <div className="flex gap-3 justify-end">
          <VerbaButton
            title="Apply to All"
            onClick={openApplyAllModal}
            Icon={VscSaveAll}
          />

          <VerbaButton
            title="Save Config"
            onClick={openDefaultModal}
            Icon={IoSettingsSharp}
          />

          <VerbaButton title="Reset" onClick={openResetModal} Icon={MdCancel} />
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
