"use client";

import React from "react";
import { FaStar } from "react-icons/fa";

interface NavbarButtonProps {
  Icon: typeof FaStar;
  iconSize: number;
  title: string;
  currentPage: string;
  setCurrentPage: (
    page: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG"
  ) => void;
  setPage: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG";
  APIHost: string | null;
  hide: boolean;
}

const NavbarButton: React.FC<NavbarButtonProps> = ({
  Icon,
  iconSize,
  title,
  currentPage,
  setPage,
  setCurrentPage,
  APIHost,
  hide,
}) => {
  return (
    <button
      disabled={APIHost === null}
      key={title}
      className={`btn md:btn-sm lg:btn-md ${hide ? "hidden" : "flex"} flex-grow items-center justify-center border-none hover:bg-button-hover-verba ${currentPage === setPage ? "bg-primary-verba text-text-verba" : "bg-button-verba text-text-alt-verba"}`}
      onClick={(e) => {
        setCurrentPage(setPage);
      }}
    >
      <Icon size={iconSize} />
      <p className="md:text-xs lg:text-sm sm:hidden md:flex">{title}</p>
    </button>
  );
};

export default NavbarButton;
