"use client";

import React, { useState, useEffect } from "react";
import { FaFolder, FaFile, FaTrash } from "react-icons/fa";
import { DocumentPreview, Credentials, Theme } from "@/app/types";
import VerbaButton from "../Navigation/VerbaButton";
import UserModalComponent from "../Navigation/UserModal";
import { retrieveAllDocuments, deleteDocument } from "@/app/api";

interface TreeViewProps {
  credentials: Credentials;
  selectedTheme: Theme;
  selectedDocument: string | null;
  onSelectDocument: (uuid: string) => void;
  production: "Local" | "Demo" | "Production";
}

const TreeView: React.FC<TreeViewProps> = ({
  credentials,
  selectedDocument,
  onSelectDocument,
  production,
  selectedTheme,
}) => {
  const [documents, setDocuments] = useState<DocumentPreview[]>([]);
  const [isFetching, setIsFetching] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setIsFetching(true);
    try {
      const data = await retrieveAllDocuments("", [], 1, 50, credentials);
      if (data && !data.error) {
        setDocuments(data.documents);
      }
    } catch (error) {
      console.error("Error retrieving documents:", error);
    }
    setIsFetching(false);
  };

  const handleDeleteDocument = async (uuid: string) => {
    if (production === "Demo") return;
    const response = await deleteDocument(uuid, credentials);
    if (response) {
      setDocuments((prevDocs) => prevDocs.filter((doc) => doc.uuid !== uuid));
    }
  };

  const handleDeleteFolder = async (label: string) => {
    if (production === "Demo") return;

    const docsToDelete = documents.filter((doc) => doc.labels.includes(label));
    for (const doc of docsToDelete) {
      await deleteDocument(doc.uuid, credentials);
    }
    setDocuments((prevDocs) =>
      prevDocs.filter((doc) => !doc.labels.includes(label))
    );
  };

  const groupedDocuments: Record<string, DocumentPreview[]> = {};
  documents.forEach((doc) => {
    doc.labels.forEach((label) => {
      if (!groupedDocuments[label]) groupedDocuments[label] = [];
      groupedDocuments[label].push(doc);
    });
  });

  return (
    <div className="text-text-verba">
      {isFetching ? (
        <p>Loading documents...</p>
      ) : (
        <ul className="space-y-2">
          {Object.entries(groupedDocuments).map(([label, docs]) => (
            <TreeNode
              key={label}
              label={label}
              documents={docs}
              onSelectDocument={onSelectDocument}
              selectedDocument={selectedDocument}
              handleDeleteDocument={handleDeleteDocument}
              handleDeleteFolder={handleDeleteFolder}
              selectedTheme={selectedTheme}
              production={production}
            />
          ))}
        </ul>
      )}
    </div>
  );
};

const TreeNode: React.FC<{
  label: string;
  documents: DocumentPreview[];
  onSelectDocument: (uuid: string) => void;
  selectedDocument: string | null;
  handleDeleteDocument: (uuid: string) => void;
  handleDeleteFolder: (label: string) => void;
  production: "Local" | "Demo" | "Production";
  selectedTheme: Theme;
}> = ({
  label,
  documents,
  onSelectDocument,
  selectedDocument,
  handleDeleteDocument,
  handleDeleteFolder,
  production,
  selectedTheme,
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <li>
      {/* Folder (Label) with Delete Button */}
      <div
        className="flex items-center justify-between p-2 rounded-lg cursor-pointer"
        style={{
          backgroundColor: selectedTheme.bg_alt_color.color,
          color: selectedTheme.text_color.color,
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <FaFolder style={{ color: selectedTheme.primary_color.color }} />
          <span className="font-bold">{label}</span>
        </div>

        {/* Folder Delete Button */}
        {production !== "Demo" && (
          <>
            <VerbaButton
              Icon={FaTrash}
              className={`max-w-min p-2 rounded-lg transition ${
                selectedTheme.theme === "dark"
                    ? "bg-[#1D253A] text-white hover:bg-[#313749]"
                    : "bg-[#EFEFEF] text-black hover:bg-[#DCDCDC]"
              }`}
              onClick={(e) => {
                e.stopPropagation();
                const modal = document.getElementById(`remove_folder_${label}`) as HTMLDialogElement;
                modal.showModal();
              }}
            />
            <UserModalComponent
              modal_id={`remove_folder_${label}`}
              title="Remove Folder"
              text={`Do you want to remove all documents under "${label}"?`}
              triggerString="Delete"
              triggerValue={label}
              triggerAccept={() => handleDeleteFolder(label)}
            />
          </>
        )}
      </div>

      {/* Folder Contents */}
      {expanded && (
        <ul className="ml-5 border-l pl-3 space-y-1" style={{ borderColor: selectedTheme.text_alt_color.color }}>
          {documents.map((doc) => (
            <li key={doc.uuid} className="flex justify-between items-center space-x-2">
              {/* File Item */}
              <div
                className="flex items-center gap-2 flex-grow p-2 rounded-lg cursor-pointer transition"
                style={{
                  backgroundColor:
                    selectedDocument === doc.uuid
                      ? selectedTheme.primary_color.color
                      : selectedTheme.bg_color.color,
                  color:
                    selectedDocument === doc.uuid
                      ? selectedTheme.text_color.color
                      : selectedTheme.text_alt_color.color,
                }}
                onClick={() => onSelectDocument(doc.uuid)}
              >
                <FaFile style={{ color: selectedTheme.secondary_color.color }} />
                <span>{doc.title}</span>
              </div>

              {/* Document Delete Button */}
              {production !== "Demo" && (
                <>
                  <VerbaButton
                    Icon={FaTrash}
                    className={`max-w-min p-2 rounded-lg transition ${
                      selectedTheme.theme === "dark"
                          ? "bg-[#1D253A] text-white hover:bg-[#313749]"
                          : "bg-[#EFEFEF] text-black hover:bg-[#DCDCDC]"
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      const modal = document.getElementById(`remove_document_${doc.uuid}`) as HTMLDialogElement;
                      modal.showModal();
                    }}
                  />
                  <UserModalComponent
                    modal_id={`remove_document_${doc.uuid}`}
                    title="Remove Document"
                    text={`Do you want to remove "${doc.title}"?`}
                    triggerString="Delete"
                    triggerValue={doc.uuid}
                    triggerAccept={() => handleDeleteDocument(doc.uuid)}
                  />
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </li>
  );
};

export default TreeView;
