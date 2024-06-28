"use client";

import React from "react";

interface StatusLabelProps {
  status: boolean;
  true_text: string;
  false_text: string;
}

const StatusLabel: React.FC<StatusLabelProps> = ({
  status,
  true_text,
  false_text,
}) => {
  return (
    <div
      className={`p-2 rounded-lg text-text-verba text-sm ${status ? "bg-secondary-verba" : "bg-bg-alt-verba text-text-alt-verba"}`}
    >
      <p
        className={`text-xs ${status ? "text-text-verba" : "text-text-alt-verba"}`}
      >
        {status ? true_text : false_text}
      </p>
    </div>
  );
};

export default StatusLabel;
