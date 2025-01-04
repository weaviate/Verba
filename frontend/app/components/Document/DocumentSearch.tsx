"use client";
import React, { useState, useEffect } from "react";
import {
  DocumentPreview,
  Credentials,
  DocumentsPreviewPayload,
} from "@/app/types";
import { retrieveAllDocuments, deleteDocument } from "@/app/api";
import { FaSearch, FaTrash } from "react-icons/fa";
import { MdOutlineRefresh, MdCancel } from "react-icons/md";
import { FaArrowAltCircleLeft, FaArrowAltCircleRight } from "react-icons/fa";
import InfoComponent from "../Navigation/InfoComponent";
import UserModalComponent from "../Navigation/UserModal";
import VerbaButton from "../Navigation/VerbaButton";
import { IoMdAddCircle } from "react-icons/io";

interface DocumentSearchComponentProps {
  selectedDocument: string | null;
  credentials: Credentials;
  setSelectedDocument: (c: string | null) => void;
  production: "Local" | "Demo" | "Production";
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const DocumentSearch: React.FC<DocumentSearchComponentProps> = ({
  selectedDocument,
  setSelectedDocument,
  production,
  addStatusMessage,
  credentials,
}) => {
  const [userInput, setUserInput] = useState("");
  const [page, setPage] = useState(1);

  const [documents, setDocuments] = useState<DocumentPreview[] | null>([]);
  const [totalDocuments, setTotalDocuments] = useState(0);

  const pageSize = 50;

  const [labels, setLabels] = useState<string[]>([]);
  const [selectedLabels, setSelectedLabels] = useState<string[]>([]);
  const [triggerSearch, setTriggerSearch] = useState(false);

  const [isFetching, setIsFetching] = useState(false);

  const nextPage = () => {
    if (!documents) {
      return;
    }

    if (page * pageSize < totalDocuments) {
      setPage((prev) => prev + 1);
    } else {
      setPage(1);
    }
  };

  const previousPage = () => {
    if (!documents) {
      return;
    }
    if (page == 1) {
      setPage(Math.ceil(totalDocuments / pageSize));
    } else {
      setPage((prev) => prev - 1);
    }
  };

  const fetchAllDocuments = async (_userInput?: string) => {
    try {
      setIsFetching(true);

      const data: DocumentsPreviewPayload | null = await retrieveAllDocuments(
        _userInput ? _userInput : "",
        selectedLabels,
        page,
        pageSize,
        credentials
      );

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setDocuments(null);
          setTotalDocuments(0);
        } else {
          setDocuments(data.documents);
          setLabels(data.labels);
          setIsFetching(false);
          setTotalDocuments(data.totalDocuments);
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
    fetchAllDocuments(userInput);
  }, [page, triggerSearch, selectedLabels]);

  const handleSearch = () => {
    fetchAllDocuments(userInput);
  };

  const clearSearch = () => {
    setUserInput("");
    setSelectedLabels([]);
    fetchAllDocuments("");
  };

  const handleKeyDown = (e: any) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      handleSearch(); // Submit form
    }
  };

  const handleDeleteDocument = async (d: string) => {
    if (production == "Demo") {
      return;
    }
    const response = await deleteDocument(d, credentials);
    addStatusMessage("Deleted document", "WARNING");
    if (response) {
      if (d == selectedDocument) {
        setSelectedDocument(null);
      }
      fetchAllDocuments(userInput);
    }
  };

  const addLabel = (l: string) => {
    setSelectedLabels((prev) => [...prev, l]);
  };

  const removeLabel = (l: string) => {
    setSelectedLabels((prev) => prev.filter((label) => label !== l));
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
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-3 items-center justify-between h-min w-full">
        <div className="hidden lg:flex gap-2 justify-start w-[8vw]">
          <InfoComponent
            tooltip_text="Search and inspect different documents imported into Verba"
            display_text="Search"
          />
        </div>

        <label className="input flex items-center gap-2 w-full bg-bg-verba">
          <input
            type="text"
            className="grow w-full"
            onKeyDown={handleKeyDown}
            placeholder={`Search for documents (${totalDocuments})`}
            value={userInput}
            onChange={(e) => {
              setUserInput(e.target.value);
            }}
          />
        </label>

        <VerbaButton onClick={handleSearch} Icon={FaSearch} />
        <VerbaButton
          onClick={clearSearch}
          icon_size={20}
          Icon={MdOutlineRefresh}
        />
      </div>

      {/* Document List */}
      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 gap-3 items-center h-full w-full overflow-auto">
        <div className="flex flex-col w-full justify-start gap-2">
          <div className="dropdown dropdown-hover">
            <label tabIndex={0}>
              <VerbaButton
                title="Label"
                className="btn-sm min-w-min"
                icon_size={12}
                text_class_name="text-xs"
                Icon={IoMdAddCircle}
                selected={false}
                disabled={false}
              />
            </label>
            <ul
              tabIndex={0}
              className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
            >
              {labels.map((label, index) => (
                <li key={"Label" + index}>
                  <a
                    onClick={() => {
                      if (!selectedLabels.includes(label)) {
                        setSelectedLabels([...selectedLabels, label]);
                      }
                      const dropdownElement =
                        document.activeElement as HTMLElement;
                      dropdownElement.blur();
                      const dropdown = dropdownElement.closest(
                        ".dropdown"
                      ) as HTMLElement;
                      if (dropdown) dropdown.blur();
                    }}
                  >
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedLabels.map((label, index) => (
              <VerbaButton
                title={label}
                key={"FilterDocumentLabel" + index}
                Icon={MdCancel}
                className="btn-sm min-w-min max-w-[200px]"
                icon_size={12}
                selected_color="bg-primary-verba"
                selected={true}
                text_class_name="truncate max-w-[200px]"
                text_size="text-xs"
                onClick={() => {
                  removeLabel(label);
                }}
              />
            ))}
          </div>
        </div>

        {isFetching && (
          <div className="flex items-center justify-center gap-2">
            <span className="loading loading-spinner loading-sm text-text-alt-verba"></span>
          </div>
        )}

        <div className="flex flex-col w-full">
          {documents &&
            documents.map((document, index) => (
              <div
                key={"Document" + index + document.title}
                className="flex justify-between items-center gap-2 rounded-2xl p-1 w-full"
              >
                <div className="flex justify-between items-center w-full gap-2">
                  <VerbaButton
                    title={document.title}
                    selected={selectedDocument == document.uuid}
                    selected_color="bg-secondary-verba"
                    key={document.title + index}
                    className="flex-grow"
                    text_class_name="truncate max-w-[150px] lg:max-w-[350px]"
                    onClick={() => setSelectedDocument(document.uuid)}
                  />
                  {production !== "Demo" && (
                    <VerbaButton
                      Icon={FaTrash}
                      selected={selectedDocument == document.uuid}
                      selected_color="bg-warning-verba"
                      className="max-w-min"
                      key={document.title + index + "delete"}
                      onClick={() => {
                        openDeleteModal("remove_document" + document.uuid);
                      }}
                    />
                  )}
                </div>
                <UserModalComponent
                  modal_id={"remove_document" + document.uuid}
                  title={"Remove Document"}
                  text={"Do you want to remove " + document.title + "?"}
                  triggerString="Delete"
                  triggerValue={document.uuid}
                  triggerAccept={handleDeleteDocument}
                />
              </div>
            ))}{" "}
        </div>
      </div>

      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-4 items-center justify-center h-min w-full">
        <div className="join justify-center items-center text-text-verba">
          <div className="flex justify-center items-center gap-2 bg-bg-alt-verba">
            <VerbaButton
              title={"Previous Page"}
              onClick={previousPage}
              className="btn-sm min-w-min max-w-[200px]"
              text_class_name="text-xs"
              Icon={FaArrowAltCircleLeft}
            />
            <div className="flex items-center">
              <p className="text-xs text-text-verba">Page {page}</p>
            </div>
            <VerbaButton
              title={"Next Page"}
              onClick={nextPage}
              className="btn-sm min-w-min max-w-[200px]"
              text_class_name="text-xs"
              Icon={FaArrowAltCircleRight}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentSearch;
