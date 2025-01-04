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
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="relative cursor-pointer flex flex-col items-center text-text-alt-verba"
      >
        <p className="text-sm ml-3">{display_text}</p>
        <div
          className={`absolute top-full left-full mt-2 z-30 p-4 bg-bg-verba text-text-alt-verba text-xs rounded-xl shadow-md w-[300px] transition-opacity duration-300 ${
            showTooltip ? "opacity-100" : "opacity-0 pointer-events-none"
          }`}
        >
          <p className="w-full text-xs whitespace-normal">{tooltip_text}</p>
        </div>
      </div>
    </div>
  );
};

export default InfoComponent;
