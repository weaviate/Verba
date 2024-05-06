"use client";

import React from "react";
import { SettingsConfiguration, CheckboxSetting } from "./types";

interface CheckComponent {
  title: string;
  CheckboxSetting: CheckboxSetting;
  setting: "Customization" | "Chat";

  settingsConfig: SettingsConfiguration;
  setSettingsConfig: (settings: any) => void;
}

const CheckComponent: React.FC<CheckComponent> = ({
  title,
  CheckboxSetting,
  setting,
  settingsConfig,
  setSettingsConfig,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newText = e.target.checked;
    setSettingsConfig((prevConfig: any) => {
      // Creating a deep copy of prevConfig to avoid mutating the original state directly
      const newConfig = JSON.parse(JSON.stringify(prevConfig));

      // Updating the copied state
      newConfig[setting].settings[title].checked = newText;

      // Return the updated copy
      return newConfig;
    });
  };

  return (
    <div key={title} className="flex flex-col gap-2">
      <div className="flex items-center justify-center">
        <p>{CheckboxSetting.description}</p>
      </div>
      <div className="flex items-center justify-center">
        <input
          type="checkbox"
          className="toggle"
          checked={(settingsConfig[setting].settings as any)[title].checked}
          onChange={handleChange}
        />
      </div>
    </div>
  );
};

export default CheckComponent;
