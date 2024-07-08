"use client";

import React, { useState, useEffect, use } from "react";
import { FileData } from "./types";
import { FaTrash } from "react-icons/fa";

import UserModalComponent from "../Navigation/UserModal";

interface FileComponentProps {
  fileData: FileData;
  handleDeleteFile: (name: string) => void;
}

const FileComponent: React.FC<FileComponentProps> = ({
  fileData,
  handleDeleteFile,
}) => {
  const [URLValue, setURLValue] = useState("");

  const openDeleteModal = () => {
    const modal = document.getElementById("remove_file_" + fileData.filename);
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  return (
    <div className="flex justify-between items-center gap-2 rounded-2xl p-1 w-full">
      <div
        className="flex justify-start items-center w-[10vw] tooltip tooltip-right"
        data-tip={
          fileData.rag_config["Reader"].components[
            fileData.rag_config["Reader"].selected
          ].description
        }
      >
        <button className="btn bg-button-verba hover:bg-button-hover-verba text-text-verba w-full">
          <p>{fileData.rag_config["Reader"].selected}</p>
        </button>
      </div>
      {fileData.isURL ? (
        <div className="flex items-center justify-center gap-2 w-full">
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              placeholder="Enter URL here"
              value={URLValue}
              onChange={(e) => {
                setURLValue(e.target.value);
              }}
            />
          </label>
        </div>
      ) : (
        <button className="flex bg-button-verba hover:bg-secondary-verba w-full p-3 rounded-lg transition-colors duration-300 ease-in-out">
          <p className="text-text-verba">{fileData.filename}</p>
        </button>
      )}
      <div className="flex justify-end items-center">
        <button
          onClick={openDeleteModal}
          className="btn bg-button-verba hover:bg-warning-verba"
        >
          <FaTrash size={15} />
        </button>
      </div>
      <UserModalComponent
        modal_id={"remove_file_" + fileData.filename}
        title={"Remove File"}
        text={
          fileData.isURL
            ? "Do you want to remove the URL?"
            : "Do you want to remove " +
              fileData.filename +
              " from the selection?"
        }
        triggerString="Delete"
        triggerValue={fileData.filename}
        triggerAccept={handleDeleteFile}
      />
    </div>
  );
};

export default FileComponent;
