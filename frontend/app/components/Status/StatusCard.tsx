"use client";

import React from "react";

interface StatusCardProps {
  title: string;
  value: number | null;
  checked: boolean;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, value, checked }) => {
  return (
    <div
      className={`flex p-3 rounded-lg ${checked ? "bg-secondary-verba" : "bg-bg-verba"}`}
    >
      <div className="flex gap-2 text-text-verba items-center">
        <p>{title}</p>
        <div className="text-xs lg:text-sm text-text-verba">
          {value !== null ? (
            <p>{value}</p>
          ) : (
            <p>{checked ? "Available" : "Not Available"}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatusCard;
