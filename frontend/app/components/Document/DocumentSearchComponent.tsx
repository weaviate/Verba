"use client";
import React, { useState, useEffect } from "react";
import {
  DocumentChunk,
  Document,
  AllDocumentsPayload,
} from "../Document/types";
import { FaSearch } from "react-icons/fa";
import PulseLoader from "react-spinners/PulseLoader";
import { SettingsConfiguration } from "../Settings/types";
import { IoIosRefresh } from "react-icons/io";

import { FaDatabase } from "react-icons/fa";

import { RAGConfig } from "../RAG/types";
import ComponentStatus from "../Status/ComponentStatus";

interface DocumentSearchComponentProps {
  APIHost: string | null;
  selectedDocument: DocumentChunk | null;
  setSelectedDocument: (c: DocumentChunk | null) => void;
  settingConfig: SettingsConfiguration;
  documents: Document[] | null;
  setDocuments: (d: Document[] | null) => void;
  triggerReset: boolean;
  setCurrentPage: (p: any) => void;
  RAGConfig: RAGConfig | null;
  production: boolean;
}

const DocumentSearchComponent: React.FC<DocumentSearchComponentProps> = ({
  APIHost,
  selectedDocument,
  settingConfig,
  setSelectedDocument,
  documents,
  setDocuments,
  triggerReset,
  setCurrentPage,
  RAGConfig,
  production,
}) => {
  const [userInput, setUserInput] = useState("");
  const [page, setPage] = useState(1);

  const pageSize = 100;

  const [documentsTook, setDocumentsTook] = useState(0);
  const [docTypes, setDocTypes] = useState<string[]>([]);
  const [currentEmbedder, setCurrentEmbedder] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);

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
          doc_type: selectedType ? selectedType : "",
          page: page,
          pageSize: pageSize,
        }),
      });

      const data: AllDocumentsPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setDocuments(null);
        } else {
          setDocuments(data.documents);
          setDocTypes(data.doc_types);
          setCurrentEmbedder(data.current_embedder);
          setDocumentsTook(data.took);
          setIsFetching(false);
        }
      }
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
    }
  };

  useEffect(() => {
    if (documents != null && APIHost != null) {
      fetchAllDocuments(userInput);
    } else {
      setDocuments(null);
      setIsFetching(false);
    }
  }, [page, selectedType]);

  useEffect(() => {
    if (APIHost != null) {
      fetchAllDocuments(userInput);
    } else {
      setDocuments(null);
      setIsFetching(false);
    }
  }, [triggerReset]);

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

  const handleDocumentClick = (d: Document) => {
    const new_chunk: DocumentChunk = {
      text: "",
      doc_name: d.name,
      chunk_id: 0,
      doc_uuid: d.uuid,
      doc_type: d.type,
      score: 0,
    };
    setSelectedDocument(new_chunk);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba md:gap-5 min-h-[15vh] md:min-h-[9.3vh]">
        {/*Search Bar*/}
        <form
          className="flex flex-col lg:flex-row w-full items-center justify-between gap-2 lg:gap-3"
          onSubmit={handleSearch}
        >
          <textarea
            rows={1}
            cols={10}
            onKeyDown={handleKeyDown}
            value={userInput}
            onChange={(e) => {
              setUserInput(e.target.value);
            }}
            className=" bg-bg-alt-verba textarea textarea-xs p-2 text-sm md:text-base w-full"
            placeholder={`Search for documents`}
          ></textarea>

          <div className="flex justify-between items-center gap-2 lg:w-3/5">
            <div className="flex w-full">
              <ComponentStatus
                disable={production}
                component_name={RAGConfig ? RAGConfig["Embedder"].selected : ""}
                Icon={FaDatabase}
                changeTo={"RAG"}
                changePage={setCurrentPage}
              />
            </div>
            <button
              type="button"
              onClick={handleSearch}
              className="btn btn-sm md:btn-md btn-circle border-none shadow-none bg-bg-alt-verba hover:bg-secondary-verba"
            >
              <FaSearch size={18} />
            </button>
            <button
              type="button"
              onClick={clearSearch}
              className="btn btn-sm md:btn-md btn-circle border-none shadow-none bg-bg-alt-verba hover:bg-secondary-verba"
            >
              <IoIosRefresh size={18} />
            </button>
          </div>
        </form>
      </div>
      <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-3 sm:h-[35vh] md:h-[40vh] lg:h-[55vh] overflow-auto">
        <div className="flex gap-2 items-center justify-center">
          <div className="flex items-center justify-center">
            <select
              value={selectedType ? selectedType : "All"}
              onChange={(e) => {
                setSelectedType(
                  e.target.value === "All" ? null : e.target.value
                );
              }}
              className="select select-sm bg-bg-verba"
            >
              <option key={"Select_None"}>All</option>
              {docTypes.map((template) => (
                <option key={"Select_" + template}>{template}</option>
              ))}
            </select>
          </div>
          <div className="join justify-center items-center text-text-verba">
            {page > 1 && (
              <button
                onClick={previousPage}
                className="join-item btn btn-sm border-none bg-button-verba hover:bg-secondary-verba"
              >
                «
              </button>
            )}
            <button className="join-item btn btn-sm border-none bg-button-verba hover:bg-secondary-verba">
              Page {page}
            </button>
            {documents && documents.length >= pageSize && (
              <button
                onClick={nextPage}
                className="join-item btn btn-sm border-none bg-button-verba hover:bg-secondary-verba"
              >
                »
              </button>
            )}
          </div>
        </div>
        {documents && documents.length > 0 && (
          <div className="sm:hidden md:flex items-center justify-center">
            <p className="items-center justify-center text-text-alt-verba text-xs">
              {documents.length} documents retrieved in {documentsTook} seconds
              with {currentEmbedder}.
            </p>
          </div>
        )}
        <div className="gap-2 grid grid-cols-1 lg:grid-cols-2">
          {documents &&
            documents.map((document, index) => (
              <button
                key={document.name + index}
                onClick={() => handleDocumentClick(document)}
                className={`btn md:btn-md lg:btn-lg w-full flex justify-start gap-4 ${selectedDocument && selectedDocument.doc_uuid === document.uuid ? "bg-secondary-verba" : "bg-button-verba"} hover:button-hover-verba`}
              >
                <div className="flex flex-col items-start truncate">
                  <p className="text-xs lg:text-sm text-text-verba">
                    {document.name}
                  </p>
                  <p className="text-xs text-text-alt-verba">{document.type}</p>
                </div>
              </button>
            ))}
        </div>

        {isFetching && (
          <div className="flex items-center justify-center pl-4 mb-4 gap-3">
            <PulseLoader
              color={settingConfig.Customization.settings.text_color.color}
              loading={true}
              size={10}
              speedMultiplier={0.75}
            />
            <p>Loading Document</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentSearchComponent;
