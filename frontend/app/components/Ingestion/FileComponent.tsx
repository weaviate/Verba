"use client";

import React, { useState, useEffect, use } from "react";
import { FileData } from "./types";
import { FaTrash } from "react-icons/fa";
import { GoTriangleDown } from "react-icons/go";

import UserModalComponent from "../Navigation/UserModal";
import { RAGConfig } from "../RAG/types";
import { IoIosCheckmark } from "react-icons/io";
import { MdModeEdit } from "react-icons/md";

import { closeOnClick } from "./util";

interface FileComponentProps {
  fileData: FileData;
  handleDeleteFile: (name: string) => void;
  selectedFileData: FileData | null;
  setSelectedFileData: (f: FileData) => void;
}

const FileComponent: React.FC<FileComponentProps> = ({
  fileData,
  handleDeleteFile,
  selectedFileData,
  setSelectedFileData,
}) => {
  const [URLValue, setURLValue] = useState("");
  const [editURL, setEditURL] = useState(true);
  const [currentFileData, setCurrentFileData] = useState<FileData>(fileData);

  const openDeleteModal = () => {
    const modal = document.getElementById(
      "remove_file_" + currentFileData.filename
    );
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const switchEditMode = () => {
    setEditURL((prevState) => !prevState);
  };

  const changeReader = (r: string) => {
    const newFileData: FileData = JSON.parse(JSON.stringify(currentFileData));
    const newRAGConfig: RAGConfig = JSON.parse(
      JSON.stringify(currentFileData.rag_config)
    );
    newRAGConfig["Reader"].selected = r;
    newFileData.rag_config = newRAGConfig;
    setCurrentFileData(newFileData);
  };

  function renderUploadComponents(
    rag_config: RAGConfig,
    changeReader: (r: string) => void,
    closeOnClick: () => void,
    filter: "FILE" | "URL"
  ) {
    return Object.entries(rag_config["Reader"].components)
      .filter(([key, component]) => component.type === filter)
      .map(([key, component]) => (
        <li
          key={"Dropdown_" + component.name}
          onClick={() => {
            changeReader(component.name);
            closeOnClick();
          }}
        >
          <a>{component.name}</a>
        </li>
      ));
  }

  return (
    <div className="flex justify-between items-center gap-2 rounded-2xl p-1 w-full">
      <div
        className="dropdown dropdown-bottom flex justify-start items-center min-w-[11vw] tooltip tooltip-right"
        data-tip={
          currentFileData.rag_config["Reader"].components[
            currentFileData.rag_config["Reader"].selected
          ].description
        }
      >
        <button
          tabIndex={0}
          role="button"
          className="btn bg-button-verba hover:bg-button-hover-verba text-text-verba w-full flex justify-start border-none"
        >
          <GoTriangleDown size={15} />
          <p>{currentFileData.rag_config["Reader"].selected}</p>
        </button>
        <ul
          tabIndex={0}
          className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
        >
          {currentFileData.isURL
            ? renderUploadComponents(
                currentFileData.rag_config,
                changeReader,
                closeOnClick,
                "URL"
              )
            : renderUploadComponents(
                currentFileData.rag_config,
                changeReader,
                closeOnClick,
                "FILE"
              )}
        </ul>
      </div>

      {/* If is not URL Component */}
      {!currentFileData.isURL && (
        <button
          onClick={() => {
            setSelectedFileData(currentFileData);
          }}
          className={`flex ${selectedFileData && selectedFileData.filename === currentFileData.filename ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"}  w-full p-3 rounded-lg transition-colors duration-300 ease-in-out border-none`}
        >
          <p className="text-text-verba">{currentFileData.filename}</p>
        </button>
      )}

      {/* If is URL Component and edit mode */}
      {currentFileData.isURL && editURL && (
        <div className="flex items-center justify-center gap-2 w-full">
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              placeholder={
                "Enter " +
                currentFileData.rag_config["Reader"].selected +
                " URL here"
              }
              value={URLValue}
              onChange={(e) => {
                setURLValue(e.target.value);
              }}
            />
          </label>
        </div>
      )}

      {currentFileData.isURL && !editURL && (
        <button
          onClick={() => {
            setSelectedFileData(currentFileData);
          }}
          className={`flex ${selectedFileData && selectedFileData.filename === currentFileData.filename ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"}  w-full p-3 rounded-lg transition-colors duration-300 ease-in-out border-none`}
        >
          <p className="text-text-verba">{URLValue}</p>
        </button>
      )}

      {currentFileData.isURL && (
        <div className="flex justify-end items-center">
          <button
            onClick={switchEditMode}
            className="btn btn-square border-none bg-button-verba hover:bg-secondary-verba text-text-verba"
          >
            {editURL ? <IoIosCheckmark size={20} /> : <MdModeEdit size={15} />}
          </button>
        </div>
      )}

      <div className="flex justify-end items-center">
        <button
          onClick={openDeleteModal}
          className="btn btn-square bg-button-verba border-none hover:bg-warning-verba text-text-verba"
        >
          <FaTrash size={15} />
        </button>
      </div>
      <UserModalComponent
        modal_id={"remove_file_" + currentFileData.filename}
        title={"Remove File"}
        text={
          currentFileData.isURL
            ? "Do you want to remove the URL?"
            : "Do you want to remove " +
              currentFileData.filename +
              " from the selection?"
        }
        triggerString="Delete"
        triggerValue={currentFileData.filename}
        triggerAccept={handleDeleteFile}
      />
    </div>
  );
};

export default FileComponent;
