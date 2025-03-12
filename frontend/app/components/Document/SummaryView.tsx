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
  const [showModal, setShowModal] = useState(false); // State for modal visibility

  useEffect(() => {
    if (selectedDocument) {
      fetchSummary(false); // Auto-fetch summary when document is selected
    }
  }, [selectedDocument]);

  const fetchSummary = async (forceGenerate: boolean) => {
    try {
      setIsFetching(true);
      setError(null);

      // Pass forceGenerate flag to API to trigger a fresh summary if needed
      const data: SummaryPayload | null = await fetch_summary(
        selectedDocument,
        credentials,
        forceGenerate
      );

      if (data?.error) {
        setError(data.error);
        setSummary(null);
      } else {
        console.log(data);
        setSummary(data?.summary ?? "No summary available.");
      }
    } catch (error) {
      console.error("Failed to fetch summary:", error);
      setError("Error fetching summary.");
    } finally {
      setIsFetching(false);
    }
  };

  const handleRegenerate = () => {
    setShowModal(false); // Close modal
    fetchSummary(true); // Trigger summary regeneration
  };

  return (
    <div className="flex flex-col h-full">
      <div
        className="flex flex-col rounded-lg overflow-hidden h-full"
        style={{
          backgroundColor: selectedTheme.bg_alt_color.color,
          color: selectedTheme.text_color.color,
        }}
      >
        {/* Header */}
        <div
          className="flex justify-between items-center p-3 rounded-t-lg"
          style={{ backgroundColor: selectedTheme.secondary_color.color }}
        >
          <div className="flex gap-2 items-center">
            <IoNewspaper size={18} color={selectedTheme.text_color.color} />
            <h2 className="text-lg font-bold">Document Summary</h2>
          </div>
          {/* Show regenerate button only if summary exists */}
          {summary && !isFetching && (
            <VerbaButton
              title="Regenerate Summary"
              Icon={IoNewspaper}
              onClick={() => setShowModal(true)} // Open modal before regenerating
            />
          )}
        </div>

        {/* Content */}
        <div className="flex-grow flex flex-col p-3">
          {isFetching ? (
            <div className="flex items-center justify-center gap-2 flex-grow">
              <span className="loading loading-spinner loading-sm"></span>
            </div>
          ) : error ? (
            <div className="flex-grow flex flex-col items-center justify-center">
              <p style={{ color: selectedTheme.warning_color.color }}>{error}</p>
              <VerbaButton
                title="Generate Summary"
                Icon={IoNewspaper}
                onClick={() => fetchSummary(true)}
              />
            </div>
          ) : summary ? (
            <div className="flex-grow relative">
              <div
                className="absolute inset-0 overflow-y-auto p-4 rounded-md"
                style={{
                  backgroundColor: selectedTheme.bg_color.color,
                  color: selectedTheme.text_color.color,
                }}
              >
                <ReactMarkdown className="prose prose-lg break-words">
                  {summary}
                </ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="flex-grow flex flex-col items-center justify-center">
              <p>No summary available.</p>
              <VerbaButton
                title="Generate Summary"
                Icon={IoNewspaper}
                onClick={() => fetchSummary(true)}
              />
            </div>
          )}
        </div>
      </div>

      {/* Regenerate Confirmation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h2 className="text-lg font-bold mb-4">Are you sure?</h2>
            <p className="text-gray-600 mb-6">
              Regenerating the summary will replace the existing one. Do you want to proceed?
            </p>
            <div className="flex justify-end gap-3">
              <button
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                onClick={handleRegenerate}
              >
                Regenerate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryView;
