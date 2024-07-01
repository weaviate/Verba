"use client";
import React from "react";
import { SettingsConfiguration } from "../Settings/types";

import { SchemaStatus } from "./types";
import { MdDelete } from "react-icons/md";

import StatusLabel from "../Chat/StatusLabel";
import StatusCard from "./StatusCard";
import PulseLoader from "react-spinners/PulseLoader";

import UserModalComponent from "../Navigation/UserModal";

interface AdminConsoleComponentProps {
  type: string | null;
  connected: string;
  schemas: SchemaStatus | null;
  isFetching: boolean;
  settingConfig: SettingsConfiguration;
  reset_verba: (m: string) => void;
}

const AdminConsoleComponent: React.FC<AdminConsoleComponentProps> = ({
  type,
  connected,
  isFetching,
  schemas,
  settingConfig,
  reset_verba,
}) => {
  const openResetVerba = () => {
    const modal = document.getElementById("reset_verba_modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const openResetDocuments = () => {
    const modal = document.getElementById("reset_documents_modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const openResetCache = () => {
    const modal = document.getElementById("reset_cache_modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const openResetSuggestions = () => {
    const modal = document.getElementById("reset_suggestions_modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  const openConfigSuggestions = () => {
    const modal = document.getElementById("reset_config_modal");
    if (modal instanceof HTMLDialogElement) {
      modal.showModal();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-6 h-[65vh] overflow-auto">
        <div className="flex lg:flex-row flex-col gap-2">
          <p className="text-text-verba font-bold text-lg">Admin Console</p>
          <div className="flex gap-2">
            <StatusLabel
              status={type !== null}
              true_text={type ? type : ""}
              false_text={type ? type : ""}
            />
            <StatusLabel
              status={connected === "Online"}
              true_text={connected}
              false_text="Connecting..."
            />
          </div>
        </div>

        {isFetching && (
          <div className="flex items-center justify-center pl-4 mb-4 gap-3">
            <PulseLoader
              color={settingConfig.Customization.settings.text_color.color}
              loading={true}
              size={10}
              speedMultiplier={0.75}
            />
            <p>Loading Stats</p>
          </div>
        )}

        {connected === "Online" && (
          <div className="gap-2 grid grid-cols-2">
            <button
              onClick={openResetVerba}
              className="btn bg-button-verba text-text-verba border-none hover:bg-warning-verba flex gap-2"
            >
              <div className="hidden lg:flex">
                <MdDelete />
              </div>
              <p className="flex text-xs">Reset Verba</p>
            </button>
            <button
              onClick={openResetDocuments}
              className="btn bg-button-verba text-text-verba border-none hover:bg-warning-verba flex gap-2"
            >
              <div className="hidden lg:flex">
                <MdDelete />
              </div>
              <p className="flex text-xs">Reset Documents</p>
            </button>
            <button
              onClick={openResetCache}
              className="btn bg-button-verba text-text-verba border-none hover:bg-warning-verba flex gap-2"
            >
              <div className="hidden lg:flex">
                <MdDelete />
              </div>
              <p className="flex text-xs">Reset Cache</p>
            </button>
            <button
              onClick={openResetSuggestions}
              className="btn bg-button-verba text-text-verba border-none hover:bg-warning-verba flex gap-2"
            >
              <div className="hidden lg:flex">
                <MdDelete />
              </div>
              <p className="flex text-xs">Reset Suggestion</p>
            </button>
            <button
              onClick={openConfigSuggestions}
              className="btn bg-button-verba text-text-verba border-none hover:bg-warning-verba flex gap-2"
            >
              <div className="hidden lg:flex">
                <MdDelete />
              </div>
              <p className="flex text-xs">Reset Config</p>
            </button>
          </div>
        )}

        <div className="flex flex-col gap-2">
          {schemas &&
            Object.entries(schemas).map(([key, value]) => (
              <StatusCard
                key={key + "SCHEMA"}
                title={key}
                value={value}
                checked={false}
              />
            ))}
        </div>
      </div>

      <UserModalComponent
        modal_id="reset_verba_modal"
        title="Reset Verba"
        text={"Do you want to delete all data Verba data?"}
        triggerString="Reset"
        triggerValue="VERBA"
        triggerAccept={reset_verba}
      />
      <UserModalComponent
        modal_id="reset_documents_modal"
        title="Reset Documents"
        text={"Do you want to delete all documents?"}
        triggerString="Reset"
        triggerValue="DOCUMENTS"
        triggerAccept={reset_verba}
      />
      <UserModalComponent
        modal_id="reset_cache_modal"
        title="Reset Cache"
        text={"Do you want to delete all cached data?"}
        triggerString="Reset"
        triggerValue="CACHE"
        triggerAccept={reset_verba}
      />
      <UserModalComponent
        modal_id="reset_suggestions_modal"
        title="Reset Suggestions"
        text={"Do you want to delete all autocompletion suggestions?"}
        triggerString="Reset"
        triggerValue="SUGGESTIONS"
        triggerAccept={reset_verba}
      />
      <UserModalComponent
        modal_id="reset_config_modal"
        title="Reset Configuration"
        text={"Do you want to reset your Verba configuration?"}
        triggerString="Reset"
        triggerValue="CONFIG"
        triggerAccept={reset_verba}
      />
    </div>
  );
};

export default AdminConsoleComponent;
