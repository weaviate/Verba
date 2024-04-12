'use client'

import React, { useState, useEffect } from 'react';

import { IoChatbubbleSharp } from "react-icons/io5";
import { IoDocumentSharp } from "react-icons/io5";
import { HiOutlineStatusOnline } from "react-icons/hi";
import { IoMdAddCircle } from "react-icons/io";
import { IoSettingsSharp } from "react-icons/io5";
import { FaGithub } from "react-icons/fa";

import { getGitHubStars } from "./actions"
import { get } from 'http';

interface NavbarProps {
  imageSrc: string;
  title: string;
  subtitle: string;
  version: string;
  currentPage: string;
  setCurrentPage: (page: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS") => void;
}

const Navbar: React.FC<NavbarProps> = ({ imageSrc, title, subtitle, version, currentPage, setCurrentPage }) => {

  const [gitHubStars, setGitHubStars] = useState(0)
  const icon_size = 18


  useEffect(() => {
    const response = getGitHubStars()
  }, []);

  const handleGitHubClick = () => {
    // Open a new tab with the specified URL
    window.open("https://github.com/weaviate/verba", '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="flex justify-between items-center">

      {/* Logo, Title, Subtitle */}
      <div className="sm:hidden md:flex flex-row items-center gap-5">
        <img src={imageSrc} width={80} className="sm:hidden md:flex shadow-xl rounded-lg"></img>
        <div className="sm:hidden md:flex md:flex-col lg:flex-row lg:items-end justify-center lg:gap-3">
          <p className=" text-4xl text-text-verba">{title}</p>
          <p className="text-base text-text-alt-verba font-light">{subtitle}</p>
        </div>
      </div>

      <div className="flex flex-row justify-center md:justify-end items-center">

        <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px sm:mx-2 md:mx-4"></div>

        {/* Pages */}
        <div className="flex flex-row items-center sm:gap-1 lg:gap-5 justify-between">
          <button className={`btn md:btn-sm lg:btn-md flex flex-grow items-center justify-center border-none ${currentPage === "CHAT" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setCurrentPage("CHAT") }}>
            <IoChatbubbleSharp size={icon_size} />
            <p className="md:text-xs lg:text-sm sm:hidden md:flex">Chat</p>
          </button>
          <button className={`btn md:btn-sm lg:btn-md flex flex-row items-center justify-center border-none ${currentPage === "DOCUMENTS" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setCurrentPage("DOCUMENTS") }}>
            <IoDocumentSharp size={icon_size} />
            <p className="md:text-xs lg:text-sm sm:hidden md:flex">Documents</p>
          </button>
          <button className={`btn md:btn-sm lg:btn-md flex flex-row items-center justify-center border-none ${currentPage === "STATUS" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setCurrentPage("STATUS") }}>
            <HiOutlineStatusOnline size={icon_size} />
            <p className="md:text-xs lg:text-sm sm:hidden md:flex">Status</p>
          </button>
        </div>


        <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px sm:mx-2 md:mx-4"></div>

        {/* Menus */}
        <div className="flex flex-row items-center sm:gap-1 lg:gap-5 justify-between">
          <button className={`btn md:btn-sm lg:btn-md flex items-center justify-center border-none ${currentPage === "ADD" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setCurrentPage("ADD") }}>
            <IoMdAddCircle size={icon_size} />
            <p className="md:text-xs lg:text-sm sm:hidden md:flex">Add Documents</p>
          </button>
          <button className={`btn md:btn-sm lg:btn-md flex flex-row items-center justify-center border-none ${currentPage === "SETTINGS" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setCurrentPage("SETTINGS") }}>
            <IoSettingsSharp size={icon_size} />
            <p className="md:text-xs lg:text-sm sm:hidden md:flex">Settings</p>
          </button>
        </div>

        <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px sm:mx-2 md:mx-4"></div>

        {/* Github, Version */}
        <div className="flex flex-row items-center sm:gap-1 lg:gap-5 justify-between">
          <button className={`btn md:btn-sm lg:btn-md flex items-center justify-center border-none `} onClick={handleGitHubClick}>
            <FaGithub size={icon_size} />
          </button>
          <p className="text-sm text-text-alt-verba hidden md:flex">{version}</p>

        </div>

      </div>

    </div>
  );
};

export default Navbar;
