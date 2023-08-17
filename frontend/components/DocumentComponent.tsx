import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface DocumentComponentProps {
    title: string;
    text: string;
    extract?: string;
}

export function DocumentComponent({ title, text, extract }: DocumentComponentProps) {
    const extractRef = useRef(null);

    useEffect(() => {
        if (extractRef.current) {
            const element = extractRef.current as HTMLElement;
            element.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }
    }, [text, extract]);

    // If extract is not provided, just render the text as-is
    if (!extract) {
        return (
            <div className="... document-container">
                <div className="...">
                    {title || "Placeholder Title"}
                </div>
                <p className="...">
                    {text}
                </p>
            </div>
        );
    }

    // Find the start and end of the extract within the text
    const start = text.indexOf(extract);
    if (start === -1) {
        console.error("Extract not found within text.");
        console.log(extract)
        return null; // or some default rendering
    }
    const end = start + extract.length;

    return (
        <div className="w-1/2 border-2 border-gray-900 shadow-lg rounded-xl bg-gray-200 p-2 animate-pop-in overflow-y-auto max-h-[469px] document-container">
            <div className="bg-green-300 text-black p-4 rounded-t-xl">
                {title || "Placeholder Title"}
            </div>
            <div className="p-4">
                <ReactMarkdown className="pb-3 text-sm my-markdown-styles">
                    {text.slice(0, start)}
                </ReactMarkdown>
                <div ref={extractRef} className="bg-green-200 rounded-lg p-3 shadow-lg text-sm">
                    <ReactMarkdown>
                        {text.slice(start, end)}
                    </ReactMarkdown>
                </div>
                <ReactMarkdown className="pt-3 text-sm">
                    {text.slice(end)}
                </ReactMarkdown>
            </div>
        </div>
    );
}

