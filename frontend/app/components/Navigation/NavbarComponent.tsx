"use client";

import React, { useState, useEffect } from "react";

import { IoChatbubbleSharp } from "react-icons/io5";
import { IoDocumentSharp } from "react-icons/io5";
import { IoMdAddCircle } from "react-icons/io";
import { IoSettingsSharp } from "react-icons/io5";
import { FaGithub } from "react-icons/fa";
import { TiThMenu } from "react-icons/ti";

import { closeOnClick } from "@/app/util";

import VerbaButton from "./VerbaButton";

import NavbarButton from "./NavButton";
import { getGitHubStars } from "./util";

interface NavbarProps {
  imageSrc: string;
  title: string;
  subtitle: string;
  version: string;
  currentPage: string;
  production: "Local" | "Demo" | "Production";
  setCurrentPage: (
    page: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG"
  ) => void;
}

const formatGitHubNumber = (num: number): string => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  }
  return num.toString();
};

const Navbar: React.FC<NavbarProps> = ({
  imageSrc,
  title,
  subtitle,
  currentPage,
  setCurrentPage,
  production,
}) => {
  const [gitHubStars, setGitHubStars] = useState("0");
  const icon_size = 18;

  useEffect(() => {
    // Declare an asynchronous function inside the useEffect
    const fetchGitHubStars = async () => {
      try {
        // Await the asynchronous call to getGitHubStars
        const response: number = await getGitHubStars();

        if (response) {
          // Now response is the resolved value of the promise
          const formatedStars = formatGitHubNumber(response);
          setGitHubStars(formatedStars);
        }
      } catch (error) {
        console.error("Failed to fetch GitHub stars:", error);
      }
    };

    // Call the async function
    fetchGitHubStars();
  }, []);

  const handleGitHubClick = () => {
    // Open a new tab with the specified URL
    window.open(
      "https://github.com/weaviate/verba",
      "_blank",
      "noopener,noreferrer"
    );
  };

  return (
    <div className="flex justify-between items-center mb-10">
      {/* Logo, Title, Subtitle */}
      <div className="flex flex-row items-center gap-5">
        <img
          src={imageSrc}
          className="flex rounded-lg w-[50px] md:w-[80px] md:h-[80px] object-contain"
        />
        <div className="flex flex-col lg:flex-row lg:items-end justify-center lg:gap-3">
          <p className="text-2xl md:text-3xl text-text-verba">{title}</p>
          <p className="text-sm md:text-base text-text-alt-verba font-light">
            {subtitle}
          </p>
        </div>
        <div className="flex md:hidden flex-col items-center gap-3 justify-between">
          <div className="dropdown dropdown-hover">
            <VerbaButton Icon={TiThMenu} title="Menu" />
            <ul
              tabIndex={0}
              className="dropdown-content dropdown-left z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
            >
              <li key={"Menu Button1"}>
                <a
                  className={currentPage === "CHAT" ? "font-bold" : ""}
                  onClick={() => {
                    setCurrentPage("CHAT");
                    closeOnClick();
                  }}
                >
                  Chat
                </a>
              </li>
              <li key={"Menu Button2"}>
                <a
                  className={currentPage === "DOCUMENTS" ? "font-bold" : ""}
                  onClick={() => {
                    setCurrentPage("DOCUMENTS");
                    closeOnClick();
                  }}
                >
                  Documents
                </a>
              </li>
              {production != "Demo" && (
                <li key={"Menu Button4"}>
                  <a
                    className={currentPage === "ADD" ? "font-bold" : ""}
                    onClick={() => {
                      setCurrentPage("ADD");
                      closeOnClick();
                    }}
                  >
                    Import Data
                  </a>
                </li>
              )}
              {production != "Demo" && (
                <li key={"Menu Button5"}>
                  <a
                    className={currentPage === "SETTINGS" ? "font-bold" : ""}
                    onClick={() => {
                      setCurrentPage("SETTINGS");
                      closeOnClick();
                    }}
                  >
                    Settings
                  </a>
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>

      <div className="flex flex-row justify-center items-center">
        {/* Pages */}
        <div className="hidden md:flex flex-row items-center gap-3 justify-between">
          <NavbarButton
            hide={false}
            Icon={IoChatbubbleSharp}
            title="Chat"
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            setPage="CHAT"
          />
          {production != "Demo" && (
            <NavbarButton
              hide={false}
              Icon={IoMdAddCircle}
              title="Import Data"
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
              setPage="ADD"
            />
          )}
          <NavbarButton
            hide={false}
            Icon={IoDocumentSharp}
            title="Documents"
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            setPage="DOCUMENTS"
          />
          {production != "Demo" && (
            <NavbarButton
              hide={false}
              Icon={IoSettingsSharp}
              title="Settings"
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
              setPage="SETTINGS"
            />
          )}
          <div
            className={`sm:h-[3vh] lg:h-[5vh] mx-1 hidden md:block bg-text-alt-verba w-px`}
          ></div>
          <VerbaButton
            title={gitHubStars}
            Icon={FaGithub}
            onClick={handleGitHubClick}
            className="hidden md:block"
            text_size="text-xs"
            icon_size={18}
            disabled={false}
            selected={false}
          />
        </div>
      </div>
    </div>
  );
};

export default Navbar;
