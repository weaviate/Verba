import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface DocumentComponentProps {
    title: string;
    text: string;
    extract?: string;
    docLink?: string; // Add this line
}

export function DocumentComponent({ title, text, extract, docLink }: DocumentComponentProps) {
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
                </div>
                <p className="...">
                </p>
            </div>
        );
    }

    // Find the start and end of the extract within the text
    const start = text.indexOf(extract);
    if (start === -1) {
        console.error("Extract not found within text.");
        console.log(extract);

        // Render the full text if the extract doesn't match
        return (
            <div className="border-2 border-gray-900 shadow-lg rounded-xl bg-gray-200 p-2 animate-pop-in overflow-y-auto max-h-[548px] document-container">
                <div className="bg-green-300 text-black p-4 rounded-t-xl w-full sticky top-0 z-10 shadow-md">
                    <a href={docLink || '#'} target="_blank" rel="noopener noreferrer">
                        {title || "Placeholder Title"}
                    </a>
                </div>
                <div className="p-4">
                    <ReactMarkdown className="pb-3 text-sm my-markdown-styles">
                        {text}
                    </ReactMarkdown>
                </div>
            </div>
        );
    }
    const end = start + extract.length;

    return (
        <div className="border-2 border-gray-900 shadow-lg rounded-xl bg-gray-200 p-2 animate-pop-in overflow-y-auto max-h-[548px] document-container">
            <div className="bg-green-300 text-black p-4 rounded-t-xl w-full sticky top-0 z-10 shadow-md">
                <a href={docLink || '#'} target="_blank" rel="noopener noreferrer">
                    {title || "Placeholder Title"}
                </a>
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

