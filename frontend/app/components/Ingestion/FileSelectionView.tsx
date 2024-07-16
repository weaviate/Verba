"use client";

import React, { useState, useEffect, use } from "react";
import FileComponent from "./FileComponent";
import InfoComponent from "../Navigation/InfoComponent";
import { SettingsConfiguration } from "../Settings/types";
import { IoMdAddCircle } from "react-icons/io";
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";
import { GoFileDirectoryFill } from "react-icons/go";
import { TbPlugConnected } from "react-icons/tb";

import { closeOnClick } from "./util";

import UserModalComponent from "../Navigation/UserModal";

import { FileMap, FileData } from "./types";
import { RAGConfig } from "../RAG/types";

interface FileSelectionViewProps {
  settingConfig: SettingsConfiguration;
  fileMap: FileMap;
  setFileMap: React.Dispatch<React.SetStateAction<FileMap>>;
  RAGConfig: RAGConfig | null;
  setRAGConfig: (r_: RAGConfig | null) => void;
  selectedFileData: string | null;
  setSelectedFileData: (f: string | null) => void;
  importSelected: () => void;
  importAll: () => void;
  reconnect: () => void;
  socketStatus: "ONLINE" | "OFFLINE";
}

const FileSelectionView: React.FC<FileSelectionViewProps> = ({
  settingConfig,
  fileMap,
  setFileMap,
  RAGConfig,
  setRAGConfig,
  selectedFileData,
  setSelectedFileData,
  importSelected,
  socketStatus,
  reconnect,
  importAll,
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
    setFileMap((prevFileMap: FileMap): FileMap => {
      if (filename === null) {
        setSelectedFileData(null);
        return {};
      } else {
        if (filename === selectedFileData) {
          setSelectedFileData(null);
        }
        const newFileMap: FileMap = { ...prevFileMap };
        delete newFileMap[filename];
        return newFileMap;
      }
    });
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
          status_report: {},
          source: "",
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
        status_report: {},
        extension,
        isURL: true,
        source: "",
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

  function arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary); // Encode the binary string to base64
  }

  function readFileContent(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const arrayBuffer = reader.result as ArrayBuffer;
        const content = arrayBufferToBase64(arrayBuffer);
        resolve(content); // Resolve with the base64 content
      };
      reader.onerror = () => reject(reader.error);
      reader.readAsArrayBuffer(file);
    });
  }

  const calculateBytesFromHexString = (hexString: string): number => {
    // Remove any spaces from the hex string
    const cleanedHexString = hexString.replace(/\s+/g, "");

    // Ensure the string length is even (two characters per byte)
    if (cleanedHexString.length % 2 !== 0) {
      throw new Error("Invalid hex string length.");
    }

    // Each byte is represented by two hex characters
    const bytes = cleanedHexString.length / 2;
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
      {socketStatus === "ONLINE" ? (
        <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
          <div className="flex gap-3 justify-end">
            {selectedFileData && (
              <button
                onClick={importSelected}
                className="flex btn border-none text-text-verba bg-secondary-verba hover:bg-button-hover-verba gap-2"
              >
                <FaFileImport size={15} />
                <p>Import Selected</p>
              </button>
            )}
            <button
              onClick={importAll}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
            >
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
      ) : (
        <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
          <div className="flex gap-3 justify-end">
            <button
              onClick={reconnect}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
            >
              <TbPlugConnected size={15} />
              <p>Reconnect to Verba</p>
            </button>
          </div>
        </div>
      )}

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
