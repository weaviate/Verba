"use client";

import React, { useState, useEffect } from "react";
import { SettingsConfiguration } from "../Settings/types";
import {
  DocumentChunk,
  DocumentPreview,
  VerbaDocument,
  ContentPayload,
} from "./types";
import ReactMarkdown from "react-markdown";
import PulseLoader from "react-spinners/PulseLoader";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";

interface ContentViewProps {
  document: VerbaDocument | null;
  settingConfig: SettingsConfiguration;
  APIHost: string | null;
  selectedDocument: string;
}

const ContentView: React.FC<ContentViewProps> = ({
  document,
  selectedDocument,
  APIHost,
  settingConfig,
}) => {
  if (!document) {
    return <div></div>;
  }

  const [isFetching, setIsFetching] = useState(true);
  const [page, setPage] = useState(1);
  const [maxPage, setMaxPage] = useState(1);
  const [content, setContent] = useState("");

  const nextPage = () => {
    if (page == maxPage) {
      setPage(1);
    } else {
      setPage((prev) => prev + 1);
    }
  };

  const previousPage = () => {
    if (page == 1) {
      setPage(maxPage);
    } else {
      setPage((prev) => prev - 1);
    }
  };

  useEffect(() => {
    if (document) {
      fetchContent();
      setPage(1);
      setMaxPage(1);
    } else {
      setContent("");
      setPage(1);
      setMaxPage(1);
    }
  }, [document]);

  useEffect(() => {
    if (document) {
      fetchContent();
    } else {
      setContent("");
      setPage(1);
      setMaxPage(1);
    }
  }, [page]);

  const fetchContent = async () => {
    try {
      setIsFetching(true);

      const response = await fetch(APIHost + "/api/get_content", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          uuid: selectedDocument,
          page: page,
        }),
      });

      const data: ContentPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          setContent(data.error);
          setPage(1);
          setMaxPage(1);
          setIsFetching(false);
        } else {
          setContent(data.content);
          setMaxPage(data.maxPage);
          setIsFetching(false);
        }
      }
    } catch (error) {
      console.error("Failed to fetch content from document:", error);
      setIsFetching(false);
    }
  };

  const renderText = (txt: string) => {
    return (
      <ReactMarkdown
        className="max-w-[50vw] items-center justify-center flex-wrap md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <SyntaxHighlighter
                style={
                  settingConfig.Customization.settings.theme === "dark"
                    ? (oneDark as any)
                    : (oneLight as any)
                }
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {txt}
      </ReactMarkdown>
    );
  };

  return (
    <div className="flex flex-col gap-2 text-start items-start justify-start">
      {/* Header */}
      <div className="flex gap-4 w-full justify-between">
        <div className="flex gap-4 items-center ">
          {isFetching && (
            <div className="flex items-center justify-center text-text-alt-verba gap-2 h-full">
              <span className="loading loading-spinner loading-sm"></span>
            </div>
          )}
          <p className="text-lg font-bold">{document.title}</p>
        </div>
        <div className="gap-2 grid grid-cols-3">
          {Object.entries(document.labels).map(([key, label]) => (
            <div
              key={document.title + key + label}
              className="flex bg-bg-verba min-w-[8vw] p-2 text-sm text-text-verba justify-center text-center items-center rounded-xl"
            >
              <p>{label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="divider"></div>

      {/* Text */}
      <div className="flex gap-2 max-w-[70vw]">{renderText(content)}</div>

      <div className="join justify-center w-full items-center text-text-verba">
        <button
          onClick={previousPage}
          className="join-item btn btn-sqare border-none bg-button-verba hover:bg-secondary-verba"
        >
          «
        </button>

        <button className="join-item btn border-none bg-button-verba hover:bg-secondary-verba">
          Page {page}
        </button>
        <button
          onClick={nextPage}
          className="join-item btn btn-square border-none bg-button-verba hover:bg-secondary-verba"
        >
          »
        </button>
      </div>
    </div>
  );
};

export default ContentView;
