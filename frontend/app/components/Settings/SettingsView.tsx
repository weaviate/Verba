"use client";

import React, { useState } from "react";

import { RiAdminFill } from "react-icons/ri";
import { FaPaintBrush } from "react-icons/fa";
import { BiSolidCommentError } from "react-icons/bi";
import { IoLogOutSharp } from "react-icons/io5";
import { IoChatboxEllipsesSharp } from "react-icons/io5";
import { FaDatabase } from "react-icons/fa";

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
}

const SettingsView: React.FC<SettingsViewProps> = ({
  selectedTheme,
  themes,
  setThemes,
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
          <div className="bg-bg-alt-verba gap-2 rounded-2xl flex flex-col p-6 h-full w-full overflow-y-auto overflow-x-hidden">
            <button
              key={"Info Button Setting"}
              onClick={() => setSettingMode("INFO")}
              className={`flex ${settingMode === "INFO" ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"}  w-full p-3 rounded-lg items-center text-text-verba gap-2 transition-colors duration-300 ease-in-out border-none`}
            >
              <RiAdminFill size={18} />
              <p className="text-text-verba">Admin</p>
            </button>
            <button
              key={"Theme Button Setting"}
              onClick={() => setSettingMode("THEME")}
              className={`flex ${settingMode === "THEME" ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"}  w-full p-3 rounded-lg items-center text-text-verba gap-2 transition-colors duration-300 ease-in-out border-none`}
            >
              <FaPaintBrush size={18} />
              <p className="text-text-verba">Customize Theme</p>
            </button>
            <button
              key={"Suggestions Button Setting"}
              onClick={() => setSettingMode("SUGGESTIONS")}
              className={`flex ${settingMode === "SUGGESTIONS" ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"}  w-full p-3 rounded-lg items-center text-text-verba gap-2 transition-colors duration-300 ease-in-out border-none`}
            >
              <IoChatboxEllipsesSharp size={18} />
              <p className="text-text-verba">Manage Suggestions</p>
            </button>
            <button
              key={"Logout Button Setting"}
              className={`flex bg-button-verba hover:bg-secondary-verba  w-full p-3 rounded-lg items-center text-text-verba gap-2 transition-colors duration-300 ease-in-out border-none`}
              onClick={() => window.location.reload()}
            >
              <IoLogOutSharp size={18} />
              <p className="text-text-verba">Logout</p>
            </button>
            <button
              key={"Issue Button Setting"}
              className={`flex bg-button-verba hover:bg-secondary-verba  w-full p-3 rounded-lg items-center text-text-verba gap-2 transition-colors duration-300 ease-in-out border-none`}
              onClick={() =>
                window.open(
                  "https://github.com/weaviate/Verba/issues/new/choose",
                  "_blank"
                )
              }
            >
              <BiSolidCommentError size={18} />
              <p className="text-text-verba">Report Issue</p>
            </button>
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
              />
            )}
            {settingMode === "INFO" && <InfoView credentials={credentials} />}
            {settingMode === "SUGGESTIONS" && (
              <SuggestionView credentials={credentials} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsView;
