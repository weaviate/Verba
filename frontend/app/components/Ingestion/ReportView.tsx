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
import { MdError } from "react-icons/md";

import { statusTextMap, statusColorMap } from "./types";

import { closeOnClick } from "./util";

interface ReportViewProps {
  selectedFileData: string | null;
  fileMap: FileMap;
}

const ReportView: React.FC<ReportViewProps> = ({
  selectedFileData,
  fileMap,
}) => {
  const [filename, setFilename] = useState("");

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
              disabled={true}
            />
          </label>
        </div>

        <div className="divider"></div>

        <div className="flex flex-col gap-3 text-text-verba">
          {selectedFileData &&
            Object.entries(fileMap[selectedFileData].status_report).map(
              ([status, statusReport]) => (
                <div className="flex">
                  <p className="flex min-w-[8vw] gap-2 items-center text-text-verba">
                    {statusReport.status === "DONE" && (
                      <FaCheckCircle size={15} />
                    )}
                    {statusReport.status === "ERROR" && <MdError size={15} />}
                    {statusTextMap[statusReport.status]}
                  </p>
                  <label
                    className={`input flex items-center gap-2 w-full ${statusColorMap[statusReport.status]} bg-bg-verba`}
                  >
                    <input
                      type="text"
                      className="grow w-full"
                      value={
                        statusReport.took != 0
                          ? statusReport.message +
                            " (" +
                            statusReport.took +
                            "s)"
                          : statusReport.message
                      }
                      disabled={true}
                    />
                  </label>
                </div>
              )
            )}
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
      </div>
    );
  } else {
    return <div></div>;
  }
};

export default ReportView;
