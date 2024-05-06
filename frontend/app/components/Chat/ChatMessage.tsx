"use client";

import React from "react";
import { Message } from "./types";
import ReactMarkdown from "react-markdown";
import { FaDatabase } from "react-icons/fa";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";
import { SettingsConfiguration } from "../Settings/types";

interface ChatMessageProps {
  message: Message;
  handleCopyToBillboard: (m: string) => void;
  settingConfig: SettingsConfiguration;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  handleCopyToBillboard,
  settingConfig,
}) => {
  return (
    <div
      className={`flex items-end gap-2 ${message.type === "user" ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`flex flex-col items-start p-4 rounded-xl animate-press-in shadow-md sm:text-sm md:text-base ${message.type === "user" ? "bg-primary-verba" : "bg-bg-verba"}`}
      >
        {message.cached && <FaDatabase size={12} className="text-text-verba" />}
        {message.type === "system" ? (
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
        ) : (
          <div className="whitespace-pre-wrap">{message.content}</div> // Use whitespace-pre-wrap for user messages
        )}
      </div>
      <div className="flex flex-col items-center justify-center">
        {message.type === "system" && (
          <button
            onClick={() => handleCopyToBillboard(message.content)}
            className={`btn border-none shadow-none flex gap-1 bg-bg-alt-verba hover:bg-secondary-verba hover:text-text-verba text-text-alt-verba`}
          >
            <p className="text-xs">Copy</p>
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
