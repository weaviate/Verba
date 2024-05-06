"use client";

import React from "react";
import { FaInfo } from "react-icons/fa";

import { SettingsConfiguration } from "../Settings/types";

interface InfoComponentProps {
  settingConfig: SettingsConfiguration;
  tooltip_text: string;
  display_text: string;
}

const InfoComponent: React.FC<InfoComponentProps> = ({
  tooltip_text,
  display_text,
  settingConfig,
}) => {
  return (
    <div
      className={`items-center gap-2 ${settingConfig.Chat.settings.info_button.checked ? "flex" : "hidden"}`}
    >
      <div className="tooltip tooltip-right text-xs" data-tip={tooltip_text}>
        <button className="btn btn-circle btn-sm border-none bg-bg-verba hover:bg-secondary-verba text-text-verba">
          <FaInfo />
        </button>
      </div>
      <p className="text-sm text-text-alt-verba">{display_text}</p>
    </div>
  );
};

export default InfoComponent;
