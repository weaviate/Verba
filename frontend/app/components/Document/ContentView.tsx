"use client";

import React, { useState } from "react";
import { SettingsConfiguration } from "../Settings/types";
import { DocumentChunk, DocumentPreview, VerbaDocument } from "./types";

import DocumentComponent from "./DocumentComponent";
import DocumentSearch from "./DocumentSearch";
import ReactMarkdown from "react-markdown";
import PulseLoader from "react-spinners/PulseLoader";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";

import { RAGConfig } from "../RAG/types";
import DocumentExplorer from "./DocumentExplorer";
import { render } from "react-dom";

interface ContentViewProps {
  document: VerbaDocument | null;
  settingConfig: SettingsConfiguration;
}

const ContentView: React.FC<ContentViewProps> = ({
  document,
  settingConfig,
}) => {
  if (!document) {
    return <div></div>;
  }

  const renderText = (txt: string, extension: string) => {
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
        <p className="text-lg font-bold">{document.title}</p>
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
      <div className="flex gap-2 max-w-[70vw]">
        {renderText(document.content, document.extension)}
      </div>
    </div>
  );
};

export default ContentView;
