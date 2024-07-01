"use client";

import React from "react";
import { SettingsConfiguration, SelectSetting } from "./types";

interface SelectComponentProps {
  title: string;
  SelectSetting: SelectSetting;
  setting: "Customization" | "Chat";

  settingsConfig: SettingsConfiguration;
  setSettingsConfig: (settings: any) => void;
}

const SelectComponent: React.FC<SelectComponentProps> = ({
  title,
  SelectSetting,
  setting,
  settingsConfig,
  setSettingsConfig,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newText = e.target.value;
    setSettingsConfig((prevConfig: any) => {
      // Creating a deep copy of prevConfig to avoid mutating the original state directly
      const newConfig = JSON.parse(JSON.stringify(prevConfig));

      // Updating the copied state
      newConfig[setting].settings[title].value = newText;

      // Return the updated copy
      return newConfig;
    });
  };

  return (
    <div key={title} className="flex flex-col gap-1">
      <div className="flex items-center justify-center">
        <p>{SelectSetting.description}</p>
      </div>
      <div className="flex items-center justify-center">
        <select
          value={(settingsConfig[setting].settings as any)[title].value}
          onChange={handleChange}
          className="select bg-bg-verba"
        >
          {SelectSetting.options.map((template) => (
            <option key={"Select_" + template}>{template}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default SelectComponent;
