"use client";

import React, { useState, useEffect, use } from "react";
import { FileData, FileMap } from "./types";
import { FaTrash } from "react-icons/fa";
import { GoTriangleDown } from "react-icons/go";
import { IoAddCircleSharp } from "react-icons/io5";
import { CgDebug } from "react-icons/cg";

import UserModalComponent from "../Navigation/UserModal";
import { RAGConfig } from "../RAG/types";
import { IoIosCheckmark } from "react-icons/io";
import { MdModeEdit } from "react-icons/md";

import { closeOnClick } from "./util";

interface BasicSettingViewProps {
  selectedFileData: string | null;
  setSelectedFileData: (f: string | null) => void;
  fileMap: FileMap;
  setFileMap: (f: FileMap) => void;
}

const BasicSettingView: React.FC<BasicSettingViewProps> = ({
  selectedFileData,
  setSelectedFileData,
  fileMap,
  setFileMap,
}) => {
  const [filename, setFilename] = useState("");
  const [label, setLabel] = useState("");
  const [editFilename, setEditFilename] = useState(false);

  useEffect(() => {
    if (selectedFileData) {
      if (fileMap[selectedFileData].isURL) {
        setFilename(
          fileMap[selectedFileData].content
            ? fileMap[selectedFileData].content
            : ""
        );
      } else {
        setFilename(fileMap[selectedFileData].filename);
      }
    }
  }, [fileMap, selectedFileData]);

  const switchEditMode = () => {
    if (editFilename && selectedFileData) {
      const newFileData: FileData = JSON.parse(
        JSON.stringify(fileMap[selectedFileData])
      );

      if (fileMap[selectedFileData].isURL) {
        newFileData.content = filename;
      } else {
        newFileData.filename = filename;
      }
      const newFileMap: FileMap = { ...fileMap };
      newFileMap[selectedFileData] = newFileData;
      setFileMap(newFileMap);
    }
    setEditFilename((prevState) => !prevState);
  };

  const openDebugModal = () => {
    const modal = document.getElementById("File_Debug_Modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const formatByteSize = (bytes: number): string => {
    if (bytes < 1024) {
      // File size in Bytes
      return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
      // File size in Kilobytes
      const sizeInKB = (bytes / 1024).toFixed(2);
      return `${sizeInKB} KB`;
    } else if (bytes < 1024 * 1024 * 1024) {
      // File size in Megabytes
      const sizeInMB = (bytes / (1024 * 1024)).toFixed(2);
      return `${sizeInMB} MB`;
    } else {
      // File size in Gigabytes
      const sizeInGB = (bytes / (1024 * 1024 * 1024)).toFixed(2);
      return `${sizeInGB} GB`;
    }
  };

  const setOverwrite = (o: boolean) => {
    if (selectedFileData) {
      const newFileData: FileData = JSON.parse(
        JSON.stringify(fileMap[selectedFileData])
      );
      newFileData.overwrite = o;
      const newFileMap: FileMap = { ...fileMap };
      newFileMap[selectedFileData] = newFileData;
      setFileMap(newFileMap);
    }
  };

  const addLabel = (l: string) => {
    if (
      selectedFileData &&
      !fileMap[selectedFileData].labels.includes(l) &&
      l.length > 0
    ) {
      const newFileData: FileData = JSON.parse(
        JSON.stringify(fileMap[selectedFileData])
      );
      newFileData.labels.push(l);
      const newFileMap: FileMap = { ...fileMap };
      newFileMap[selectedFileData] = newFileData;
      setFileMap(newFileMap);
      setLabel("");
    }
  };

  const removeLabel = (l: string) => {
    if (
      selectedFileData &&
      fileMap[selectedFileData].labels.includes(l) &&
      l.length > 0
    ) {
      const newFileData: FileData = JSON.parse(
        JSON.stringify(fileMap[selectedFileData])
      );
      newFileData.labels = newFileData.labels.filter((item) => item !== l);
      const newFileMap: FileMap = { ...fileMap };
      newFileMap[selectedFileData] = newFileData;
      setFileMap(newFileMap);
      setLabel("");
    }
  };

  function renderLabelBoxes(fileData: FileData) {
    return Object.entries(fileData.labels).map(([key, label]) => (
      <div
        key={fileData.fileID + key + label}
        className="flex bg-bg-verba min-w-[10vw] p-2 text-sm text-text-verba justify-between items-center rounded-xl"
      >
        <p>{label}</p>
        <button
          onClick={() => {
            removeLabel(label);
          }}
          className="btn btn-sm btn-square bg-button-verba border-none hover:bg-warning-verba text-text-verba"
        >
          {" "}
          <FaTrash size={12} />
        </button>
      </div>
    ));
  }

  if (selectedFileData) {
    return (
      <div className="flex flex-col justify-start gap-3 rounded-2xl p-1 w-full ">
        {/* Filename */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          {selectedFileData && fileMap[selectedFileData].isURL ? (
            <p className="flex min-w-[8vw]">URL</p>
          ) : (
            <p className="flex min-w-[8vw]">Filename</p>
          )}
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={filename}
              onChange={(e) => {
                setFilename(e.target.value);
              }}
              disabled={!editFilename}
            />
          </label>
          <button
            onClick={switchEditMode}
            className="btn btn-square bg-button-verba border-none hover:bg-secondary-verba text-text-verba"
          >
            {editFilename ? (
              <IoIosCheckmark size={20} />
            ) : (
              <MdModeEdit size={15} />
            )}
          </button>
        </div>

        {/* Labels */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Labels</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={label}
              onChange={(e) => {
                setLabel(e.target.value);
              }}
            />
          </label>
          <button
            onClick={() => {
              addLabel(label);
            }}
            className="btn btn-square bg-button-verba border-none hover:bg-secondary-verba text-text-verba"
          >
            <IoAddCircleSharp size={15} />
          </button>
        </div>

        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]"></p>
          <p className="text-sm text-text-alt-verba text-start">
            Add or remove labels for Document Filtering
          </p>
        </div>

        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]"></p>
          <div className="grid grid-cols-3 gap-2">
            {renderLabelBoxes(fileMap[selectedFileData])}
          </div>
        </div>

        <div className="divider"></div>

        {/* Extension */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Extension</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={fileMap[selectedFileData].extension}
              disabled={true}
            />
          </label>
        </div>

        {/* File Size */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">File Size</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={formatByteSize(fileMap[selectedFileData].file_size)}
              disabled={true}
            />
          </label>
        </div>

        {/* Overwrite */}
        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]">Overwrite</p>
          <input
            type="checkbox"
            className="checkbox checkbox-md"
            onClick={(e) =>
              setOverwrite((e.target as HTMLInputElement).checked)
            }
            checked={
              selectedFileData ? fileMap[selectedFileData].overwrite : false
            }
          />
        </div>

        <div className="divider"></div>

        {/* Reader */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Reader</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={fileMap[selectedFileData].rag_config["Reader"].selected}
              disabled={true}
            />
          </label>
        </div>

        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]"></p>
          <p className="text-sm text-text-alt-verba text-start">
            {selectedFileData &&
              fileMap[selectedFileData].rag_config["Reader"].components[
                fileMap[selectedFileData].rag_config["Reader"].selected
              ].description}
          </p>
        </div>

        {/* Chunker */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Chunker</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={fileMap[selectedFileData].rag_config["Chunker"].selected}
              disabled={true}
            />
          </label>
        </div>

        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]"></p>
          <p className="text-sm text-text-alt-verba text-start">
            {selectedFileData &&
              fileMap[selectedFileData].rag_config["Chunker"].components[
                fileMap[selectedFileData].rag_config["Chunker"].selected
              ].description}
          </p>
        </div>

        {/* Embedder */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Embedder</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={fileMap[selectedFileData].rag_config["Embedder"].selected}
              disabled={true}
            />
          </label>
        </div>

        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]"></p>
          <p className="text-sm text-text-alt-verba text-start">
            {selectedFileData &&
              fileMap[selectedFileData].rag_config["Embedder"].components[
                fileMap[selectedFileData].rag_config["Embedder"].selected
              ].description}
          </p>
        </div>

        <div className="divider"></div>

        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Debug</p>
          <button
            onClick={openDebugModal}
            className="btn btn-square bg-button-verba border-none hover:bg-secondary-verba text-text-verba"
          >
            <CgDebug size={15} />
          </button>
        </div>

        <dialog id={"File_Debug_Modal"} className="modal">
          <div className="modal-box min-w-fit">
            <h3 className="font-bold text-lg">Debugging File Configuration</h3>
            <pre className="whitespace-pre-wrap">
              {selectedFileData
                ? (() => {
                    // Create a shallow copy of the object
                    const objCopy = { ...fileMap[selectedFileData] };
                    // Delete the `content` property
                    delete objCopy.content;
                    // Convert to a pretty-printed JSON string
                    return JSON.stringify(objCopy, null, 2);
                  })()
                : ""}
            </pre>
            <div className="modal-action">
              <form method="dialog">
                <button className="btn text-text-verba bg-warning-verba border-none hover:bg-button-hover-verba ml-2">
                  Close
                </button>
              </form>
            </div>
          </div>
        </dialog>
      </div>
    );
  } else {
    return <div></div>;
  }
};

export default BasicSettingView;
