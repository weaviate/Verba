"use client";

import React, { useState, useEffect } from "react";
import { Credentials, NodePayload, CollectionPayload } from "@/app/types";
import { IoTrash, IoDocumentSharp, IoReload } from "react-icons/io5";
import { FaWrench } from "react-icons/fa";
import { deleteAllDocuments, fetchMeta } from "@/app/api";
import UserModalComponent from "../Navigation/UserModal";

import VerbaButton from "../Navigation/VerbaButton";

interface InfoViewProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const InfoView: React.FC<InfoViewProps> = ({
  credentials,
  addStatusMessage,
}) => {
  const [nodePayload, setNodePayload] = useState<NodePayload | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [collectionPayload, setCollectionPayload] =
    useState<CollectionPayload | null>(null);

  const fetchMetadata = async () => {
    setIsLoading(true);
    const metaData = await fetchMeta(credentials);
    if (metaData?.error === "") {
      setNodePayload(metaData.node_payload);
      setCollectionPayload(metaData.collection_payload);
      setIsLoading(false);
    } else {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setIsLoading(true);
    fetchMetadata();
    setIsLoading(false);
  }, []);

  const resetDocuments = async () => {
    const response = await deleteAllDocuments("DOCUMENTS", credentials);
    if (response) {
      addStatusMessage("All documents reset", "SUCCESS");
      fetchMetadata();
    } else {
      addStatusMessage("Failed to reset documents", "ERROR");
    }
  };

  const resetVerba = async () => {
    const response = await deleteAllDocuments("ALL", credentials);
    if (response) {
      addStatusMessage("Verba reset", "SUCCESS");
      fetchMetadata();
    } else {
      addStatusMessage("Failed to reset Verba", "ERROR");
    }
  };

  const resetConfig = async () => {
    const response = await deleteAllDocuments("CONFIG", credentials);
    if (response) {
      addStatusMessage("Config reset", "SUCCESS");
      fetchMetadata();
    } else {
      addStatusMessage("Failed to reset config", "ERROR");
    }
  };

  const resetSuggestions = async () => {
    const response = await deleteAllDocuments("SUGGESTIONS", credentials);
    if (response) {
      addStatusMessage("Suggestions reset", "SUCCESS");
      fetchMetadata();
    } else {
      addStatusMessage("Failed to reset suggestions", "ERROR");
    }
  };

  const openModal = (modal_id: string) => {
    const modal = document.getElementById(modal_id);
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  return (
    <div className="flex flex-col w-full h-full p-4">
      <div className="flex justify-between items-center mb-4">
        <p className="text-2xl font-bold">Admin Panel</p>
        <VerbaButton
          title="Refresh"
          loading={isLoading}
          onClick={fetchMetadata}
          className="max-w-min"
          Icon={IoReload}
        />
      </div>
      <div className="flex-grow overflow-y-auto">
        <div className="gap-4 flex flex-col p-4 text-text-verba">
          <p className="font-bold text-lg">Resetting Verba</p>
          <div className="flex flex-wrap gap-2 justify-between">
            <div className="flex flex-wrap gap-2">
              <VerbaButton
                title="Clear Documents"
                onClick={() => openModal("reset-documents")}
                Icon={IoDocumentSharp}
              />
              <VerbaButton
                title="Clear Config"
                onClick={() => openModal("reset-configs")}
                Icon={FaWrench}
              />
              <VerbaButton
                title="Clear Everything"
                onClick={() => openModal("reset-verba")}
                Icon={IoTrash}
              />
              <VerbaButton
                title="Clear Suggestions"
                onClick={() => openModal("reset-suggestions")}
                Icon={IoTrash}
              />
            </div>
          </div>
          <p className="font-bold text-lg">Weaviate Information</p>

          <div className="flex flex-col border-2 gap-2 border-bg-verba shadow-sm p-4 rounded-lg">
            <p className="text-sm lg:text-base font-semibold text-text-alt-verba">
              Connected to
            </p>
            <p className="   text-text-verba">{credentials.url}</p>
          </div>

          <div className="flex flex-col border-2 gap-2 border-bg-verba shadow-sm p-4 rounded-lg">
            <p className="text-sm lg:text-base font-semibold text-text-alt-verba">
              Deployment
            </p>
            <p className=" text-text-verba">{credentials.deployment}</p>
          </div>

          <div className="flex flex-col border-2 gap-2 border-secondary-verba shadow-sm p-4 rounded-lg">
            <p className="text-sm lg:text-base font-semibold text-text-alt-verba">
              Version
            </p>
            {nodePayload ? (
              <p className="text-text-verba">{nodePayload.weaviate_version}</p>
            ) : (
              <span className="loading loading-spinner loading-sm"></span>
            )}
          </div>

          <div className="flex flex-col border-2 border-bg-verba shadow-sm p-4 rounded-lg">
            <div className="flex gap-2 items-center">
              <p className="text-text-alt-verba text-sm lg:text-base font-semibold">
                Nodes
              </p>
              {nodePayload ? (
                <p className="text-text-alt-verba text-sm lg:text-base font-semibold">
                  {nodePayload.node_count}
                </p>
              ) : (
                <span className="loading loading-spinner loading-sm"></span>
              )}
            </div>

            {nodePayload ? (
              <ul className="flex flex-col mt-2 list-disc list-inside">
                {nodePayload.nodes.map((node) => (
                  <li
                    key={"Node" + node.name}
                    className="text-sm text-text-verba flex justify-between"
                  >
                    <span className="w-64 truncate">{node.name}</span>
                    <span>
                      ({node.status} - {node.shards} shards)
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <span className="loading loading-dots loading-sm mt-2"></span>
            )}
          </div>

          <div className="flex flex-col border-2 border-bg-verba shadow-sm p-4 rounded-lg">
            <div className="flex gap-2 items-center">
              <p className="text-text-alt-verba text-sm lg:text-base font-semibold">
                Collections
              </p>
              {collectionPayload ? (
                <p className="text-text-alt-verba text-sm lg:text-base font-semibold">
                  {collectionPayload.collection_count}
                </p>
              ) : (
                <span className="loading loading-spinner loading-sm"></span>
              )}
            </div>

            {collectionPayload ? (
              <ul className="flex flex-col mt-2 list-disc list-inside">
                {collectionPayload.collections.map((collection) => (
                  <li
                    key={"Collection" + collection.name}
                    className="text-sm text-text-verba flex justify-between"
                  >
                    <span className="w-128 truncate">{collection.name}</span>
                    <span>{collection.count} objects</span>
                  </li>
                ))}
              </ul>
            ) : (
              <span className="loading loading-dots loading-sm mt-2"></span>
            )}
          </div>
        </div>
      </div>
      <UserModalComponent
        modal_id="reset-documents"
        title="Reset Documents"
        text="Are you sure you want to reset all documents? This will clear all documents and chunks from Verba."
        triggerAccept={resetDocuments}
        triggerString="Reset"
      />
      <UserModalComponent
        modal_id="reset-configs"
        title="Reset Config"
        text="Are you sure you want to reset the config?"
        triggerAccept={resetConfig}
        triggerString="Reset"
      />
      <UserModalComponent
        modal_id="reset-verba"
        title="Reset Verba"
        text="Are you sure you want to reset Verba? This will delete all collections related to Verba."
        triggerAccept={resetVerba}
        triggerString="Reset"
      />
      <UserModalComponent
        modal_id="reset-suggestions"
        title="Reset Suggestions"
        text="Are you sure you want to reset all autocomplete suggestions?"
        triggerAccept={resetSuggestions}
        triggerString="Reset"
      />
    </div>
  );
};

export default InfoView;
