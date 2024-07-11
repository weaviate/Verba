"use client";

import React, { useState, useEffect, use } from "react";
import FileComponent from "./FileComponent";
import InfoComponent from "../Navigation/InfoComponent";
import { SettingsConfiguration } from "../Settings/types";
import { IoMdAddCircle } from "react-icons/io";
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";
import { GoFileDirectoryFill } from "react-icons/go";

import { closeOnClick } from "./util";

import UserModalComponent from "../Navigation/UserModal";

import { FileMap, FileData } from "./types";
import { RAGConfig } from "../RAG/types";

interface FileSelectionViewProps {
  settingConfig: SettingsConfiguration;
  fileMap: FileMap;
  setFileMap: (f: FileMap) => void;
  RAGConfig: RAGConfig | null;
  setRAGConfig: (r_: RAGConfig | null) => void;
  selectedFileData: string | null;
  setSelectedFileData: (f: string | null) => void;
}

const FileSelectionView: React.FC<FileSelectionViewProps> = ({
  settingConfig,
  fileMap,
  setFileMap,
  RAGConfig,
  setRAGConfig,
  selectedFileData,
  setSelectedFileData,
}) => {
  const ref = React.useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current !== null) {
      ref.current.setAttribute("directory", "");
      ref.current.setAttribute("webkitdirectory", "");
    }
  }, [ref]);

  const openDeleteModal = () => {
    const modal = document.getElementById("remove_all_files");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const handleDeleteFile = (filename: string | null) => {
    if (filename === null) {
      setSelectedFileData(null);
      setFileMap({});
    } else {
      const newFileMap = { ...fileMap };
      delete newFileMap[filename];

      if (filename === selectedFileData) {
        setSelectedFileData(null);
      }

      setFileMap(newFileMap);
    }
  };

  const handleUploadFiles = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (event.target.files && RAGConfig) {
      const files = event.target.files;
      const newFileMap: FileMap = { ...fileMap };

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const newRAGConfig: RAGConfig = JSON.parse(JSON.stringify(RAGConfig));
        const filename = file.name;
        const fileID = file.name;
        const extension = file.name.split(".").pop() || "";
        const fileContent = await readFileContent(file);

        newFileMap[fileID] = {
          fileID,
          filename,
          extension,
          isURL: false,
          overwrite: false,
          content: fileContent,
          labels: ["Document"],
          rag_config: newRAGConfig,
          file_size: calculateBytesFromHexString(fileContent),
          status: "READY",
        };
      }

      setFileMap(newFileMap);

      event.target.value = "";
    }
  };

  const handleAddURL = (URLReader: string) => {
    if (RAGConfig) {
      const newFileMap: FileMap = { ...fileMap };
      const newRAGConfig: RAGConfig = JSON.parse(JSON.stringify(RAGConfig));
      newRAGConfig["Reader"].selected = URLReader;

      const now = new Date();
      const filename = now.toISOString();
      const fileID = filename;
      const extension = "URL";

      newFileMap[fileID] = {
        fileID,
        filename,
        extension,
        isURL: true,
        overwrite: false,
        content: "",
        labels: ["Document"],
        rag_config: newRAGConfig,
        file_size: 0,
        status: "READY",
      };

      setFileMap(newFileMap);
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target && event.target.result instanceof ArrayBuffer) {
          const arrayBuffer = event.target.result;
          const byteArray = new Uint8Array(arrayBuffer);
          const byteString = Array.from(byteArray)
            .map((byte) => byte.toString(16).padStart(2, "0"))
            .join(" ");
          resolve(byteString);
        } else {
          reject(new Error("Failed to read file content"));
        }
      };
      reader.onerror = (event) => {
        reject(new Error("Error reading file: " + event.target?.error));
      };
      reader.readAsArrayBuffer(file);
    });
  };

  const calculateBytesFromHexString = (hexString: string): number => {
    // Each byte is represented by two hex characters and a space
    const bytes = hexString.split(" ").length;
    return bytes;
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* FileSelection Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start ">
          <InfoComponent
            settingConfig={settingConfig}
            tooltip_text="Upload your data through this interface into Verba. You can select individual files, directories or add URL to fetch data from."
            display_text="File Selection"
          />
        </div>
        <div className="flex gap-3 justify-end">
          <button
            onClick={() => document.getElementById("files_upload")?.click()}
            className="flex border-none btn text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
          >
            <IoMdAddCircle size={15} />
            <p>Add Files</p>
          </button>
          <input
            id={"files_upload"}
            type="file"
            onChange={handleUploadFiles}
            className="hidden"
            multiple
          />
          <button
            onClick={() => document.getElementById("dir_upload")?.click()}
            className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
          >
            <GoFileDirectoryFill size={15} />
            <p>Add Directory</p>
          </button>
          <input
            id={"dir_upload"}
            type="file"
            ref={ref}
            onChange={handleUploadFiles}
            className="hidden"
            multiple
          />
          <div className="dropdown dropdown-bottom">
            <button
              tabIndex={0}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
            >
              <IoMdAddCircle size={15} />
              <p>Add URL</p>
            </button>
            <ul
              tabIndex={0}
              className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
            >
              {RAGConfig &&
                Object.entries(RAGConfig["Reader"].components)
                  .filter(([key, component]) => component.type === "URL")
                  .map(([key, component]) => (
                    <li
                      key={"URL_" + component.name + key}
                      onClick={() => {
                        handleAddURL(component.name);
                        closeOnClick();
                      }}
                    >
                      <a>{component.name}</a>
                    </li>
                  ))}
            </ul>
          </div>
        </div>
      </div>

      {/* File List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 items-center h-full w-full overflow-auto">
        {Object.entries(fileMap).map(([key, fileData]) => (
          <FileComponent
            key={"FileComponent_" + key}
            fileData={fileData}
            handleDeleteFile={handleDeleteFile}
            selectedFileData={selectedFileData}
            setSelectedFileData={setSelectedFileData}
            fileMap={fileMap}
            setFileMap={setFileMap}
          />
        ))}
      </div>

      {/* Import Footer */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        <div className="flex gap-3 justify-end">
          {selectedFileData && (
            <button className="flex btn border-none text-text-verba bg-secondary-verba hover:bg-button-hover-verba gap-2">
              <FaFileImport size={15} />
              <p>Import Selected</p>
            </button>
          )}
          <button className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2">
            <FaFileImport size={15} />
            <p>Import All</p>
          </button>
          <button
            onClick={openDeleteModal}
            className="flex btn border-none text-text-verba bg-button-verba hover:bg-warning-verba gap-2"
          >
            <MdCancel size={15} />
            <p>Clear Files</p>
          </button>
        </div>
      </div>
      <UserModalComponent
        modal_id={"remove_all_files"}
        title={"Clear all files?"}
        text={"Do you want to clear all files from your selection?"}
        triggerString="Clear All"
        triggerValue={null}
        triggerAccept={handleDeleteFile}
      />
    </div>
  );
};

export default FileSelectionView;
