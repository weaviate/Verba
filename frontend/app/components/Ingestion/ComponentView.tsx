"use client";

import React, { useState, useEffect, use } from "react";
import { FileData, FileMap } from "./types";
import { FaTrash } from "react-icons/fa";
import { GoTriangleDown } from "react-icons/go";
import { IoAddCircleSharp } from "react-icons/io5";
import { CgDebug } from "react-icons/cg";

import UserModalComponent from "../Navigation/UserModal";
import { RAGConfig, RAGSetting, ConfigSetting } from "../RAG/types";
import { IoIosCheckmark } from "react-icons/io";
import { FaCheckCircle } from "react-icons/fa";
import { MdModeEdit } from "react-icons/md";

import { statusTextMap } from "./types";

import { closeOnClick } from "./util";

interface ComponentViewProps {
  selectedFileData: string | null;
  fileMap: FileMap;
  setFileMap: React.Dispatch<React.SetStateAction<FileMap>>;
  component_name: "Chunker" | "Embedder";
}

const ComponentView: React.FC<ComponentViewProps> = ({
  selectedFileData,
  fileMap,
  setFileMap,
  component_name,
}) => {
  const updateConfig = (configKey: string, configValue: string | number) => {
    setFileMap((prevFileMap) => {
      if (selectedFileData) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData])
        );
        const newFileMap: FileMap = { ...prevFileMap };

        newFileMap[selectedFileData].rag_config[component_name].components[
          newFileMap[selectedFileData].rag_config[component_name].selected
        ].config[configKey].value = configValue;
        newFileMap[selectedFileData] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  function renderComponents(rag_config: RAGConfig) {
    return Object.entries(rag_config[component_name].components).map(
      ([key, component]) => (
        <li
          key={"ComponentDropdown_" + component.name}
          onClick={() => {
            changeComponent(component.name);
            closeOnClick();
          }}
        >
          <a>{component.name}</a>
        </li>
      )
    );
  }

  function renderConfigOptions(rag_config: RAGConfig, configKey: string) {
    return rag_config[component_name].components[
      rag_config[component_name].selected
    ].config[configKey].values.map((configValue) => (
      <li
        key={"ConfigValue" + configValue}
        onClick={() => {
          updateConfig(configKey, configValue);
          closeOnClick();
        }}
      >
        <a>{configValue}</a>
      </li>
    ));
  }

  const changeComponent = (component: string) => {
    setFileMap((prevFileMap) => {
      if (selectedFileData) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData])
        );
        const newRAGConfig: RAGConfig = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData].rag_config)
        );
        newRAGConfig[component_name].selected = component;
        newFileData.rag_config = newRAGConfig;
        const newFileMap: FileMap = { ...prevFileMap };
        newFileMap[selectedFileData] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  if (selectedFileData) {
    return (
      <div className="flex flex-col justify-start gap-3 rounded-2xl p-1 w-full ">
        {/* Component */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">{component_name}</p>
          <div className="dropdown dropdown-bottom flex justify-start items-center w-full">
            <button
              tabIndex={0}
              role="button"
              className="btn bg-button-verba hover:bg-button-hover-verba text-text-verba w-full flex justify-start border-none"
            >
              <GoTriangleDown size={15} />
              <p>
                {fileMap[selectedFileData].rag_config[component_name].selected}
              </p>
            </button>
            <ul
              tabIndex={0}
              className="dropdown-content menu bg-base-100 rounded-box z-[1] w-full p-2 shadow"
            >
              {renderComponents(fileMap[selectedFileData].rag_config)}
            </ul>
          </div>
        </div>

        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]"></p>
          <p className="text-sm text-text-alt-verba text-start">
            {selectedFileData &&
              fileMap[selectedFileData].rag_config[component_name].components[
                fileMap[selectedFileData].rag_config[component_name].selected
              ].description}
          </p>
        </div>

        <div className="divider"></div>

        {selectedFileData &&
          Object.entries(
            fileMap[selectedFileData].rag_config[component_name].components[
              fileMap[selectedFileData].rag_config[component_name].selected
            ].config
          ).map(([configTitle, config]) => (
            <div>
              <div className="flex gap-2 justify-between items-center text-text-verba">
                <p className="flex min-w-[8vw]">{configTitle}</p>
                {config.type === "dropdown" ? (
                  <div className="dropdown dropdown-bottom flex justify-start items-center w-full">
                    <button
                      tabIndex={0}
                      role="button"
                      className="btn bg-button-verba hover:bg-button-hover-verba text-text-verba w-full flex justify-start border-none"
                    >
                      <GoTriangleDown size={15} />
                      <p>{config.value}</p>
                    </button>
                    <ul
                      tabIndex={0}
                      className="dropdown-content menu bg-base-100 rounded-box z-[1] w-full p-2 shadow"
                    >
                      {renderConfigOptions(
                        fileMap[selectedFileData].rag_config,
                        configTitle
                      )}
                    </ul>
                  </div>
                ) : (
                  <label className="input flex items-center gap-2 w-full bg-bg-verba">
                    <input
                      type={config.type}
                      className="grow w-full"
                      value={config.value}
                      onChange={(e) => {
                        updateConfig(configTitle, e.target.value);
                      }}
                    />
                  </label>
                )}
              </div>
              <div className="flex gap-2 items-center text-text-verba">
                <p className="flex min-w-[8vw]"></p>
                <p className="text-sm text-text-alt-verba text-start">
                  {config.description}
                </p>
              </div>
            </div>
          ))}
      </div>
    );
  } else {
    return <div></div>;
  }
};

export default ComponentView;
