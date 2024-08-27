"use client";

import React, { useState, useEffect } from "react";
import { Credentials, Suggestion } from "@/app/types";
import { IoTrash, IoDocumentSharp, IoReload, IoCopy } from "react-icons/io5";
import { FaWrench } from "react-icons/fa";
import {
  deleteAllDocuments,
  fetchAllSuggestions,
  deleteSuggestion,
} from "@/app/api";
import UserModalComponent from "../Navigation/UserModal";
import { FaArrowAltCircleRight, FaArrowAltCircleLeft } from "react-icons/fa";
import { formatDistanceToNow, parseISO } from "date-fns";

interface SuggestionViewProps {
  credentials: Credentials;
}

const SuggestionView: React.FC<SuggestionViewProps> = ({ credentials }) => {
  const [page, setPage] = useState(1);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 3;

  const handleSuggestionFetch = async () => {
    const suggestions = await fetchAllSuggestions(page, pageSize, credentials);
    if (suggestions) {
      setSuggestions(suggestions.suggestions);
      setTotalCount(suggestions.total_count);
    }
  };
  useEffect(() => {
    handleSuggestionFetch();
  }, []);

  useEffect(() => {
    handleSuggestionFetch();
  }, [page]);

  const nextPage = () => {
    if (page * pageSize <= totalCount) {
      setPage((prev) => prev + 1);
    } else {
      setPage(1);
    }
  };

  const previousPage = () => {
    if (page == 1) {
      setPage(1);
    } else {
      setPage((prev) => prev - 1);
    }
  };

  const openModal = (modal_id: string) => {
    const modal = document.getElementById(modal_id);
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const getTimeAgo = (timestamp: string): string => {
    try {
      const date = parseISO(timestamp);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (error) {
      console.error("Error parsing timestamp:", error);
      return "Invalid date";
    }
  };

  const handleRefresh = () => {
    handleSuggestionFetch();
  };

  const handleDelete = async (uuid: string) => {
    await deleteSuggestion(uuid, credentials);
    await handleSuggestionFetch();
  };

  const handleCopy = (query: string) => {
    navigator.clipboard.writeText(query).then(() => {
      // You can add a toast notification here if you want
      console.log("Copied to clipboard");
    });
  };

  return (
    <div className="flex flex-col w-full h-full p-4">
      <div className="flex justify-between items-center mb-4">
        <p className="text-2xl font-bold">Manage Suggestions ({totalCount})</p>
        <button
          onClick={handleRefresh}
          className="btn border-none shadow-none flex items-center gap-2 p-3 text-text-alt-verba hover:text-text-verba bg-button-verba hover:bg-button-hover-verba"
          title="Refresh suggestions"
        >
          <IoReload size={15} />
          <p>Refresh</p>
        </button>
      </div>
      <div className="flex-grow overflow-y-auto">
        <div className="gap-4 flex flex-col p-4 text-text-verba">
          <div className="flex flex-col gap-2">
            {suggestions.map((suggestion, index) => (
              <div
                key={"Suggestion" + suggestion.uuid}
                className="flex items-center justify-between gap-2 p-4 border-2 bg-bg-alt-verba rounded-xl"
              >
                <div className="flex flex-col items-start justify-start gap-2 w-2/3">
                  <p className="font-bold flex text-xs text-start text-text-alt-verba">
                    {getTimeAgo(suggestion.timestamp)}
                  </p>
                  <p
                    className="text-sm text-text-verba truncate max-w-full"
                    title={suggestion.query}
                  >
                    {suggestion.query}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleCopy(suggestion.query)}
                    className="p-3 btn-square border-none shadow-none btn text-text-alt-verba hover:text-text-verba bg-button-verba hover:bg-button-hover-verba"
                    title="Copy to clipboard"
                  >
                    <IoCopy size={15} />
                  </button>
                  <button
                    onClick={() =>
                      openModal("remove_suggestion" + suggestion.uuid)
                    }
                    className="p-3 btn-square border-none shadow-none btn text-text-alt-verba hover:text-text-verba bg-button-verba hover:bg-warning-verba"
                    title="Delete suggestion"
                  >
                    <IoTrash size={15} />
                  </button>
                </div>
                <UserModalComponent
                  modal_id={"remove_suggestion" + suggestion.uuid}
                  title={"Remove Suggestion"}
                  text={"Do you want to remove this suggestion?"}
                  triggerString="Delete"
                  triggerValue={suggestion.uuid}
                  triggerAccept={handleDelete}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
      {suggestions.length > 0 && (
        <div className="flex justify-center items-center gap-2 p-3 bg-bg-alt-verba">
          <button
            onClick={previousPage}
            className={`flex gap-2 items-center p-3 bg-button-verba hover:bg-button-hover-verba rounded-full w-fit`}
          >
            <FaArrowAltCircleLeft size={12} />
            <p className="text-xs flex text-text-verba">Previous Page</p>
          </button>
          <p className="text-xs flex text-text-verba">Page {page}</p>
          <button
            onClick={nextPage}
            className="flex gap-2 items-center p-3 bg-button-verba hover:bg-button-hover-verba rounded-full w-fit"
          >
            <FaArrowAltCircleRight size={12} />
            <p className="text-xs flex text-text-verba">Next Page</p>
          </button>
        </div>
      )}
    </div>
  );
};

export default SuggestionView;
