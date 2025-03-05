"use client";

import React, { useState, useEffect } from "react";
import { Theme, SummaryPayload } from "@/app/types";
import ReactMarkdown from "react-markdown";
import { IoNewspaper } from "react-icons/io5";
import { fetch_summary } from "@/app/api"; // API function to fetch summary
import { Credentials } from "@/app/types";
import VerbaButton from "../Navigation/VerbaButton";

interface SummaryViewProps {
  selectedDocument: string | null;
  selectedTheme: Theme;
  credentials: Credentials;
}

const SummaryView: React.FC<SummaryViewProps> = ({
  selectedDocument,
  credentials,
  selectedTheme,
}) => {
  const [isFetching, setIsFetching] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedDocument) {
      fetchSummary();
    }
  }, [selectedDocument]);

  const fetchSummary = async () => {
    try {
      setIsFetching(true);
      setError(null);

      const data: SummaryPayload | null = await fetch_summary(selectedDocument, credentials);

      if (data?.error) {
        setError(data.error);
        setSummary(null);
      } else {
        console.log(data)
        setSummary(data?.summary ?? "No summary available.");
      }
    } catch (error) {
      console.error("Failed to fetch summary:", error);
      setError("Error fetching summary.");
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-bg-alt-verba flex flex-col rounded-lg overflow-hidden h-full">
        {/* Header */}
        <div className="flex justify-between items-center p-3 bg-secondary-verba">
          <div className="flex gap-2 items-center">
            <IoNewspaper size={18} />
            <h2 className="text-lg font-bold text-text-verba">Document Summary</h2>
          </div>
        </div>

        {/* Content */}
        <div className="flex-grow flex flex-col p-3">
          {isFetching ? (
            <div className="flex items-center justify-center text-text-verba gap-2 flex-grow">
              <span className="loading loading-spinner loading-sm"></span>
            </div>
          ) : error ? (
            <p className="text-red-500 flex-grow flex items-center justify-center">{error}</p>
          ) : (
            <div className="flex-grow relative">
              <div className="absolute inset-0 overflow-y-auto bg-gray-100 p-4 rounded-md">
                <ReactMarkdown className="prose prose-lg text-gray-700 break-words">
                  {summary ?? ""}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SummaryView;
