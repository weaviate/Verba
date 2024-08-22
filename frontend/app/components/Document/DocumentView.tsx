"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";
import DocumentSearch from "./DocumentSearch";
import DocumentExplorer from "./DocumentExplorer";
import { Credentials } from "@/app/api_types";

interface DocumentViewProps {
  settingConfig: SettingsConfiguration;
  production: boolean;
  credentials: Credentials;
}

const DocumentView: React.FC<DocumentViewProps> = ({
  settingConfig,
  production,
  credentials,
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
          settingConfig={settingConfig}
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
          settingConfig={settingConfig}
          selectedDocument={selectedDocument}
        />
      </div>
    </div>
  );
};

export default DocumentView;
