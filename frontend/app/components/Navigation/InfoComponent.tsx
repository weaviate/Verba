"use client";

import React from "react";
import { FaInfo } from "react-icons/fa";

interface InfoComponentProps {
  tooltip_text: string;
  display_text: string;
}

const InfoComponent: React.FC<InfoComponentProps> = ({
  tooltip_text,
  display_text,
}) => {
  return (
    <div className={`items-center gap-2 flex`}>
      <div className="tooltip tooltip-right text-xs" data-tip={tooltip_text}>
        <button className="btn btn-circle btn-sm border-none text-text-alt-verba bg-button-verba hover:bg-secondary-verba hover:text-text-verba">
          <FaInfo />
        </button>
      </div>
      <p
        className="text-sm text-text-alt-verba truncate max-w-[350px]"
        title={display_text}
      >
        {display_text}
      </p>
    </div>
  );
};

export default InfoComponent;
