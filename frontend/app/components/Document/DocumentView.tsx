"use client";

import React, { useState } from "react";
import DocumentSearch from "./DocumentSearch";
import DocumentExplorer from "./DocumentExplorer";
import { Credentials, Theme, DocumentFilter } from "@/app/types";

interface DocumentViewProps {
  selectedTheme: Theme;
  production: "Local" | "Demo" | "Production";
  credentials: Credentials;
  documentFilter: DocumentFilter[];
  setDocumentFilter: React.Dispatch<React.SetStateAction<DocumentFilter[]>>;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const DocumentView: React.FC<DocumentViewProps> = ({
  selectedTheme,
  production,
  credentials,
  documentFilter,
  setDocumentFilter,
  addStatusMessage,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedDocument ? "hidden md:flex md:w-[45vw]" : "w-full md:w-[45vw] md:flex"}`}
      >
        <DocumentSearch
          production={production}
          addStatusMessage={addStatusMessage}
          setSelectedDocument={setSelectedDocument}
          credentials={credentials}
          selectedDocument={selectedDocument}
        />
      </div>

      <div
        className={`${selectedDocument ? "md:w-[55vw] w-full flex" : "hidden md:flex md:w-[55vw]"}`}
      >
        <DocumentExplorer
          production={production}
          credentials={credentials}
          addStatusMessage={addStatusMessage}
          setSelectedDocument={setSelectedDocument}
          selectedTheme={selectedTheme}
          selectedDocument={selectedDocument}
          documentFilter={documentFilter}
          setDocumentFilter={setDocumentFilter}
        />
      </div>
    </div>
  );
};

export default DocumentView;
