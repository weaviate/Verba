import { useEffect, useRef } from "react";
import React from 'react';
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { DocType, DOC_TYPE_COLORS } from "@/pages";

interface DocumentComponentProps {
    title: string;
    text: string;
    type?: DocType;
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

    useEffect(() => {
        if (extractRef.current) {
            const element = extractRef.current as HTMLElement;
            element.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        }
    }, [text, extract]);

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

    if (!title) return <div className=""></div>;

    const start = extract ? text.indexOf(extract) : -1;
    const end = extract ? start + extract.length : -1;

    return (
        <div className="border-2 border-gray-900 shadow-lg rounded-xl bg-gray-100 p-2 animate-pop-in overflow-y-auto max-h-[50vh] document-container">
            <div
                className={`bg-gray-300 text-black p-4 rounded-t-xl w-full sticky top-0 z-10 shadow-md`}
            >
                <span className="mr-4 bg-yellow-300 p-2 rounded-lg shadow-md ">{type}</span>
                <a href={docLink || "#"} target="_blank" rel="noopener noreferrer">
                    {title || "Placeholder Title"}
                </a>
            </div>
            <div className="p-4 my-markdown-styles text-sm font-mono">
                {start !== -1 && (
                    <RenderMarkdown text={text.slice(0, start)} />
                )}
                {extract && (
                    <div
                        ref={extractRef}
                        className={`${DOC_TYPE_COLORS[type]} rounded-lg p-3 shadow-lg extract text-sm`}
                    >
                        <RenderMarkdown text={text.slice(start, end)} />
                    </div>
                )}
                {start !== -1 ? (
                    <div className="pt-3">
                        <RenderMarkdown text={text.slice(end)} />
                    </div>
                ) : (
                    <RenderMarkdown text={text} />
                )}
            </div>
        </div>
    );
}
