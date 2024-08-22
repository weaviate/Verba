"use client";

import React from "react";
import { MdCancel } from "react-icons/md";
import { IoSettingsSharp } from "react-icons/io5";
import { RAGConfig } from "@/app/api_types";
import ComponentView from "../Ingestion/ComponentView";

interface ChatConfigProps {
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  onSave: () => void; // New parameter for handling save
  onReset: () => void; // New parameter for handling reset
}

const ChatConfig: React.FC<ChatConfigProps> = ({
  RAGConfig,
  setRAGConfig,
  onSave,
  onReset,
}) => {
  const updateConfig = (
    component_n: string,
    configTitle: string,
    value: string | boolean | string[]
  ) => {
    setRAGConfig((prevRAGConfig) => {
      if (prevRAGConfig) {
        const newRAGConfig = { ...prevRAGConfig };
        if (typeof value === "string" || typeof value === "boolean") {
          newRAGConfig[component_n].components[
            newRAGConfig[component_n].selected
          ].config[configTitle].value = value;
        } else {
          newRAGConfig[component_n].components[
            newRAGConfig[component_n].selected
          ].config[configTitle].values = value;
        }
        return newRAGConfig;
      }
      return prevRAGConfig;
    });
  };

  const selectComponent = (component_n: string, selected_component: string) => {
    setRAGConfig((prevRAGConfig) => {
      if (prevRAGConfig) {
        const newRAGConfig = { ...prevRAGConfig };
        newRAGConfig[component_n].selected = selected_component;
        return newRAGConfig;
      }
      return prevRAGConfig;
    });
  };

  if (RAGConfig) {
    return (
      <div className="flex flex-col justify-start gap-3 rounded-2xl p-1 w-full ">
        <ComponentView
          RAGConfig={RAGConfig}
          component_name="Embedder"
          selectComponent={selectComponent}
          updateConfig={updateConfig}
          blocked={false}
        />
        <ComponentView
          RAGConfig={RAGConfig}
          component_name="Generator"
          selectComponent={selectComponent}
          updateConfig={updateConfig}
          blocked={false}
        />
        <ComponentView
          RAGConfig={RAGConfig}
          component_name="Retriever"
          selectComponent={selectComponent}
          updateConfig={updateConfig}
          blocked={false}
        />

        {/* Add Save and Reset buttons */}
        <div className="flex justify-end gap-2 mt-4">
          <button
            onClick={onSave}
            className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
          >
            <IoSettingsSharp size={15} />
            <p>Set as Default</p>
          </button>
          <button
            onClick={onReset}
            className="flex btn border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2"
          >
            <MdCancel size={15} />
            <p>Reset</p>
          </button>
        </div>
      </div>
    );
  } else {
    return <div></div>;
  }
};

export default ChatConfig;
