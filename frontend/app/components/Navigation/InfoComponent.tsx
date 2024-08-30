"use client";

import React, { useState } from "react";
import { FaInfo } from "react-icons/fa";
import VerbaButton from "./VerbaButton";

interface InfoComponentProps {
  tooltip_text: string;
  display_text: string;
}

const InfoComponent: React.FC<InfoComponentProps> = ({
  tooltip_text,
  display_text,
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className={`items-center gap-2 flex`}>
      <div className="relative">
        <VerbaButton
          title=""
          Icon={FaInfo}
          icon_size={10}
          disabled={false}
          selected={false}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          circle={true}
          button_size="btn-xs"
        />
        <div
          className={`absolute left-full z-30 p-4 bg-bg-verba text-text-alt-verba text-xs rounded-xl shadow-md w-[300px] transition-opacity duration-300 ${
            showTooltip ? "opacity-100" : "opacity-0 pointer-events-none"
          }`}
        >
          <p className="w-full whitespace-normal">{tooltip_text}</p>
        </div>
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
