import { useEffect, useRef } from "react";
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

const RenderMarkdown = ({ text, type }: { text: string; type: DocType }) => {
    return (
        <ReactMarkdown
            components={{
                code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                        <SyntaxHighlighter
                            {...props}
                            style={oneLight}
                            language={match[1]}
                            PreTag="div"
                        >
                            {String(children).replace(/\n$/, "")}
                        </SyntaxHighlighter>
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
};

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

    if (!title) return <div className=""></div>;

    const start = extract ? text.indexOf(extract) : -1;
    const end = extract ? start + extract.length : -1;

    return (
        <div className="border-2 border-gray-900 shadow-lg rounded-xl bg-gray-100 p-2 animate-pop-in overflow-y-auto max-h-[548px] document-container">
            <div
                className={`${DOC_TYPE_COLORS[type]} text-black p-4 rounded-t-xl w-full sticky top-0 z-10 shadow-md`}
            >
                <a href={docLink || "#"} target="_blank" rel="noopener noreferrer">
                    {title || "Placeholder Title"}
                </a>
            </div>
            <div className="p-4 my-markdown-styles text-sm font-mono">
                {start !== -1 && (
                    <RenderMarkdown text={text.slice(0, start)} type={type} />
                )}
                {extract && (
                    <div
                        ref={extractRef}
                        className={`${DOC_TYPE_COLORS[type]} rounded-lg p-3 shadow-lg text-sm`}
                    >
                        <RenderMarkdown text={text.slice(start, end)} type={type} />
                    </div>
                )}
                {start !== -1 ? (
                    <div className="pt-3">
                        <RenderMarkdown text={text.slice(end)} type={type} />
                    </div>
                ) : (
                    <RenderMarkdown text={text} type={type} />
                )}
            </div>
        </div>
    );
}
