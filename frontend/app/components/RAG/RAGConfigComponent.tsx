"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";

import { RAGConfig, RAGComponentClass } from "./types";

import { TextFieldSetting, NumberFieldSetting } from "../Settings/types";

import { FaCheck } from "react-icons/fa";

import TextFieldRAGComponent from "./TextFieldRAGComponent";
import NumberFieldRAGComponent from "./NumberFieldRAGComponent";
import { text } from "stream/consumers";

interface RAGConfigComponentProps {
  settingConfig: SettingsConfiguration;
  APIHost: string | null;
  files: FileList | null;
  RAGConfig: RAGConfig;
  RAGConfigTitle: string;
  RAGComponents: RAGComponentClass;
  setRAGConfig: (r_: any) => void;
  setFiles: (f: FileList | null) => void;
  setTextValues: (t: string[]) => void;
  textValues: string[];
}

const RAGConfigComponent: React.FC<RAGConfigComponentProps> = ({
  APIHost,
  files,
  settingConfig,
  textValues,
  RAGConfig,
  RAGConfigTitle,
  RAGComponents,
  setRAGConfig,
  setFiles,
  setTextValues,
}) => {
  const [currentText, setCurrentText] = useState(
    textValues ? textValues[0] : ""
  );

  const onSelectComponent = (_selected: string) => {
    setRAGConfig((prevConfig: any) => {
      const newConfig = JSON.parse(JSON.stringify(prevConfig));
      newConfig[RAGConfigTitle].selected = _selected;
      return newConfig;
    });
  };

  const handleUploadFiles = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFiles(event.target.files);
    }
  };

  const renderSettingComponent = (
    title: any,
    setting_type: TextFieldSetting | NumberFieldSetting
  ) => {
    if (!RAGConfig) {
      return null;
    }

    switch (setting_type.type) {
      case "text":
        return (
          <TextFieldRAGComponent
            title={title}
            RAGConfig={RAGConfig}
            TextFieldSetting={setting_type}
            RAGComponentTitle={RAGComponents.selected}
            RAGConfigTitle={RAGConfigTitle}
            setRAGConfig={setRAGConfig}
          />
        );
      case "number":
        return (
          <NumberFieldRAGComponent
            title={title}
            RAGConfig={RAGConfig}
            NumberFieldSetting={setting_type}
            RAGComponentTitle={RAGComponents.selected}
            RAGConfigTitle={RAGConfigTitle}
            setRAGConfig={setRAGConfig}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex sm:flex-col md:flex-row justify-center items-start gap-3 w-full">
      <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 h-[65vh] overflow-auto w-full">
        <div className="flex flex-col">
          <p className="text-lg">Select a {RAGConfigTitle}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
          {RAGComponents &&
            Object.entries(RAGComponents.components).map(([key, value]) => (
              <button
                key={"Component_" + key}
                disabled={!value.available}
                onClick={() => {
                  onSelectComponent(key);
                }}
                className={`btn border-none ${value.available ? "flex" : "hidden"} ${key === RAGComponents.selected ? "bg-secondary-verba text-text-verba" : "bg-button-verba text-text-alt-verba"} hover:bg-button-hover-verba `}
              >
                <p>{key}</p>
              </button>
            ))}
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex lg:flex-row flex-col gap-1">
            <p className="lg:text-base text-xs">You selected: </p>
            <p className="font-bold lg:text-base text-sm">
              {RAGComponents.selected}
            </p>
          </div>
          <p className="text-sm text-text-alt-verba">
            {RAGComponents.components[RAGComponents.selected].description}
          </p>
        </div>

        <div className=" flex-col gap-4 grid grid-cols-1 lg:grid-cols-1">
          {RAGConfig &&
            Object.entries(
              RAGComponents.components[RAGComponents.selected].config
            ).map(([key, settingValue]) =>
              renderSettingComponent(key, settingValue)
            )}
        </div>

        {RAGComponents.components[RAGComponents.selected].type === "UPLOAD" && (
          <div className="flex lg:flex-row flex-col gap-3">
            <div className="flex flex-col gap-2 items-center">
              <div className="flex">
                <button
                  onClick={() =>
                    document
                      .getElementById(
                        RAGConfigTitle + RAGComponents.selected + "_upload"
                      )
                      ?.click()
                  }
                  className="btn border-none bg-button-verba hover:bg-secondary-verba text-text-verba"
                >
                  Add Files
                </button>
                <input
                  id={RAGConfigTitle + RAGComponents.selected + "_upload"}
                  type="file"
                  value={files ? undefined : ""}
                  onChange={handleUploadFiles}
                  className="hidden"
                  multiple
                />
              </div>
              {files && (
                <div className="flex">
                  <button
                    onClick={() => {
                      setFiles(null);
                    }}
                    className="btn text-sm border-none bg-warning-verba hover:bg-button-hover-verba "
                  >
                    Clear Files
                  </button>
                </div>
              )}
            </div>
            {files && (
              <div className="flex gap-2">
                <p className="flex text-text-alt-verba text-sm ">Files:</p>
                <div className="flex flex-col gap-1 overflow-y-auto h-[15vh] border-2 p-2 rounded-lg border-bg-verba">
                  {files &&
                    Array.from(files).map((file, index) => (
                      <p key={index + file.name}>{file.name}</p>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {RAGComponents.components[RAGComponents.selected].type === "URL" && (
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-center">
              {(textValues.length > 0 && currentText !== textValues[0]) ||
              (currentText != "" && textValues.length <= 0) ? (
                <p>*Enter URL</p>
              ) : (
                <p>Enter URL</p>
              )}
            </div>
            <div className="flex flex-row gap-2 w-full items-center justify-center">
              <div className="flex flex-col items-center justify-center gap-1 w-full">
                <label className="input input-bordered flex items-center w-full bg-bg-verba">
                  <input
                    type="text"
                    className="grow"
                    value={currentText}
                    onChange={(e) => {
                      setCurrentText(e.target.value);
                    }}
                  />
                </label>
              </div>
              <button
                onClick={() => {
                  setTextValues([currentText]);
                }}
                className="btn bg-bg-verba border-none hover:bg-secondary-verba"
              >
                <FaCheck />
              </button>
            </div>
          </div>
        )}

        <div></div>
      </div>
    </div>
  );
};

export default RAGConfigComponent;
