"use client";

import React, { useState, useEffect, useCallback } from "react";
import { FaTrash } from "react-icons/fa";
import { GoTriangleDown } from "react-icons/go";
import { IoAddCircleSharp } from "react-icons/io5";
import { CgDebug } from "react-icons/cg";

import { MultiInput } from "../Ingestion/ComponentView";

import UserModalComponent from "../Navigation/UserModal";
import { RAGConfig, RAGSetting, ConfigSetting } from "../RAG/types";
import { IoIosCheckmark } from "react-icons/io";
import { FaCheckCircle } from "react-icons/fa";
import { MdModeEdit } from "react-icons/md";

import ComponentView from "../Ingestion/ComponentView";

import { closeOnClick } from "../Ingestion/util";

interface ChatConfigProps {
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
}

const ChatConfig: React.FC<ChatConfigProps> = ({ RAGConfig, setRAGConfig }) => {
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
      </div>
    );
  } else {
    return <div></div>;
  }
};

export default ChatConfig;
