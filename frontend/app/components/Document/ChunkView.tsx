"use client";

import React, { useState, useEffect } from "react";
import { SettingsConfiguration } from "../Settings/types";
import {
  DocumentChunk,
  DocumentPreview,
  VerbaDocument,
  VerbaChunk,
  ChunksPayload,
} from "./types";
import ReactMarkdown from "react-markdown";
import PulseLoader from "react-spinners/PulseLoader";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";

interface ChunkViewProps {
  selectedDocument: string | null;
  settingConfig: SettingsConfiguration;
  APIHost: string | null;
}

const ChunkView: React.FC<ChunkViewProps> = ({
  selectedDocument,
  APIHost,
  settingConfig,
}) => {
  const [isFetching, setIsFetching] = useState(false);
  const [chunks, setChunks] = useState<VerbaChunk[]>([]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchChunks();
  }, [selectedDocument, page]);

  const pageSize = 10;

  const nextPage = () => {
    if (chunks.length == 0) {
      return;
    }

    if (chunks.length < pageSize) {
      setPage(1);
    } else {
      setPage((prev) => prev + 1);
    }
  };

  const previousPage = () => {
    if (chunks.length == 0) {
      return;
    }
    if (page == 1) {
      setPage(1);
    } else {
      setPage((prev) => prev - 1);
    }
  };

  const fetchChunks = async () => {
    try {
      setIsFetching(true);

      const response = await fetch(APIHost + "/api/get_chunks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          uuid: selectedDocument,
          page: page,
          pageSize: pageSize,
        }),
      });

      const data: ChunksPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setChunks([]);
        } else {
          setChunks(data.chunks);
          setIsFetching(false);
        }
      }
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
    }
  };

  if (chunks.length == 0) {
    return (
      <div>
        {isFetching && (
          <div className="flex items-center justify-center text-text-alt-verba gap-2 h-full">
            <span className="loading loading-spinner loading-sm"></span>
            <p>Loading Chunks</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 justify-center">
      <div className="join justify-center items-center text-text-verba">
        {page > 1 && (
          <button
            onClick={previousPage}
            className="join-item btn btn-sqare border-none bg-button-verba hover:bg-secondary-verba"
          >
            «
          </button>
        )}
        <button className="join-item btn border-none bg-button-verba hover:bg-secondary-verba">
          Page {page}
        </button>
        {chunks.length >= pageSize && (
          <button
            onClick={nextPage}
            className="join-item btn btn-square border-none bg-button-verba hover:bg-secondary-verba"
          >
            »
          </button>
        )}
      </div>

      {chunks.map((chunk, index) => (
        <div
          key={"Chunk" + index}
          className="bg-bg-alt-verba border-2 border-bg-bg-verba flex flex-col p-3 rounded-lg"
        >
          <div className="flex flex-col justify-between">
            <div className="divider font-bold text-text-alt-verba">
              Chunk {chunk.chunk_id}
            </div>
          </div>
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
            {chunk.content}
          </ReactMarkdown>
        </div>
      ))}

      <div className="join justify-center items-center text-text-verba">
        {page > 1 && (
          <button
            onClick={previousPage}
            className="join-item btn btn-sqare border-none bg-button-verba hover:bg-secondary-verba"
          >
            «
          </button>
        )}
        <button className="join-item btn border-none bg-button-verba hover:bg-secondary-verba">
          Page {page}
        </button>
        {chunks.length >= pageSize && (
          <button
            onClick={nextPage}
            className="join-item btn btn-square border-none bg-button-verba hover:bg-secondary-verba"
          >
            »
          </button>
        )}
      </div>
    </div>
  );
};

export default ChunkView;
