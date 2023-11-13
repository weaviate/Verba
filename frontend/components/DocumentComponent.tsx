import { useEffect, useRef, useState } from "react";
import React from 'react';
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { GrDocumentDownload } from 'react-icons/gr';

interface DocumentComponentProps {
    title: string;
    text: string;
    type?: string;
    extract?: string;
    docLink?: string;
}

const MemoizedSyntaxHighlighter = React.memo(SyntaxHighlighter);

export function DocumentComponent({
    title,
    text,
    type = "Documentation",
    extract,
    docLink,
}: DocumentComponentProps) {
    const extractRef = useRef(null);
    const containerRef = useRef<HTMLDivElement | null>(null)  // Add a ref for the container
    const [displayedChunks, setDisplayedChunks] = useState(1);
    const [hasScrolledToExtract, setHasScrolledToExtract] = useState(false);
    const CHUNK_SIZE = 1500; // Number of characters per chunk. Adjust as needed.


    useEffect(() => {
        setDisplayedChunks(1);
    }, [text]);

    const start = extract ? text.indexOf(extract) : -1;
    const extractChunk = start !== -1 ? Math.ceil(start / CHUNK_SIZE) : 0;

    useEffect(() => {
        if (extract && extractChunk > displayedChunks) {
            setDisplayedChunks(extractChunk + 1); // Load up to the chunk containing the extract
        }
    }, [extract, extractChunk]);

    useEffect(() => {
        if (extractRef.current && !hasScrolledToExtract) {
            const element = extractRef.current as HTMLElement;
            element.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
            setHasScrolledToExtract(true); // Set to true after scrolling
        }
    }, [text, extract]);

    useEffect(() => {
        setHasScrolledToExtract(false); // Reset the flag when text or extract changes
    }, [text, extract])

    const RenderMarkdown = React.memo(function RenderMarkdown({ text }: { text: string; }) {
        return (
            <ReactMarkdown
                components={{
                    code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline && match ? (
                            <MemoizedSyntaxHighlighter
                                {...props}
                                style={oneLight}
                                language={match[1]}
                                PreTag="div"
                            >
                                {String(children).replace(/\n$/, "")}
                            </MemoizedSyntaxHighlighter>
                        ) : (
                            <code {...props} className={className}>
                                {children}
                            </code>
                        );
                    },
                }}
            >
                {text}
            </ReactMarkdown>
        );
    });

    const handleLoadMore = () => {
        setDisplayedChunks(prev => prev + 1);
    }

    if (!title) return <div className=""></div>;

    const end = extract ? start + extract.length : -1;

    return (
        <div ref={containerRef} className="border-2 border-gray-900 shadow-lg rounded-xl bg-gray-100 p-2 animate-pop-in overflow-y-auto max-h-[50vh]">
            <div className={`bg-gray-300 text-black p-4 rounded-t-xl w-full sticky top-0 z-10 shadow-md`}>
                <span className="mr-4 bg-yellow-300 p-2 rounded-lg shadow-md ">{type}</span>
                <a href={docLink || "#"} target="_blank" rel="noopener noreferrer">
                    {title || "Placeholder Title"}
                </a>
            </div>
            <div className="p-4 my-markdown-styles text-sm font-mono">
                <RenderMarkdown text={extract ? text.slice(0, start) : text.slice(0, displayedChunks * CHUNK_SIZE)} />

                {extract && (
                    <div
                        ref={extractRef}
                        className={`bg-green-300 rounded-lg p-3 shadow-lg extract text-sm`}
                    >
                        <RenderMarkdown text={text.slice(start, end)} />
                    </div>
                )}
                <RenderMarkdown text={text.slice(end, displayedChunks * CHUNK_SIZE)} />

                {/* Load More Button */}
                {displayedChunks * CHUNK_SIZE < text.length && (
                    <div className="flex items-center justify-center">
                        <button className="flex mt-4 bg-yellow-400 hover:bg-yellow-300 text-xs text-black p-3 rounded-lg shadow-md" onClick={handleLoadMore}>
                            <GrDocumentDownload size={15} />
                            <span className="ml-2">Load More</span>
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
