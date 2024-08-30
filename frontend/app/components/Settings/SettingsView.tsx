"use client";

import React, { useState } from "react";

import { RiAdminFill } from "react-icons/ri";
import { FaPaintBrush } from "react-icons/fa";
import { BiSolidCommentError } from "react-icons/bi";
import { IoLogOutSharp } from "react-icons/io5";
import { IoChatboxEllipsesSharp } from "react-icons/io5";

import VerbaButton from "../Navigation/VerbaButton";

import { Theme, Themes, Credentials } from "@/app/types";

import SettingsComponent from "./SettingsComponent";

import InfoComponent from "../Navigation/InfoComponent";
import SuggestionView from "./SuggestionView";
import InfoView from "./InfoView";

interface SettingsViewProps {
  selectedTheme: Theme;
  setSelectedTheme: React.Dispatch<React.SetStateAction<Theme>>;
  themes: Themes;
  setThemes: React.Dispatch<React.SetStateAction<Themes>>;
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const SettingsView: React.FC<SettingsViewProps> = ({
  selectedTheme,
  themes,
  setThemes,
  addStatusMessage,
  setSelectedTheme,
  credentials,
}) => {
  const [settingMode, setSettingMode] = useState<
    "INFO" | "ADMIN" | "THEME" | "SUGGESTIONS" | "CACHE"
  >("INFO");

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div className={`w-1/3 flex`}>
        <div className="flex flex-col gap-2 w-full">
          <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
            <div className="flex gap-2 justify-start ">
              <InfoComponent
                tooltip_text="Customize Verba's Theme, reset collections, logout or report issues."
                display_text={"Settings"}
              />
            </div>
          </div>
          <div className="bg-bg-alt-verba gap-2 rounded-2xl flex flex-col p-6 w-full overflow-y-auto overflow-x-hidden">
            <VerbaButton
              title="Admin"
              onClick={() => setSettingMode("INFO")}
              selected={settingMode === "INFO"}
              selected_color="bg-secondary-verba"
              Icon={RiAdminFill}
            />
            <VerbaButton
              title="Customize Theme"
              onClick={() => setSettingMode("THEME")}
              selected={settingMode === "THEME"}
              selected_color="bg-secondary-verba"
              Icon={FaPaintBrush}
            />
            <VerbaButton
              title="Manage Suggestions"
              onClick={() => setSettingMode("SUGGESTIONS")}
              selected={settingMode === "SUGGESTIONS"}
              selected_color="bg-secondary-verba"
              Icon={IoChatboxEllipsesSharp}
            />
          </div>
          <div className="bg-bg-alt-verba gap-2 rounded-2xl flex flex-col p-6 w-full overflow-y-auto overflow-x-hidden">
            <VerbaButton
              title="Logout"
              onClick={() => window.location.reload()}
              Icon={IoLogOutSharp}
            />
            <VerbaButton
              title="Report Issue"
              onClick={() =>
                window.open(
                  "https://github.com/weaviate/Verba/issues/new/choose",
                  "_blank"
                )
              }
              Icon={BiSolidCommentError}
            />
          </div>
        </div>
      </div>

      <div className={`w-2/3 flex`}>
        <div className="flex flex-col gap-2 w-full">
          <div className="bg-bg-alt-verba gap-2 rounded-2xl flex flex-col p-6 h-full w-full overflow-y-auto overflow-x-hidden">
            {settingMode === "THEME" && (
              <SettingsComponent
                themes={themes}
                credentials={credentials}
                setThemes={setThemes}
                setSelectedTheme={setSelectedTheme}
                selectedTheme={selectedTheme}
                addStatusMessage={addStatusMessage}
              />
            )}
            {settingMode === "INFO" && (
              <InfoView
                addStatusMessage={addStatusMessage}
                credentials={credentials}
              />
            )}
            {settingMode === "SUGGESTIONS" && (
              <SuggestionView
                credentials={credentials}
                addStatusMessage={addStatusMessage}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsView;
