'use client'

import React, { useState, useEffect } from 'react';

import { IoChatbubbleSharp } from "react-icons/io5";
import { IoDocumentSharp } from "react-icons/io5";
import { HiOutlineStatusOnline } from "react-icons/hi";
import { IoMdAddCircle } from "react-icons/io";
import { IoSettingsSharp } from "react-icons/io5";
import { FaGithub } from "react-icons/fa";
import { IoBuildSharp } from "react-icons/io5";
import { LuMenu } from "react-icons/lu";

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
      <div className="flex flex-row items-center gap-5">
        <img src={imageSrc} width={80} className="flex"></img>
        <div className="flex flex-col lg:flex-row lg:items-end justify-center lg:gap-3">
          <p className="sm:text-2xl md:text-3xl text-text-verba">{title}</p>
          <p className="sm:text-sm text-base text-text-alt-verba font-light">{subtitle}</p>
        </div>
      </div>

      <div className="flex flex-row justify-center items-center">

        <div className="hidden sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px sm:mx-2 md:mx-4"></div>

        {/* Pages */}
        <div className="lg:flex hidden lg:flex-row items-center lg:gap-3 justify-between">
          <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px mx-1"></div>
          <NavbarButton Icon={IoChatbubbleSharp} iconSize={icon_size} title='Chat' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='CHAT' />
          <NavbarButton Icon={IoDocumentSharp} iconSize={icon_size} title='Documents' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='DOCUMENTS' />
          <NavbarButton Icon={HiOutlineStatusOnline} iconSize={icon_size} title='Status' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='STATUS' />
          <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px mx-1"></div>
          <NavbarButton Icon={IoMdAddCircle} iconSize={icon_size} title='Add Documents' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='ADD' />
          <NavbarButton Icon={IoBuildSharp} iconSize={icon_size} title='RAG' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='RAG' />
          <NavbarButton Icon={IoSettingsSharp} iconSize={icon_size} title='Settings' currentPage={currentPage} setCurrentPage={setCurrentPage} setPage='SETTINGS' />
          <div className="hidden sm:block sm:h-[3vh] lg:h-[5vh] bg-text-alt-verba w-px mx-1"></div>

          <button className={`md:hidden btn md:btn-sm lg:btn-md lg:flex items-center justify-center border-none bg-secondary-verba hover:bg-button-hover-verba`} onClick={handleGitHubClick}>
            <FaGithub size={icon_size} className='' />
            <p className="text-xs sm:hidden md:flex ">{gitHubStars}</p>
          </button>
          <p className="hidden lg:flex text-xs text-text-alt-verba">{version}</p>
        </div>

      </div>

      {/* Menu */}
      <div className="flex flex-row items-center sm:gap-1 lg:gap-5 justify-between">
        <div className='lg:hidden sm:flex md:ml-4 sm:mr-8'>
          <ul className="menu md:menu-md sm:menu-sm sm:menu-horizontal bg-base-200 rounded-box bg-bg-alt-verba z-50">
            <li>
              <details>
                <summary><LuMenu size={20} /></summary>
                <ul className='bg-bg-alt-verba'>
                  <li onClick={(e) => { setCurrentPage("CHAT") }}><a>Chat</a></li>
                  <li onClick={(e) => { setCurrentPage("DOCUMENTS") }}><a>Documents</a></li>
                  <li onClick={(e) => { setCurrentPage("STATUS") }}><a>Status</a></li>
                  <li onClick={(e) => { setCurrentPage("ADD") }}><a>Add Documents</a></li>
                  <li onClick={(e) => { setCurrentPage("RAG") }}><a>RAG</a></li>
                  <li onClick={(e) => { setCurrentPage("SETTINGS") }}><a>Settings</a></li>
                  <li onClick={handleGitHubClick}><a>GitHub</a></li>
                  <li className='items-center justify-center text-xs text-text-alt-verba mt-2'>{version}</li>
                </ul>
              </details>
            </li>
          </ul>
        </div>
      </div>

    </div>
  );
};

export default Navbar;
