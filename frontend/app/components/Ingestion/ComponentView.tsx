"use client";

import React, { useState, useEffect, useCallback } from "react";
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
  component_name: "Chunker" | "Embedder" | "Reader";
}

const ComponentView: React.FC<ComponentViewProps> = ({
  selectedFileData,
  fileMap,
  setFileMap,
  component_name,
}) => {
  const updateConfig = useCallback(
    (configKey: string, configValue: string | boolean) => {
      setFileMap((prevFileMap) => {
        if (selectedFileData) {
          const newFileMap = { ...prevFileMap };
          const selectedFile = newFileMap[selectedFileData];
          const componentConfig =
            selectedFile.rag_config[component_name].components[
              selectedFile.rag_config[component_name].selected
            ].config;

          // Update the specific config value directly
          componentConfig[configKey].value = configValue;

          return newFileMap;
        }
        return prevFileMap;
      });
    },
    [selectedFileData, component_name]
  );

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

  function renderUploadComponents(rag_config: RAGConfig, filter_url: boolean) {
    const filter = filter_url ? "URL" : "FILE";

    return Object.entries(rag_config[component_name].components)
      .filter(([key, component]) => component.type === filter)
      .map(([key, component]) => (
        <li
          key={"FilteredDropdown_" + component.name}
          onClick={() => {
            changeComponent(component.name);
            closeOnClick();
          }}
        >
          <a>{component.name}</a>
        </li>
      ));
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
        <div className="divider text-text-alt-verba">{component_name}</div>
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
              {component_name != "Reader"
                ? renderComponents(fileMap[selectedFileData].rag_config)
                : renderUploadComponents(
                    fileMap[selectedFileData].rag_config,
                    fileMap[selectedFileData].isURL
                  )}
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

        {selectedFileData &&
          Object.entries(
            fileMap[selectedFileData].rag_config[component_name].components[
              fileMap[selectedFileData].rag_config[component_name].selected
            ].config
          ).map(([configTitle, config]) => (
            <div key={"Configuration" + configTitle + component_name}>
              <div className="flex gap-3 justify-between items-center text-text-verba">
                <p className="flex min-w-[8vw]">{configTitle}</p>
                {config.type === "dropdown" && (
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
                )}

                {typeof config.value != "boolean" && (
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

                {typeof config.value === "boolean" && (
                  <input
                    type="checkbox"
                    className="checkbox checkbox-md"
                    onChange={(e) =>
                      updateConfig(
                        configTitle,
                        (e.target as HTMLInputElement).checked
                      )
                    }
                    checked={config.value}
                  />
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
