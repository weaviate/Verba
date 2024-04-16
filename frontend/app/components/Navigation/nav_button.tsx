'use client'

import React from 'react';
import { FaStar } from "react-icons/fa";

interface NavbarButtonProps {
  Icon: typeof FaStar;
  iconSize: number;
  title: string;
  currentPage: string;
  setCurrentPage: (page: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG") => void;
  setPage: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG";
}

const NavbarButton: React.FC<NavbarButtonProps> = ({ Icon, iconSize, title, currentPage, setPage, setCurrentPage }) => {

  return (
    <button className={`btn md:btn-sm lg:btn-md flex flex-grow items-center justify-center border-none hover:bg-button-hover-verba ${currentPage === setPage ? ("bg-primary-verba") : "bg-button-verba text-text-alt-verba"}`} onClick={(e) => { setCurrentPage(setPage) }}>
      <Icon size={iconSize} />
      <p className="md:text-xs lg:text-sm sm:hidden md:flex">{title}</p>
    </button>
  );
};

export default NavbarButton;
