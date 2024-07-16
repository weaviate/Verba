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
import { FaCheckCircle } from "react-icons/fa";
import { MdModeEdit } from "react-icons/md";

import { statusTextMap } from "./types";

import { closeOnClick } from "./util";

interface ChunkingViewProps {
  selectedFileData: string | null;
  fileMap: FileMap;
  setFileMap: React.Dispatch<React.SetStateAction<FileMap>>;
}

const ChunkingView: React.FC<ChunkingViewProps> = ({
  selectedFileData,
  fileMap,
  setFileMap,
}) => {
  const updateChunkerConfig = (
    configKey: string,
    configValue: string | number
  ) => {
    setFileMap((prevFileMap) => {
      if (selectedFileData) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[selectedFileData])
        );
        const newFileMap: FileMap = { ...prevFileMap };

        newFileMap[selectedFileData].rag_config["Chunker"].components[
          newFileMap[selectedFileData].rag_config["Chunker"].selected
        ].config[configKey].value = configValue;
        newFileMap[selectedFileData] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  if (selectedFileData) {
    return (
      <div className="flex flex-col justify-start gap-3 rounded-2xl p-1 w-full ">
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

        <div className="divider"></div>

        {selectedFileData &&
          Object.entries(
            fileMap[selectedFileData].rag_config["Chunker"].components[
              fileMap[selectedFileData].rag_config["Chunker"].selected
            ].config
          ).map(([configTitle, config]) => (
            <div>
              <div className="flex gap-2 justify-between items-center text-text-verba">
                <p className="flex min-w-[8vw]">{configTitle}</p>
                <label className="input flex items-center gap-2 w-full bg-bg-verba">
                  <input
                    type={config.type}
                    className="grow w-full"
                    value={config.value}
                    onChange={(e) => {
                      updateChunkerConfig(configTitle, e.target.value);
                    }}
                  />
                </label>
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

export default ChunkingView;
