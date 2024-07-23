"use client";
import React, { useState, useEffect } from "react";
import {
  DocumentChunk,
  DocumentPreview,
  DocumentsPreviewPayload,
} from "./types";
import { FaSearch } from "react-icons/fa";
import PulseLoader from "react-spinners/PulseLoader";
import { SettingsConfiguration } from "../Settings/types";
import { IoIosRefresh } from "react-icons/io";
import { FaTrash } from "react-icons/fa";
import { FaFilter } from "react-icons/fa";

import InfoComponent from "../Navigation/InfoComponent";
import { MdCancel } from "react-icons/md";
import { MdOutlineRefresh } from "react-icons/md";

import { FaDatabase } from "react-icons/fa";
import UserModalComponent from "../Navigation/UserModal";
import { closeOnClick } from "../Ingestion/util";

import { RAGConfig } from "../RAG/types";
import ComponentStatus from "../Status/ComponentStatus";

interface DocumentSearchComponentProps {
  APIHost: string | null;
  selectedDocument: string | null;
  setSelectedDocument: (c: string | null) => void;
  settingConfig: SettingsConfiguration;
  production: boolean;
}

const DocumentSearch: React.FC<DocumentSearchComponentProps> = ({
  APIHost,
  selectedDocument,
  settingConfig,
  setSelectedDocument,
  production,
}) => {
  const [userInput, setUserInput] = useState("");
  const [page, setPage] = useState(1);

  const [documents, setDocuments] = useState<DocumentPreview[] | null>([]);

  const pageSize = 20;

  const [requestTime, setRequestTime] = useState(0);
  const [labels, setLabels] = useState<string[]>(["Documents", "Code", "Blog"]);
  const [selectedLabels, setSelectedLabels] = useState<string[]>([]);
  const [currentEmbedder, setCurrentEmbedder] = useState<string | null>(null);
  const [triggerSearch, setTriggerSearch] = useState(false);

  const [isFetching, setIsFetching] = useState(false);

  const nextPage = () => {
    if (!documents) {
      return;
    }

    if (documents.length < pageSize) {
      setPage(1);
    } else {
      setPage((prev) => prev + 1);
    }
  };

  const previousPage = () => {
    if (!documents) {
      return;
    }
    if (page == 1) {
      setPage(1);
    } else {
      setPage((prev) => prev - 1);
    }
  };

  const fetchAllDocuments = async (_userInput?: string) => {
    try {
      setIsFetching(true);

      const response = await fetch(APIHost + "/api/get_all_documents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: _userInput ? _userInput : "",
          labels: selectedLabels,
          page: page,
          pageSize: pageSize,
        }),
      });

      const data: DocumentsPreviewPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setDocuments(null);
        } else {
          setDocuments(data.documents);
          setLabels(data.labels);
          setRequestTime(data.took);
          setIsFetching(false);
        }
      }
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
    }
  };

  useEffect(() => {
    setTriggerSearch(true);
  }, []);

  useEffect(() => {
    if (APIHost != null) {
      fetchAllDocuments(userInput);
    } else {
      setDocuments(null);
      setIsFetching(false);
    }
  }, [page, triggerSearch, selectedLabels]);

  const handleSearch = () => {
    fetchAllDocuments(userInput);
  };

  const clearSearch = () => {
    setUserInput("");
    fetchAllDocuments("");
  };

  const handleKeyDown = (e: any) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      handleSearch(); // Submit form
    }
  };

  const deleteDocument = async (d: string) => {
    if (production) {
      return;
    }
    const response = await fetch(APIHost + "/api/delete_document", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ uuid: d }),
    });

    if (response) {
      if (d == selectedDocument) {
        setSelectedDocument(null);
      }
      fetchAllDocuments(userInput);
    }
  };

  const deleteAllDocuments = async () => {
    if (production) {
      return;
    }

    setSelectedDocument(null);
    setDocuments(null);

    await fetch(APIHost + "/api/reset", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ resetMode: "DOCUMENTS" }),
    });
  };

  const addLabel = (l: string) => {
    setSelectedLabels((prev) => [...prev, l]);
  };

  const removeLabel = (l: string) => {
    setSelectedLabels((prev) => prev.filter((label) => label !== l));
  };

  const triggerLabel = (l: string) => {
    if (selectedLabels.includes(l)) {
      removeLabel(l);
    } else {
      addLabel(l);
    }
  };

  const openDeleteModal = (id: string) => {
    const modal = document.getElementById(id);
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* Search Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start w-[8vw]">
          <InfoComponent
            settingConfig={settingConfig}
            tooltip_text="Search and inspect different documents imported into Verba"
            display_text="Search"
          />
        </div>

        <label className="input flex items-center gap-2 w-full bg-bg-verba">
          <input
            type="text"
            className="grow w-full"
            onKeyDown={handleKeyDown}
            placeholder="Search for documents"
            value={userInput}
            onChange={(e) => {
              setUserInput(e.target.value);
            }}
          />
        </label>

        <button
          type="button"
          onClick={handleSearch}
          className="btn btn-square border-none bg-primary-verba hover:bg-button-hover-verba"
        >
          <FaSearch size={15} />
        </button>

        <button
          type="button"
          onClick={clearSearch}
          className="btn btn-square border-none bg-button-verba hover:bg-button-hover-verba"
        >
          <MdOutlineRefresh size={18} />
        </button>
      </div>

      {/* Document List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 gap-3 items-center h-full w-full overflow-auto">
        <div className="grid grid-flow-col gap-2 justify-start items-start w-full">
          {labels &&
            labels.map((label, index) => (
              <button
                key={document.title + index + label}
                onClick={() => {
                  triggerLabel(label);
                }}
                className={`flex p-2 px-4 text-sm text-text-verba justify-center text-center items-center rounded-xl ${selectedLabels.includes(label) ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-bg-verba hover:bg-primary-verba"} transition-colors duration-300 ease-in-out border-none`}
              >
                <p>{label}</p>
              </button>
            ))}
        </div>

        {isFetching && (
          <div className="flex items-center justify-center gap-2">
            <span className="loading loading-spinner loading-sm"></span>
            <p className="text-text-alt-verba">Loading Documents</p>
          </div>
        )}

        <div className="flex flex-col w-full">
          {documents &&
            documents.map((document, index) => (
              <div
                key={"Document" + index + document.title}
                className="flex justify-between items-center gap-2 rounded-2xl p-1 w-full"
              >
                <button
                  key={document.title + index}
                  onClick={() => setSelectedDocument(document.uuid)}
                  className={`flex ${selectedDocument && selectedDocument === document.uuid ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"}  w-full p-3 rounded-lg transition-colors duration-300 ease-in-out border-none`}
                >
                  <p className="text-text-verba">{document.title}</p>
                </button>
                <div className="flex justify-end items-center">
                  <button
                    onClick={() => {
                      openDeleteModal("remove_document" + document.uuid);
                    }}
                    className="btn btn-square bg-button-verba border-none hover:bg-warning-verba text-text-verba"
                  >
                    <FaTrash size={15} />
                  </button>
                </div>
                <UserModalComponent
                  modal_id={"remove_document" + document.uuid}
                  title={"Remove Document"}
                  text={"Do you want to remove " + document.title + "?"}
                  triggerString="Delete"
                  triggerValue={document.uuid}
                  triggerAccept={deleteDocument}
                />
              </div>
            ))}{" "}
        </div>
      </div>

      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-center h-min w-full">
        <div className="flex gap-3 items-center justify-between w-full">
          <div className="join justify-center items-center text-text-verba">
            {page > 1 && (
              <button
                onClick={previousPage}
                className="join-item btn btn-sqare border-none bg-button-verba hover:bg-secondary-verba"
              >
                «
              </button>
            )}
            <button className="join-item btn border-none bg-button-verba hover:bg-secondary-verba">
              Page {page}
            </button>
            {documents && documents.length >= pageSize && (
              <button
                onClick={nextPage}
                className="join-item btn btn-square border-none bg-button-verba hover:bg-secondary-verba"
              >
                »
              </button>
            )}
          </div>

          <button
            onClick={() => {
              const modal = document.getElementById("remove_all_documents");
              if (modal instanceof HTMLDialogElement) {
                modal.showModal();
              }
            }}
            className={`flex bg-button-verba hover:bg-button-hover-verba border-none btn text-text-verba gap-2`}
          >
            <FaTrash size={15} />
            <p>Delete all Documents</p>
          </button>
        </div>
      </div>
      <UserModalComponent
        modal_id={"remove_all_documents"}
        title={"Remove all Document?"}
        text={"Do you want to all remove documents from Verba?"}
        triggerString={"Remove All"}
        triggerValue={null}
        triggerAccept={deleteAllDocuments}
      />
    </div>
  );
};

export default DocumentSearch;