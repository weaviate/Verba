"use client";

import React from "react";
import { SettingsConfiguration, ImageFieldSetting } from "./types";

interface ImageFieldComponentProps {
  title: string;
  ImageFieldSetting: ImageFieldSetting;
  setting: "Customization" | "Chat";

  settingsConfig: SettingsConfiguration;
  setSettingsConfig: (settings: any) => void;
}

const ImageFieldComponent: React.FC<ImageFieldComponentProps> = ({
  title,
  ImageFieldSetting,
  setting,
  settingsConfig,
  setSettingsConfig,
}) => {
  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const reader = new FileReader();

      reader.onload = (e) => {
        setSettingsConfig((prevConfig: any) => {
          // Creating a deep copy of prevConfig to avoid mutating the original state directly
          const newConfig = JSON.parse(JSON.stringify(prevConfig));

          // Updating the copied state
          newConfig[setting].settings[title].src = e.target?.result as string;

          // Return the updated copy
          return newConfig;
        });
      };
      reader.readAsDataURL(event.target.files[0]);
    }
  };

  return (
    <div key={title} className="flex flex-col justify-center gap-1">
      <div className="flex justify-center items-center">
        <p>{ImageFieldSetting.description}</p>
      </div>
      <div className="flex justify-center items-center">
        <div>
          <div className="flex justify-center items-center mt-4">
            <img
              src={(settingsConfig[setting].settings as any)[title].src}
              alt="Logo"
              className="max-w-xs max-h-32 rounded-xl"
            />
          </div>
          <div className="flex justify-center items-center mt-1">
            <button
              onClick={() => document.getElementById("LogoImageInput")?.click()}
              className="btn border-none text-xs bg-bg-verba text-text-alt-verba"
            >
              Add Logo
            </button>
            <input
              id={"LogoImageInput"}
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageFieldComponent;
