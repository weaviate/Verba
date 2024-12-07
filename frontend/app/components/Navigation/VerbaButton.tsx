"use client";

import React from "react";
import { FaStar } from "react-icons/fa";

interface VerbaButtonProps {
  title?: string;
  Icon?: typeof FaStar;
  onClick?: (...args: any[]) => void; // Updated to accept any number of arguments
  onMouseEnter?: (...args: any[]) => void;
  onMouseLeave?: (...args: any[]) => void;
  disabled?: boolean;
  key?: string;
  className?: string;
  type?: "button" | "submit" | "reset";
  selected?: boolean;
  selected_color?: string;
  selected_text_color?: string;
  circle?: boolean;
  text_class_name?: string;
  loading?: boolean;
  text_size?: string;
  icon_size?: number;
  onClickParams?: any[]; // New prop to pass additional parameters
}

const VerbaButton: React.FC<VerbaButtonProps> = ({
  title = "",
  key = "Button" + title,
  Icon,
  onClick = () => {},
  onMouseEnter = () => {},
  onMouseLeave = () => {},
  disabled = false,
  className = "",
  text_class_name = "",
  selected = false,
  selected_color = "bg-button-verba",
  selected_text_color = "text-text-verba-button",
  text_size = "text-xs",
  icon_size = 12,
  type = "button",
  loading = false,
  circle = false,
  onClickParams = [],
}) => {
  return (
    <button
      type={type}
      key={key}
      className={
        className +
        ` p-3 transition-all active:scale-95 scale-100 duration-300 flex gap-1 items-center justify-center ${circle ? "rounded-full" : "rounded-lg"} hover:bg-button-hover-verba hover:text-text-verba-button ${selected ? selected_color + " shadow-md " + selected_text_color : " bg-button-verba text-text-alt-verba-button"} `
      }
      onClick={(e) => onClick(e, ...onClickParams)}
      disabled={disabled}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {loading ? (
        <span className="text-text-verba-button loading loading-spinner loading-xs"></span>
      ) : (
        <>
          {Icon && <Icon size={icon_size} className="w-[20px]" />}
          {title && (
            <p title={title} className={text_size + " " + text_class_name}>
              {title}
            </p>
          )}
        </>
      )}
    </button>
  );
};

export default VerbaButton;
