"use client";

import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";
import { FaArrowAltCircleLeft, FaArrowAltCircleRight } from "react-icons/fa";
import { HiSparkles } from "react-icons/hi2";
import { IoNewspaper } from "react-icons/io5";
import { SettingsConfiguration } from "../Settings/types";
import {
  VerbaDocument,
  ContentPayload,
  Credentials,
  ContentSnippet,
  ChunkScore,
} from "@/app/api_types";
import { fetchContent } from "@/app/api";

interface ContentViewProps {
  document: VerbaDocument | null;
  settingConfig: SettingsConfiguration;
  selectedDocument: string;
  credentials: Credentials;
  chunkScores?: ChunkScore[];
}

const ContentView: React.FC<ContentViewProps> = ({
  document,
  selectedDocument,
  settingConfig,
  credentials,
  chunkScores,
}) => {
  if (!document) {
    return <div></div>;
  }

  const [isFetching, setIsFetching] = useState(true);
  const [page, setPage] = useState(1);
  const [maxPage, setMaxPage] = useState(1);
  const [content, setContent] = useState<ContentSnippet[]>([]);

  const contentRef = useRef<HTMLDivElement>(null);

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
      handleFetchContent();
      setPage(1);
      setMaxPage(1);
    } else {
      setContent([]);
      setPage(1);
      setMaxPage(1);
    }
  }, [document, chunkScores]);

  useEffect(() => {
    if (document) {
      handleFetchContent();
    } else {
      setContent([]);
      setPage(1);
      setMaxPage(1);
    }
  }, [page]);

  useEffect(() => {
    if (chunkScores && chunkScores.length > 0) {
      contentRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [content, chunkScores]);

  const handleFetchContent = async () => {
    try {
      setIsFetching(true);

      const data: ContentPayload | null = await fetchContent(
        selectedDocument,
        page,
        chunkScores ? chunkScores : [],
        credentials
      );

      if (data) {
        if (data.error !== "") {
          setContent([
            { content: data.error, chunk_id: 0, score: 0, type: "text" },
          ]);
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

  const renderText = (contentSnippet: ContentSnippet) => {
    if (contentSnippet.type === "text") {
      return (
        <div className="flex p-2" ref={!chunkScores ? contentRef : null}>
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
            {contentSnippet.content}
          </ReactMarkdown>
        </div>
      );
    } else {
      return (
        <div
          className="flex p-2 border-2 flex-col gap-2 border-secondary-verba shadow-lg rounded-3xl"
          ref={contentRef}
        >
          <div className="flex justify-between">
            <div className="flex gap-2">
              <div className="flex gap-2 items-center p-3 bg-secondary-verba rounded-full w-fit">
                <HiSparkles size={12} />
                <p className="text-xs flex text-text-verba">Context Used</p>
              </div>
              <div className="flex gap-2 items-center p-3 bg-secondary-verba rounded-full w-fit">
                <IoNewspaper size={12} />
                <p className="text-xs flex text-text-verba">
                  Chunk {contentSnippet.chunk_id + 1}
                </p>
              </div>
              {contentSnippet.score > 0 && (
                <div className="flex gap-2 items-center p-3 bg-primary-verba rounded-full w-fit">
                  <HiSparkles size={12} />
                  <p className="text-xs flex text-text-verba">High Relevancy</p>
                </div>
              )}
            </div>
          </div>
          <ReactMarkdown
            className="w-full items-center justify-center flex-wrap md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
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
            {contentSnippet.content}
          </ReactMarkdown>
        </div>
      );
    }
  };

  return (
    <div className="flex flex-col h-full">
      {document && (
        <div className="bg-bg-alt-verba flex flex-col rounded-lg overflow-hidden h-full">
          {/* Header */}
          <div className="p-3 bg-bg-alt-verba">
            <div className="flex gap-4 w-full justify-between">
              <div className="flex gap-4 items-center">
                {isFetching && (
                  <div className="flex items-center justify-center text-text-alt-verba gap-2">
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
          </div>

          {/* Content div */}
          <div className="flex-grow overflow-hidden p-3">
            <div className="overflow-y-auto h-full">
              {content &&
                content.map((contentSnippet, index) =>
                  renderText(contentSnippet)
                )}
            </div>
          </div>

          {/* Navigation div */}

          <div className="flex justify-center gap-2 p-3 bg-bg-alt-verba">
            <button
              onClick={previousPage}
              className="flex gap-2 items-center p-3 bg-button-verba hover:bg-button-hover-verba rounded-full w-fit"
            >
              <FaArrowAltCircleLeft size={12} />
              <p className="text-xs flex text-text-verba">
                Previous {chunkScores ? "Chunk" : "Page"}
              </p>
            </button>
            <div className="flex items-center">
              <p className="text-xs text-text-verba">
                {chunkScores ? "Chunk " : "Page "} {page}
              </p>
            </div>
            <button
              onClick={nextPage}
              className="flex gap-2 items-center p-3 bg-button-verba hover:bg-button-hover-verba rounded-full w-fit"
            >
              <FaArrowAltCircleRight size={12} />
              <p className="text-xs flex text-text-verba">
                Next {chunkScores ? "Chunk" : "Page"}
              </p>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentView;
