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

interface BasicSettingViewProps {
  selectedFileData: FileData | null;
  setSelectedFileData: (f: FileData) => void;
}

const BasicSettingView: React.FC<BasicSettingViewProps> = ({
  selectedFileData,
  setSelectedFileData,
}) => {
  const [currentFileData, setCurrentFileData] = useState<FileData | null>(
    selectedFileData
  );

  return (
    <div className="flex flex-col justify-start gap-2 rounded-2xl p-1 w-full">
      {/* Filename */}
      <div className="flex gap-2 justify-between items-center">
        <p>Filename</p>
        <label className="input flex items-center gap-2 w-full bg-bg-verba">
          <input
            type="text"
            className="grow w-full"
            value={currentFileData?.filename}
            disabled={true}
          />
        </label>
        <button className="btn btn-square border-none bg-button-verba hover:bg-secondary-verba text-text-verba">
          <MdModeEdit size={15} />
        </button>
      </div>
    </div>
  );
};

export default BasicSettingView;
