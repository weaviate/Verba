"use client";

import React from "react";
import { SettingsConfiguration, TextFieldSetting } from "./types";

interface TextFieldComponentProps {
  title: string;
  TextFieldSetting: TextFieldSetting;
  setting: "Customization" | "Chat";

  settingsConfig: SettingsConfiguration;
  setSettingsConfig: (settings: any) => void;
}

const TextFieldComponent: React.FC<TextFieldComponentProps> = ({
  title,
  TextFieldSetting,
  setting,
  settingsConfig,
  setSettingsConfig,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newText = e.target.value;
    setSettingsConfig((prevConfig: any) => {
      // Creating a deep copy of prevConfig to avoid mutating the original state directly
      const newConfig = JSON.parse(JSON.stringify(prevConfig));

      // Updating the copied state
      newConfig[setting].settings[title].text = newText;

      // Return the updated copy
      return newConfig;
    });
  };

  return (
    <div key={title} className="flex flex-col gap-1">
      <div className="flex items-center justify-center">
        <p>{TextFieldSetting.description}</p>
      </div>
      <div className="flex items-center justify-center">
        <label className="input input-bordered flex items-center gap-2 w-full bg-bg-verba">
          <input
            type="text"
            className="grow"
            placeholder={title}
            value={(settingsConfig[setting].settings as any)[title].text}
            onChange={handleChange}
          />
        </label>
      </div>
    </div>
  );
};

export default TextFieldComponent;
