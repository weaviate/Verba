"use client";

import React from "react";
import { SettingsConfiguration, ColorSetting } from "./types";
import { HexColorPicker } from "react-colorful";

interface ColorFieldComponentProps {
  title: string;
  ColorSetting: ColorSetting;
  setting: "Customization" | "Chat";

  settingsConfig: SettingsConfiguration;
  setSettingsConfig: (settings: any) => void;
}

const ColorFieldComponent: React.FC<ColorFieldComponentProps> = ({
  title,
  ColorSetting,
  setting,
  settingsConfig,
  setSettingsConfig,
}) => {
  const handleChange = (e: string) => {
    setSettingsConfig((prevConfig: any) => {
      // Creating a deep copy of prevConfig to avoid mutating the original state directly
      const newConfig = JSON.parse(JSON.stringify(prevConfig));

      // Updating the copied state
      newConfig[setting].settings[title].color = e;

      // Return the updated copy
      return newConfig;
    });
  };

  return (
    <div key={title} className="flex flex-col justify-center gap-1">
      <div className="flex justify-center items-center">
        <p>{ColorSetting.description}</p>
      </div>
      <div className="flex gap-2 justify-center items-center">
        <div className="flex flex-col gap-1 h-[15vh]">
          <label className="input bg-bg-verba input-sm input-bordered flex items-center gap-2 w-full">
            <input
              type="text"
              className="grow"
              placeholder={title}
              value={(settingsConfig[setting].settings as any)[title].color}
              onChange={(e) => {
                handleChange(e.target.value);
              }}
            />
          </label>
          <HexColorPicker
            color={(settingsConfig[setting].settings as any)[title].color}
            onChange={(newColor: string) => {
              handleChange(newColor);
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ColorFieldComponent;
