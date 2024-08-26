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
}

const DocumentView: React.FC<DocumentViewProps> = ({
  selectedTheme,
  production,
  credentials,
  documentFilter,
  setDocumentFilter,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedDocument ? "hidden lg:flex lg:w-[45vw]" : "w-full lg:w-[45vw] lg:flex"}`}
      >
        <DocumentSearch
          production={production}
          setSelectedDocument={setSelectedDocument}
          credentials={credentials}
          selectedDocument={selectedDocument}
        />
      </div>

      <div
        className={`${selectedDocument ? "lg:w-[55vw] w-full flex" : "hidden lg:flex lg:w-[55vw]"}`}
      >
        <DocumentExplorer
          credentials={credentials}
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
