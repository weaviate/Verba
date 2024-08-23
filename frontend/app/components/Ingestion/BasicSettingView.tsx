"use client";

import React, { useState, useEffect, useCallback } from "react";
import { FileData, FileMap, statusTextMap, statusColorMap } from "@/app/types";
import { FaTrash } from "react-icons/fa";
import { IoAddCircleSharp } from "react-icons/io5";
import { CgDebug } from "react-icons/cg";

import { MdError } from "react-icons/md";
import { FaCheckCircle } from "react-icons/fa";

interface BasicSettingViewProps {
  selectedFileData: string | null;
  fileMap: FileMap;
  setFileMap: (f: FileMap) => void;
  blocked: boolean | undefined;
}

const BasicSettingView: React.FC<BasicSettingViewProps> = ({
  selectedFileData,
  fileMap,
  setFileMap,
  blocked,
}) => {
  const [filename, setFilename] = useState("");
  const [source, setSource] = useState("");
  const [label, setLabel] = useState("");

  useEffect(() => {
    if (selectedFileData) {
      setFilename(fileMap[selectedFileData].filename);
      setSource(fileMap[selectedFileData].source);
    }
  }, [fileMap, selectedFileData]);

  const updateFileMap = useCallback(
    (key: "filename" | "source", value: string) => {
      if (selectedFileData) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(fileMap[selectedFileData])
        );
        newFileData[key] = value;
        const newFileMap: FileMap = { ...fileMap };
        newFileMap[selectedFileData] = newFileData;
        setFileMap(newFileMap);
      }
    },
    [selectedFileData, fileMap, setFileMap]
  );

  const handleFilenameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newFilename = e.target.value;
      setFilename(newFilename);
      updateFileMap("filename", newFilename);
    },
    [updateFileMap]
  );

  const handleSourceChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newSource = e.target.value;
      setSource(newSource);
      updateFileMap("source", newSource);
    },
    [updateFileMap]
  );

  const openDebugModal = () => {
    const modal = document.getElementById("File_Debug_Modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const formatByteSize = (bytes: number): string => {
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    if (bytes === 0) return "0 B";

    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = bytes / Math.pow(1024, i);
    return `${size.toFixed(2)} ${sizes[i]}`;
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
        <p className="truncate max-w-[80%]" title={label}>
          {label}
        </p>
        <button
          onClick={() => {
            removeLabel(label);
          }}
          disabled={blocked}
          className="btn btn-sm btn-square bg-button-verba border-none hover:bg-warning-verba text-text-verba ml-2"
        >
          <FaTrash size={12} />
        </button>
      </div>
    ));
  }

  if (selectedFileData) {
    return (
      <div className="flex flex-col justify-start gap-3 rounded-2xl p-1 w-full ">
        {selectedFileData && fileMap[selectedFileData].status != "READY" && (
          <div className="divider  text-text-alt-verba">Import Status</div>
        )}

        <div className="flex flex-col gap-3 text-text-verba">
          {selectedFileData &&
            Object.entries(fileMap[selectedFileData].status_report).map(
              ([status, statusReport]) => (
                <div className="flex" key={"Status" + status}>
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

        <div className="divider text-text-alt-verba">File Settings</div>

        {/* Filename */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Title</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={filename}
              onChange={handleFilenameChange}
              disabled={blocked}
            />
          </label>
        </div>

        {/* Source */}
        <div className="flex gap-2 justify-between items-center text-text-verba">
          <p className="flex min-w-[8vw]">Source Link</p>
          <label className="input flex items-center gap-2 w-full bg-bg-verba">
            <input
              type="text"
              className="grow w-full"
              value={source}
              onChange={handleSourceChange}
              disabled={blocked}
            />
          </label>
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
              disabled={blocked}
              title={label}
            />
          </label>
          <button
            onClick={() => {
              addLabel(label);
            }}
            disabled={blocked}
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

        {/* Overwrite */}
        <div className="flex gap-2 items-center text-text-verba">
          <p className="flex min-w-[8vw]">Overwrite</p>
          <input
            type="checkbox"
            className="checkbox checkbox-md"
            onChange={(e) =>
              setOverwrite((e.target as HTMLInputElement).checked)
            }
            checked={
              selectedFileData ? fileMap[selectedFileData].overwrite : false
            }
            disabled={blocked}
          />
        </div>

        <div className="divider  text-text-alt-verba">File Info</div>

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

        <div className="divider  text-text-alt-verba">Ingestion Pipeline</div>

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
                    objCopy.content = "File Content";
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
