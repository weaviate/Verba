"use client";

import React from "react";
import { ChunkScore, Message } from "./types";
import ReactMarkdown from "react-markdown";
import { FaDatabase } from "react-icons/fa";
import { BiError } from "react-icons/bi";
import { IoNewspaper } from "react-icons/io5";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";
import { SettingsConfiguration } from "../Settings/types";

interface ChatMessageProps {
  message: Message;
  message_index: number;
  settingConfig: SettingsConfiguration;
  selectedDocument: string | null;
  setSelectedDocument: (s: string | null) => void;
  setSelectedDocumentScore: (s: string | null) => void;
  setSelectedChunkScore: (s: ChunkScore[]) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  settingConfig,
  selectedDocument,
  setSelectedDocument,
  message_index,
  setSelectedDocumentScore,
  setSelectedChunkScore,
}) => {
  const colorTable = {
    user: "bg-bg-verba",
    system: "bg-bg-verba",
    error: "bg-warning-verba",
    retrieval: "bg-bg-verba",
  };

  if (typeof message.content === "string") {
    return (
      <div
        className={`flex items-end gap-2 ${message.type === "user" ? "justify-end" : "justify-start"}`}
      >
        <div
          className={`flex flex-col items-start p-5 rounded-3xl animate-press-in sm:text-sm md:text-base ${colorTable[message.type]}`}
        >
          {message.cached && (
            <FaDatabase size={12} className="text-text-verba" />
          )}
          {message.type === "system" && (
            <ReactMarkdown
              className="prose md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
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
              {message.content}
            </ReactMarkdown>
          )}
          {message.type === "user" && (
            <div className="whitespace-pre-wrap">{message.content}</div>
          )}
          {message.type === "error" && (
            <div className="whitespace-pre-wrap flex items-center gap-2 text-sm text-text-verba">
              <BiError size={15} />
              <p>{message.content}</p>
            </div>
          )}
        </div>
        <div className="flex flex-col items-center justify-center">
          {message.type === "system" && (
            <button
              className={`btn border-none shadow-none flex gap- bg-bg-alt-verba hover:bg-secondary-verba hover:text-text-verba text-text-alt-verba`}
            >
              <p className="text-xs">Copy</p>
            </button>
          )}
        </div>
      </div>
    );
  } else {
    return (
      <div className="grid grid-cols-3 gap-3 w-full">
        {message.content.map((document, index) => (
          <button
            onClick={() => {
              setSelectedDocument(document.uuid);
              setSelectedDocumentScore(
                document.uuid + document.score + document.chunks.length
              );
              setSelectedChunkScore(document.chunks);
            }}
            key={"Retrieval" + document.title + index}
            className={`flex ${selectedDocument && selectedDocument === document.uuid + document.score + document.chunks.length ? "bg-secondary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-secondary-verba"} rounded-3xl p-3 items-center justify-center flex gap-2 transition-colors duration-300 ease-in-out border-none`}
          >
            <p className="text-xs flex">{document.title}</p>
            <div className="flex gap-1 items-center text-text-verba">
              <IoNewspaper size={12} />
              <p className="text-sm">{document.chunks.length}</p>
            </div>
          </button>
        ))}
      </div>
    );
  }
};

export default ChatMessage;
