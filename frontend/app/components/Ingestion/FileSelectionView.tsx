"use client";

import React, { useState, useEffect } from "react";
import FileComponent from "./FileComponent";
import InfoComponent from "../Navigation/InfoComponent";
import { IoMdAddCircle } from "react-icons/io";
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";
import { GoFileDirectoryFill } from "react-icons/go";
import { TbPlugConnected } from "react-icons/tb";
import { IoMdArrowDropdown } from "react-icons/io";

import { closeOnClick } from "@/app/util";

import UserModalComponent from "../Navigation/UserModal";

import VerbaButton from "../Navigation/VerbaButton";

import { FileMap } from "@/app/types";
import { RAGConfig } from "@/app/types";

interface FileSelectionViewProps {
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
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const FileSelectionView: React.FC<FileSelectionViewProps> = ({
  fileMap,
  setFileMap,
  RAGConfig,
  addStatusMessage,
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
        addStatusMessage("Cleared all files", "WARNING");
        setSelectedFileData(null);
        return {};
      } else {
        if (filename === selectedFileData) {
          setSelectedFileData(null);
        }
        addStatusMessage("Cleared selected file", "WARNING");
        const newFileMap: FileMap = { ...prevFileMap };
        delete newFileMap[filename];
        return newFileMap;
      }
    });
  };

  const [selectedFileReader, setSelectedFileReader] = useState<string | null>(
    null
  );
  const [selectedDirReader, setSelectedDirReader] = useState<string | null>(
    null
  );

  const handleUploadFiles = async (
    event: React.ChangeEvent<HTMLInputElement>,
    isDirectory: boolean
  ) => {
    if (event.target.files && RAGConfig) {
      const files = event.target.files;
      const newFileMap: FileMap = { ...fileMap };
      const selectedReader = isDirectory
        ? selectedDirReader
        : selectedFileReader;

      addStatusMessage("Added new files", "SUCCESS");

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const newRAGConfig: RAGConfig = JSON.parse(JSON.stringify(RAGConfig));
        if (selectedReader) {
          newRAGConfig["Reader"].selected = selectedReader;
        }
        const filename = file.name;
        let fileID = file.name;

        // Check if the fileID already exists in the map
        if (fileID in newFileMap) {
          // If it exists, append a timestamp to make it unique
          const timestamp = Date.now();
          fileID = `${fileID}_${timestamp}`;
        }

        const extension = file.name.split(".").pop() || "";
        const fileContent = await readFileContent(file);

        newFileMap[fileID] = {
          fileID,
          filename,
          extension,
          status_report: {},
          source: "",
          isURL: false,
          metadata: "",
          overwrite: false,
          content: fileContent,
          labels: ["Document"],
          rag_config: newRAGConfig,
          file_size: calculateBytesFromHexString(fileContent),
          status: "READY",
        };
      }

      setFileMap(newFileMap);
      setSelectedFileData(Object.keys(newFileMap)[0]);

      event.target.value = "";
    }
  };

  const handleAddURL = (URLReader: string) => {
    if (RAGConfig) {
      const newFileMap: FileMap = { ...fileMap };
      const newRAGConfig: RAGConfig = JSON.parse(JSON.stringify(RAGConfig));
      newRAGConfig["Reader"].selected = URLReader;

      const now = new Date();
      const filename = "New " + URLReader + " Job";
      const fileID = now.toISOString();
      const extension = "URL";

      addStatusMessage("Added new URL Job", "SUCCESS");

      newFileMap[fileID] = {
        fileID,
        filename,
        metadata: "",
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
      setSelectedFileData(fileID);
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
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end lg:justify-between h-min w-full">
        <div className="hidden lg:flex gap-2 justify-start ">
          <InfoComponent
            tooltip_text="Upload your data through this interface into Verba. You can select individual files, directories or add URL to fetch data from."
            display_text="File Selection"
          />
        </div>
        <div className="flex gap-3 justify-center lg:justify-end">
          <div className="dropdown dropdown-hover">
            <label tabIndex={0}>
              <VerbaButton
                title="Files"
                Icon={IoMdAddCircle}
                onClick={() => document.getElementById("files_upload")?.click()}
              />
            </label>
            <ul
              tabIndex={0}
              className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
            >
              {RAGConfig &&
                Object.entries(RAGConfig["Reader"].components)
                  .filter(([key, component]) => component.type !== "URL")
                  .map(([key, component]) => (
                    <li
                      key={"File_" + component.name + key}
                      onClick={() => {
                        setSelectedFileReader(component.name);
                        document.getElementById("files_upload")?.click();
                        closeOnClick();
                      }}
                    >
                      <a>{component.name}</a>
                    </li>
                  ))}
            </ul>
          </div>
          <input
            id={"files_upload"}
            type="file"
            onChange={(e) => handleUploadFiles(e, false)}
            className="hidden"
            multiple
          />

          <div className="dropdown dropdown-hover">
            <label tabIndex={0}>
              <VerbaButton title="Directory" Icon={GoFileDirectoryFill} />
            </label>
            <ul
              tabIndex={0}
              className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
            >
              {RAGConfig &&
                Object.entries(RAGConfig["Reader"].components)
                  .filter(([key, component]) => component.type !== "URL")
                  .map(([key, component]) => (
                    <li
                      key={"Dir_" + component.name + key}
                      onClick={() => {
                        setSelectedDirReader(component.name);
                        document.getElementById("dir_upload")?.click();
                        closeOnClick();
                      }}
                    >
                      <a>{component.name}</a>
                    </li>
                  ))}
            </ul>
          </div>
          <input
            id={"dir_upload"}
            type="file"
            ref={ref}
            onChange={(e) => handleUploadFiles(e, true)}
            className="hidden"
            multiple
          />

          <div className="dropdown dropdown-hover">
            <label tabIndex={0}>
              <VerbaButton title="URL" Icon={IoMdAddCircle} />
            </label>
            <input id={"url_upload"} type="file" className="hidden" />
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
          />
        ))}
      </div>

      {/* Import Footer */}
      {socketStatus === "ONLINE" ? (
        <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
          <div className="flex flex-wrap gap-3 justify-end">
            {selectedFileData && (
              <VerbaButton
                title="Import Selected"
                Icon={FaFileImport}
                onClick={importSelected}
              />
            )}
            <VerbaButton
              title="Import All"
              Icon={FaFileImport}
              onClick={importAll}
            />

            <VerbaButton
              title="Clear Files"
              Icon={MdCancel}
              onClick={openDeleteModal}
            />
          </div>
        </div>
      ) : (
        <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
          <div className="flex gap-3 justify-end">
            <button
              onClick={reconnect}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2 items-center"
            >
              <TbPlugConnected size={15} />
              <p>Reconnecting...</p>
              <span className="loading loading-spinner loading-xs"></span>
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
