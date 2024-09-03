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
  button_size?: string;
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
  text_size = "text-sm",
  icon_size = 15,
  type = "button",
  loading = false,
  circle = false,
  button_size = "",
  onClickParams = [],
}) => {
  return (
    <button
      type={type}
      key={key}
      className={
        className +
        ` btn rounded-lg flex-grow items-center justify-center border-none ${circle ? "btn-circle" : ""} ${button_size} hover:bg-button-hover-verba hover:text-text-verba-button ${selected ? selected_color + " shadow-md " + selected_text_color : " bg-button-verba shadow-none text-text-alt-verba-button"} `
      }
      onClick={(e) => onClick(e, ...onClickParams)}
      disabled={disabled}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {loading ? (
        <span className="text-text-verba-button loading loading-spinner loading-sm"></span>
      ) : (
        <>
          <div className="flex gap-2 items-center">
            {Icon && <Icon size={icon_size} className="w-[20px]" />}
            {title && (
              <p title={title} className={text_size + " " + text_class_name}>
                {title}
              </p>
            )}
          </div>
        </>
      )}
    </button>
  );
};

export default VerbaButton;
