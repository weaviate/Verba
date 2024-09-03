"use client";

import React, { useState, useEffect } from "react";
import { FaTrash } from "react-icons/fa";
import { GoTriangleDown } from "react-icons/go";
import { IoAddCircleSharp } from "react-icons/io5";
import { RAGConfig, RAGComponentConfig } from "@/app/types";

import { closeOnClick } from "@/app/util";

import VerbaButton from "../Navigation/VerbaButton";

export const MultiInput: React.FC<{
  component_name: string;
  values: string[];
  blocked: boolean | undefined;
  config_title: string;
  updateConfig: (
    component_n: string,
    configTitle: string,
    value: string | boolean | string[]
  ) => void;
}> = ({ values, config_title, updateConfig, component_name, blocked }) => {
  const [currentInput, setCurrentInput] = useState("");
  const [currentValues, setCurrentValues] = useState(values);

  useEffect(() => {
    updateConfig(component_name, config_title, currentValues);
  }, [currentValues]);

  const addValue = (v: string) => {
    if (!currentValues.includes(v)) {
      setCurrentValues((prev) => [...prev, v]);
      setCurrentInput("");
    }
  };

  const removeValue = (v: string) => {
    if (currentValues.includes(v)) {
      setCurrentValues((prev) => prev.filter((label) => label !== v));
    }
  };

  return (
    <div className="flex flex-col w-full gap-2">
      <div className="flex gap-2 justify-between">
        <label className="input flex items-center gap-2 w-full bg-bg-verba">
          <input
            type="text"
            className="grow w-full"
            disabled={blocked}
            value={currentInput}
            onChange={(e) => {
              setCurrentInput(e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addValue(currentInput);
              }
            }}
          />
        </label>
        <button
          onClick={() => {
            addValue(currentInput);
          }}
          disabled={blocked}
          className="btn flex gap-2 bg-button-verba border-none hover:bg-secondary-verba text-text-verba"
        >
          <IoAddCircleSharp size={15} />
          <p>Add</p>
        </button>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {values.map((value, index) => (
          <div
            key={value + index}
            className="flex bg-bg-verba w-full p-2 text-center text-sm text-text-verba justify-between items-center rounded-xl"
          >
            <div className="flex w-full justify-center items-center overflow-hidden">
              <p className="truncate" title={value}>
                {value}
              </p>
            </div>
            <button
              disabled={blocked}
              onClick={() => {
                removeValue(value);
              }}
              className="btn btn-sm btn-square bg-button-verba border-none hover:bg-warning-verba text-text-verba ml-2"
            >
              <FaTrash size={12} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

interface ComponentViewProps {
  RAGConfig: RAGConfig;
  blocked: boolean | undefined;
  component_name: "Chunker" | "Embedder" | "Reader" | "Generator" | "Retriever";
  selectComponent: (component_n: string, selected_component: string) => void;
  skip_component?: boolean;
  updateConfig: (
    component_n: string,
    configTitle: string,
    value: string | boolean | string[]
  ) => void;
  saveComponentConfig: (
    component_n: string,
    selected_component: string,
    config: RAGComponentConfig
  ) => void;
}

const ComponentView: React.FC<ComponentViewProps> = ({
  RAGConfig,
  component_name,
  selectComponent,
  updateConfig,
  saveComponentConfig,
  blocked,
  skip_component,
}) => {
  function renderComponents(rag_config: RAGConfig) {
    return Object.entries(rag_config[component_name].components)
      .filter(([key, component]) => component.available)
      .map(([key, component]) => (
        <li
          key={"ComponentDropdown_" + component.name}
          onClick={() => {
            if (!blocked) {
              selectComponent(component_name, component.name);
              closeOnClick();
            }
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
        className="lg:text-base text-sm"
        onClick={() => {
          if (!blocked) {
            updateConfig(component_name, configKey, configValue);
            closeOnClick();
          }
        }}
      >
        <a>{configValue}</a>
      </li>
    ));
  }

  if (
    Object.entries(
      RAGConfig[component_name].components[RAGConfig[component_name].selected]
        .config
    ).length == 0 &&
    skip_component
  ) {
    return <></>;
  }

  return (
    <div className="flex flex-col justify-start gap-3 rounded-2xl p-1 w-full ">
      <div className="flex items-center justify-between">
        <div className="divider text-text-alt-verba flex-grow text-xs lg:text-sm">
          <p>{RAGConfig[component_name].selected} Settings</p>
          <VerbaButton
            title="Save"
            className="btn-sm lg:text-sm text-xs"
            text_size=""
            onClick={() => {
              saveComponentConfig(
                component_name,
                RAGConfig[component_name].selected,
                RAGConfig[component_name].components[
                  RAGConfig[component_name].selected
                ]
              );
            }}
          />
        </div>
      </div>
      {/* Component */}
      {!skip_component && (
        <div className="flex flex-col gap-2">
          <div className="flex gap-2 justify-between items-center text-text-verba">
            <p className="flex min-w-[8vw] lg:text-base text-sm">
              {component_name}
            </p>
            <div className="dropdown dropdown-bottom flex justify-start items-center w-full">
              <button
                tabIndex={0}
                role="button"
                disabled={blocked}
                className="btn bg-button-verba hover:bg-button-hover-verba text-text-verba w-full flex justify-start border-none"
              >
                <GoTriangleDown size={15} />
                <p>{RAGConfig[component_name].selected}</p>
              </button>
              <ul
                tabIndex={0}
                className="dropdown-content menu bg-base-100 rounded-box z-[1] w-full p-2 shadow"
              >
                {renderComponents(RAGConfig)}
              </ul>
            </div>
          </div>

          <div className="flex gap-2 items-center text-text-verba">
            <p className="flex min-w-[8vw]"></p>
            <p className="lg:text-sm text-xs text-text-alt-verba text-start">
              {
                RAGConfig[component_name].components[
                  RAGConfig[component_name].selected
                ].description
              }
            </p>
          </div>
        </div>
      )}

      {Object.entries(
        RAGConfig[component_name].components[RAGConfig[component_name].selected]
          .config
      ).map(([configTitle, config]) => (
        <div key={"Configuration" + configTitle + component_name}>
          <div className="flex gap-3 justify-between items-center text-text-verba lg:text-base text-sm">
            <p className="flex min-w-[8vw]">{configTitle}</p>

            {/* Dropdown */}
            {config.type === "dropdown" && (
              <div className="dropdown dropdown-bottom flex justify-start items-center w-full">
                <button
                  tabIndex={0}
                  role="button"
                  disabled={blocked}
                  className="btn bg-button-verba hover:bg-button-hover-verba text-text-verba w-full flex justify-start border-none"
                >
                  <GoTriangleDown size={15} />
                  <p>{config.value}</p>
                </button>
                <ul
                  tabIndex={0}
                  className="dropdown-content menu bg-base-100 max-h-[20vh] overflow-auto rounded-box z-[1] w-full p-2 shadow"
                >
                  {renderConfigOptions(RAGConfig, configTitle)}
                </ul>
              </div>
            )}

            {/* Text Input */}
            {typeof config.value != "boolean" &&
              ["text", "number", "password"].includes(config.type) && (
                <label className="input flex text-sm items-center gap-2 w-full bg-bg-verba">
                  <input
                    type={config.type}
                    className="grow w-full"
                    value={config.value}
                    onChange={(e) => {
                      if (!blocked) {
                        updateConfig(
                          component_name,
                          configTitle,
                          e.target.value
                        );
                      }
                    }}
                  />
                </label>
              )}

            {/* Multi Input */}
            {typeof config.value != "boolean" && config.type == "multi" && (
              <MultiInput
                component_name={component_name}
                values={config.values}
                config_title={configTitle}
                updateConfig={updateConfig}
                blocked={blocked}
              />
            )}

            {/* Checkbox Input */}
            {config.type == "bool" && (
              <div className="flex gap-5 justify-start items-center w-full my-4">
                <p className="lg:text-sm text-xs text-text-alt-verba text-start w-[250px]">
                  {config.description}
                </p>
                <input
                  type="checkbox"
                  className="checkbox checkbox-md"
                  onChange={(e) => {
                    if (!blocked) {
                      updateConfig(
                        component_name,
                        configTitle,
                        (e.target as HTMLInputElement).checked
                      );
                    }
                  }}
                  checked={
                    typeof config.value === "boolean" ? config.value : false
                  }
                />
              </div>
            )}
          </div>
          {config.type != "bool" && (
            <div className="flex gap-2 items-center text-text-verba">
              <p className="flex min-w-[8vw]"></p>
              <p className="lg:text-sm text-xs text-text-alt-verba text-start">
                {config.description}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ComponentView;
