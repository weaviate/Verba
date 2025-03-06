"use client";

import React, { useState, useEffect } from "react";
import { FaFolder, FaFile, FaTrash } from "react-icons/fa";
import { DocumentPreview, Credentials } from "@/app/types";
import VerbaButton from "../Navigation/VerbaButton";
import UserModalComponent from "../Navigation/UserModal";
import { retrieveAllDocuments, deleteDocument } from "@/app/api";

interface TreeViewProps {
  credentials: Credentials;
  selectedDocument: string | null;
  onSelectDocument: (uuid: string) => void;
  production: "Local" | "Demo" | "Production";
}

const TreeView: React.FC<TreeViewProps> = ({
  credentials,
  selectedDocument,
  onSelectDocument,
  production,
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
  production: "Local" | "Demo" | "Production";
}> = ({ label, documents, onSelectDocument, selectedDocument, handleDeleteDocument, production }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <li>
      {/* Folder (Label) */}
      <div
        className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-gray-200 hover:bg-gray-300"
        onClick={() => setExpanded(!expanded)}
      >
        <FaFolder className="text-yellow-500" />
        <span className="font-bold">{label}</span>
      </div>

      {expanded && (
        <ul className="ml-5 border-l border-gray-400 pl-3 space-y-1">
          {documents.map((doc) => (
            <li key={doc.uuid} className="flex justify-between items-center space-x-2">
              {/* Grey Box for File */}
              <div
                className={`flex items-center gap-2 flex-grow p-2 rounded-lg cursor-pointer bg-gray-100 hover:bg-gray-300 transition ${
                  selectedDocument === doc.uuid ? "bg-blue-500 text-black" : ""
                }`}
                onClick={() => onSelectDocument(doc.uuid)}
              >
                <FaFile className="text-blue-500" />
                <span>{doc.title}</span>
              </div>

              {/* Delete Button (Separate) */}
              {production !== "Demo" && (
                <>
                  <VerbaButton
                    Icon={FaTrash}
                    className="max-w-min p-2 rounded-lg bg-gray-200 hover:bg-red-600 hover:text-white transition"
                    onClick={() => {
                      const modal = document.getElementById(`remove_document_${doc.uuid}`) as HTMLDialogElement;
                      modal.showModal();
                    }}
                  />
                  <UserModalComponent
                    modal_id={`remove_document_${doc.uuid}`}
                    title="Remove Document"
                    text={`Do you want to remove ${doc.title}?`}
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
