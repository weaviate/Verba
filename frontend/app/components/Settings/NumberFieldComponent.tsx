"use client";

import React from "react";
import { SettingsConfiguration, NumberFieldSetting } from "./types";

interface NumberFieldComponentProps {
  title: string;
  NumberFieldSetting: NumberFieldSetting;
  setting: "Customization" | "Chat";

  settingsConfig: SettingsConfiguration;
  setSettingsConfig: (settings: any) => void;
}

const NumberFieldComponent: React.FC<NumberFieldComponentProps> = ({
  title,
  NumberFieldSetting,
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
      newConfig[setting].settings[title].value = newText;

      // Return the updated copy
      return newConfig;
    });
  };

  return (
    <div key={title} className="flex flex-col gap-1">
      <div className="flex items-center justify-center">
        <p>{NumberFieldSetting.description}</p>
      </div>
      <div className="flex items-center justify-center">
        <label className="input input-bordered flex items-center gap-2 w-full bg-bg-verba">
          <input
            type="number"
            className="grow"
            placeholder={title}
            value={(settingsConfig[setting].settings as any)[title].value}
            onChange={handleChange}
          />
        </label>
      </div>
    </div>
  );
};

export default NumberFieldComponent;
