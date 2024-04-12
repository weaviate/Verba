'use client'

import React, { useState, useEffect } from 'react';

import { IoChatbubbleSharp } from "react-icons/io5";
import { IoDocumentSharp } from "react-icons/io5";
import { HiOutlineStatusOnline } from "react-icons/hi";
import { IoMdAddCircle } from "react-icons/io";
import { IoSettingsSharp } from "react-icons/io5";
import { FaGithub } from "react-icons/fa";
import { IoBuildSharp } from "react-icons/io5";

import NavbarButton from "./nav_button"
import { getGitHubStars } from "./actions"

interface NavbarProps {
  imageSrc: string;
  title: string;
  subtitle: string;
  version: string;
  currentPage: string;
  setCurrentPage: (page: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG") => void;
}

const formatGitHubNumber = (num: number): string => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
  }
  return num.toString();
}

const Navbar: React.FC<NavbarProps> = ({ imageSrc, title, subtitle, version, currentPage, setCurrentPage }) => {

  const [gitHubStars, setGitHubStars] = useState("0")
  const icon_size = 18

  useEffect(() => {
    // Declare an asynchronous function inside the useEffect
    const fetchGitHubStars = async () => {
      try {
        // Await the asynchronous call to getGitHubStars
        const response: number = await getGitHubStars();

        if (response) {
          // Now response is the resolved value of the promise
          const formatedStars = formatGitHubNumber(response);
          console.log(formatedStars);
          setGitHubStars(formatedStars);
        }
      } catch (error) {
        console.error('Failed to fetch GitHub stars:', error);
      }
    };

    // Call the async function
    fetchGitHubStars();
  }, []);

  const handleGitHubClick = () => {
    // Open a new tab with the specified URL
    window.open("https://github.com/weaviate/verba", '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="flex justify-between items-center mb-10">

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
          <NavbarButton Icon={IoChatbubbleSharp} iconSize={icon_size} title='Chat' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='CHAT' />
          <NavbarButton Icon={IoDocumentSharp} iconSize={icon_size} title='Documents' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='DOCUMENTS' />
          <NavbarButton Icon={HiOutlineStatusOnline} iconSize={icon_size} title='Status' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='STATUS' />
        </div>

        <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px sm:mx-2 md:mx-4"></div>

        {/* Menus */}
        <div className="flex flex-row items-center sm:gap-1 lg:gap-5 justify-between">
          <NavbarButton Icon={IoMdAddCircle} iconSize={icon_size} title='Add Documents' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='ADD' />
          <NavbarButton Icon={IoBuildSharp} iconSize={icon_size} title='RAG' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='RAG' />
        </div>

        <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px sm:mx-2 md:mx-4"></div>

        {/* Github, Version */}
        <div className="flex flex-row items-center sm:gap-1 lg:gap-5 justify-between">
          <NavbarButton Icon={IoSettingsSharp} iconSize={icon_size} title='Settings' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='SETTINGS' />

          <button className={`btn md:btn-sm lg:btn-md flex items-center justify-center border-none bg-secondary-verba hover:bg-white`} onClick={handleGitHubClick}>
            <FaGithub size={icon_size} className='' />
            <p className="text-xs sm:hidden md:flex ">{gitHubStars}</p>
          </button>
          <p className="text-sm text-text-alt-verba hidden md:flex">{version}</p>

        </div>

      </div>

    </div>
  );
};

export default Navbar;
