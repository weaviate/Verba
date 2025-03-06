"use client";

import React, { useState, useEffect } from "react";
import DocumentSearch from "./DocumentSearch";
import DocumentExplorer from "./DocumentExplorer";
import TreeView from "./TreeView";
import { Credentials, Theme, DocumentPreview, DocumentFilter } from "@/app/types";
import { retrieveAllDocuments } from "@/app/api";

interface DocumentViewProps {
  selectedTheme: Theme;
  production: "Local" | "Demo" | "Production";
  credentials: Credentials;
  documentFilter?: DocumentFilter[];
  setDocumentFilter?: React.Dispatch<React.SetStateAction<DocumentFilter[]>>;

  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const DocumentView: React.FC<DocumentViewProps> = ({
  selectedTheme,
  production,
  credentials,
  addStatusMessage,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentPreview[]>([]);

  useEffect(() => {
    const fetchDocuments = async () => {
      const data = await retrieveAllDocuments("", [], 1, 50, credentials);
      if (data?.documents) {
        setDocuments(data.documents);
      }
    };

    fetchDocuments();
  }, [credentials]);

  return (
    <div className="flex gap-3 h-[80vh] w-full">
      {/* Left Sidebar (Tree View & Search) */}
      <div className="w-1/4 bg-bg-alt-verba rounded-lg p-4 overflow-y-auto">
        <h2 className="text-lg font-bold mb-3 text-text-verba">Documents</h2>

        {/* Tree View */}
        <TreeView
          credentials={credentials}
          selectedDocument={selectedDocument}
          onSelectDocument={setSelectedDocument}
          production={production} 
        />

        {/* Document Search Below Tree */}
        {/* <DocumentSearch
          production={production}
          addStatusMessage={addStatusMessage}
          setSelectedDocument={setSelectedDocument}
          credentials={credentials}
          selectedDocument={selectedDocument}
        /> */}
      </div>

      {/* Right Panel (Document Viewer) */}
      <div className="w-3/4 flex">
        {selectedDocument ? (
          <DocumentExplorer
            production={production}
            credentials={credentials}
            addStatusMessage={addStatusMessage}
            setSelectedDocument={setSelectedDocument}
            selectedTheme={selectedTheme}
            selectedDocument={selectedDocument}
            documentFilter={[]} // Not needed anymore
            setDocumentFilter={() => {}} // Placeholder function
          />
        ) : (
          <div className="flex justify-center items-center w-full text-text-verba">
            Select a document to view details.
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentView;
