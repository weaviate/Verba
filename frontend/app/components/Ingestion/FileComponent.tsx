"use client";

import React from "react";
import { FileData, FileMap, statusTextMap } from "@/app/types";
import { FaTrash } from "react-icons/fa";
import { FaCheckCircle } from "react-icons/fa";
import { MdError } from "react-icons/md";

import UserModalComponent from "../Navigation/UserModal";

import VerbaButton from "../Navigation/VerbaButton";

interface FileComponentProps {
  fileData: FileData;
  fileMap: FileMap;
  handleDeleteFile: (name: string) => void;
  selectedFileData: string | null;
  setSelectedFileData: (f: string | null) => void;
}

const FileComponent: React.FC<FileComponentProps> = ({
  fileData,
  fileMap,
  handleDeleteFile,
  selectedFileData,
  setSelectedFileData,
}) => {
  const openDeleteModal = () => {
    const modal = document.getElementById(
      "remove_file_" + fileMap[fileData.fileID].filename
    );
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  return (
    <div className="flex justify-between items-center gap-2 rounded-2xl p-1 w-full">
      {fileMap[fileData.fileID].status != "READY" ? (
        <div className="flex gap-2">
          {fileMap[fileData.fileID].status != "DONE" &&
            fileMap[fileData.fileID].status != "ERROR" && (
              <VerbaButton
                title={statusTextMap[fileMap[fileData.fileID].status]}
                text_class_name="text-xs"
                className="w-[120px]"
              />
            )}
          {fileMap[fileData.fileID].status == "DONE" && (
            <VerbaButton
              title={statusTextMap[fileMap[fileData.fileID].status]}
              Icon={FaCheckCircle}
              selected={true}
              className="w-[120px]"
              selected_color={"bg-secondary-verba"}
            />
          )}
          {fileMap[fileData.fileID].status == "ERROR" && (
            <VerbaButton
              title={statusTextMap[fileMap[fileData.fileID].status]}
              Icon={MdError}
              className="w-[120px]"
              selected={true}
              selected_color={"bg-warning-verba"}
            />
          )}
        </div>
      ) : (
        <div className="flex gap-2">
          <VerbaButton
            title={fileMap[fileData.fileID].rag_config["Reader"].selected}
            className="w-[120px]"
            text_class_name="truncate w-[100px]"
          />
        </div>
      )}

      <VerbaButton
        title={
          fileMap[fileData.fileID].filename
            ? fileMap[fileData.fileID].filename
            : "No Filename"
        }
        selected={selectedFileData === fileMap[fileData.fileID].fileID}
        selected_color="bg-secondary-verba"
        className="w-[200px] lg:w-[350px]"
        text_class_name="truncate max-w-[150px] lg:max-w-[300px]"
        onClick={() => {
          setSelectedFileData(fileData.fileID);
        }}
      />

      <VerbaButton
        Icon={FaTrash}
        onClick={openDeleteModal}
        className="w-[120px] max-w-min"
        selected={selectedFileData === fileMap[fileData.fileID].fileID}
        selected_color="bg-warning-verba"
      />

      <UserModalComponent
        modal_id={"remove_file_" + fileMap[fileData.fileID].filename}
        title={"Remove File"}
        text={
          fileMap[fileData.fileID].isURL
            ? "Do you want to remove the URL?"
            : "Do you want to remove " +
              fileMap[fileData.fileID].filename +
              " from the selection?"
        }
        triggerString="Delete"
        triggerValue={fileMap[fileData.fileID].fileID}
        triggerAccept={handleDeleteFile}
      />
    </div>
  );
};

export default FileComponent;
