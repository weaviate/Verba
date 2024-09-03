"use client";

import React, { useState, useEffect } from "react";
import { VerbaChunk, ChunksPayload, Theme } from "@/app/types";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/cjs/styles/prism";
import { IoNewspaper } from "react-icons/io5";
import { FaArrowAltCircleRight, FaArrowAltCircleLeft } from "react-icons/fa";

import { fetch_chunks } from "@/app/api";
import { Credentials } from "@/app/types";

import VerbaButton from "../Navigation/VerbaButton";

interface ChunkViewProps {
  selectedDocument: string | null;
  selectedTheme: Theme;
  credentials: Credentials;
}

const ChunkView: React.FC<ChunkViewProps> = ({
  selectedDocument,
  credentials,
  selectedTheme,
}) => {
  const [isFetching, setIsFetching] = useState(false);
  const [chunks, setChunks] = useState<VerbaChunk[]>([]);
  const [page, setPage] = useState(1);
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [isPreviousDisabled, setIsPreviousDisabled] = useState(true);

  useEffect(() => {
    fetchChunks(page);
    setIsPreviousDisabled(page === 1 && currentChunkIndex === 0);
  }, [page, currentChunkIndex]);

  useEffect(() => {
    fetchChunks(1);
    setCurrentChunkIndex(0);
    setIsPreviousDisabled(page === 1 && currentChunkIndex === 0);
  }, [selectedDocument]);

  const pageSize = 10;

  const nextChunk = async () => {
    if (currentChunkIndex === chunks.length - 1) {
      const hasMoreChunks = await fetchChunks(page + 1);
      if (hasMoreChunks) {
        setPage((prev) => prev + 1);
        setCurrentChunkIndex(0);
      } else {
        await fetchChunks(1);
        setPage(1);
        setCurrentChunkIndex(0);
      }
    } else {
      setCurrentChunkIndex((prev) => prev + 1);
    }
  };

  const previousChunk = async () => {
    if (currentChunkIndex === 0) {
      if (page > 1) {
        const prevPage = page - 1;
        const hasChunks = await fetchChunks(prevPage);
        if (hasChunks) {
          setPage(prevPage);
          setCurrentChunkIndex(pageSize - 1);
        }
      } else {
        let lastPage = page;
        let hasMoreChunks = true;
        while (hasMoreChunks) {
          hasMoreChunks = await fetchChunks(lastPage + 1);
          if (hasMoreChunks) lastPage++;
        }
        await fetchChunks(lastPage);
        setPage(lastPage);
        setCurrentChunkIndex(chunks.length - 1);
      }
    } else {
      setCurrentChunkIndex((prev) => prev - 1);
    }
  };

  const fetchChunks = async (pageNumber: number) => {
    try {
      setIsFetching(true);

      const data: ChunksPayload | null = await fetch_chunks(
        selectedDocument,
        pageNumber,
        pageSize,
        credentials
      );

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setChunks([]);
          return false; // No more chunks available
        } else {
          setChunks(data.chunks);
          setIsFetching(false);
          return data.chunks.length > 0; // Return true if chunks were fetched
        }
      }
      return false; // No more chunks available
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
      return false; // No more chunks available
    }
  };

  if (chunks.length == 0) {
    return (
      <div>
        {isFetching && (
          <div className="flex items-center justify-center text-text-verba gap-2 h-full">
            <span className="loading loading-spinner loading-sm"></span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {chunks.length > 0 && (
        <div className="bg-bg-alt-verba flex flex-col rounded-lg overflow-hidden h-full">
          {/* Content div */}
          <div className="flex-grow overflow-hidden p-3">
            <div className="flex justify-between mb-2">
              <div className="flex gap-2">
                <div className="flex gap-2 items-center p-3 bg-secondary-verba rounded-full w-fit">
                  <IoNewspaper size={12} />
                  <p className="text-xs flex text-text-verba">
                    Chunk {chunks[currentChunkIndex].chunk_id}
                  </p>
                </div>
              </div>
            </div>
            <div className="overflow-y-auto h-[calc(100%-3rem)]">
              <ReactMarkdown
                className="max-w-[50vw] items-center justify-center flex-wrap md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={
                          selectedTheme.theme === "dark"
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
                {chunks[currentChunkIndex].content}
              </ReactMarkdown>
            </div>
          </div>

          {/* Navigation div */}
          {chunks.length > 1 && (
            <div className="flex justify-center items-center gap-2 p-3 bg-bg-alt-verba">
              <VerbaButton
                title={"Previous Chunk"}
                onClick={previousChunk}
                className="btn-sm min-w-min max-w-[200px]"
                text_class_name="text-xs"
                disabled={isPreviousDisabled}
                Icon={FaArrowAltCircleLeft}
              />
              <VerbaButton
                title={"Next Chunk"}
                onClick={nextChunk}
                className="btn-sm min-w-min max-w-[200px]"
                text_class_name="text-xs"
                Icon={FaArrowAltCircleRight}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChunkView;
