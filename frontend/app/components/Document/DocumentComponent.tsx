'use client'
import React, { useState, useEffect, useRef } from 'react';
import { DocumentChunk, Document, DocumentPayload } from '../Document/types';
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { SettingsConfiguration } from '../Settings/types';
import { FormattedDocument } from '../Document/types';
import { splitDocument } from './util';
import { FaExternalLinkAlt } from "react-icons/fa";
import { MdOutlineSimCardDownload } from "react-icons/md";
import { HiMiniSparkles } from "react-icons/hi2";


interface DocumentComponentProps {
    settingConfig: SettingsConfiguration;
    APIhost: string | null;
    selectedChunk: DocumentChunk | null
}

const DocumentComponent: React.FC<DocumentComponentProps> = ({
    APIhost,
    selectedChunk,
    settingConfig
}) => {

    const [currentDocument, setCurrentDocument] = useState<Document | null>(null)
    const [formattedDocument, setFormattedDocument] = useState<FormattedDocument | null>(null)
    const [isFetching, setIsFetching] = useState(false);
    const [showWholeDocument, setWholeDocument] = useState(false)

    const chunkRef = useRef<null | HTMLDivElement>(null);

    useEffect(() => {
        if (selectedChunk != null && APIhost != null) {
            const fetchDocuments = async () => {
                try {
                    setIsFetching(true)

                    const response = await fetch(APIhost + "/api/get_document", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            document_id: selectedChunk.doc_uuid,
                        }),
                    });
                    const data: DocumentPayload = await response.json();

                    if (data) {
                        if (data.error !== "") {
                            setCurrentDocument(null)
                            console.error(data.error)
                            setFormattedDocument(null)
                            setIsFetching(false)
                            setWholeDocument(false)
                        } else {
                            setCurrentDocument(data.document)
                            setFormattedDocument(splitDocument(data.document.text, selectedChunk.text))
                            setIsFetching(false)
                            if (chunkRef.current) {
                                chunkRef.current.scrollIntoView({ behavior: "smooth" });
                            }
                            if (data.document.text.length > settingConfig.Chat.settings.max_document_size.value) {
                                setWholeDocument(false)
                            } else {
                                setWholeDocument(true)
                            }
                        }
                    }


                } catch (error) {
                    console.error("Failed to fetch document:", error);
                    setIsFetching(false)
                }
            }

            fetchDocuments();

        } else {
            setCurrentDocument(null)
        }
    }, [selectedChunk]);

    const handleSourceClick = () => {
        // Open a new tab with the specified URL
        window.open(currentDocument?.link, '_blank', 'noopener,noreferrer');
    };

    const handleDocumentShow = () => {
        setWholeDocument(prev => !prev)
    }

    if (currentDocument !== null) {

        return (
            <div className='flex flex-col gap-2' >
                <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 sm:h-[47vh] lg:h-[65vh] overflow-auto">
                    {/*Title*/}
                    <div className='flex justify-between'>
                        <div className='flex flex-col'>
                            <p className='sm:text-sm md:text-lg font-semibold'>{currentDocument.name}</p>
                            <p className='sm:text-xs md:text-sm text-text-alt-verba'>{currentDocument.type}</p>
                        </div>
                        <div className='flex gap-2'>
                            {formattedDocument && (
                                <div className='flex'>
                                    <button onClick={handleDocumentShow} className='btn bg-button-verba hover:button-hover-verba flex gap-2'>
                                        <MdOutlineSimCardDownload />
                                        <p className='sm:hidden md:flex text-xs'>
                                            {showWholeDocument ? ("Show Only Context") : ("Show Whole Document")}
                                        </p>
                                    </button>
                                </div>
                            )}
                            {currentDocument.link !== "" && (
                                <div className='flex'>
                                    <button onClick={handleSourceClick} className='btn bg-button-verba hover:button-hover-verba flex gap-2'>
                                        <FaExternalLinkAlt />
                                        <p className='sm:hidden md:flex text-xs'>
                                            Go To Source
                                        </p>
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    {/*Text*/}
                    {formattedDocument && (
                        <div className='flex flex-col gap-5'>
                            {showWholeDocument && (
                                <ReactMarkdown
                                    className="prose md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
                                    components={{
                                        code({ node, inline, className, children, ...props }) {
                                            const match = /language-(\w+)/.exec(className || '')
                                            return !inline && match ? (
                                                <SyntaxHighlighter
                                                    style={settingConfig.Customization.settings.theme === "dark" ? oneDark as any : oneLight as any}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    {...props}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            ) : (
                                                <code className={className} {...props}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                >
                                    {formattedDocument.beginning}
                                </ReactMarkdown>
                            )}
                            <div ref={chunkRef} className=' border-secondary-verba border-2 rounded-lg shadow-lg flex gap-2 flex-col p-3'>
                                <div className='flex w-1/3'>
                                    <div className={`p-2 flex gap-1 rounded-lg text-text-verba text-sm bg-secondary-verba }`}>
                                        <HiMiniSparkles />
                                        <p className={`text-xs text-text-verba}`}>
                                            Context Used
                                        </p>
                                    </div>
                                </div>
                                <ReactMarkdown
                                    className="prose md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
                                    components={{
                                        code({ node, inline, className, children, ...props }) {
                                            const match = /language-(\w+)/.exec(className || '')
                                            return !inline && match ? (
                                                <SyntaxHighlighter
                                                    style={settingConfig.Customization.settings.theme === "dark" ? oneDark as any : oneLight as any}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    {...props}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            ) : (
                                                <code className={className} {...props}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                >
                                    {formattedDocument.substring}
                                </ReactMarkdown>
                            </div>
                            {showWholeDocument && (
                                <ReactMarkdown
                                    className="prose md:prose-base sm:prose-sm p-3 prose-pre:bg-bg-alt-verba"
                                    components={{
                                        code({ node, inline, className, children, ...props }) {
                                            const match = /language-(\w+)/.exec(className || '')
                                            return !inline && match ? (
                                                <SyntaxHighlighter
                                                    style={settingConfig.Customization.settings.theme === "dark" ? oneDark as any : oneLight as any}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    {...props}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            ) : (
                                                <code className={className} {...props}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                >
                                    {formattedDocument.ending}
                                </ReactMarkdown>
                            )}
                        </div>
                    )}



                </div >
            </div >
        );
    } else {

        return (
            <div className='flex flex-col gap-2' >
                {/*Chat Messages*/}
                <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 md:h-[47vh] lg:h-[65vh] overflow-auto">


                </div >
            </div >
        );
    }

};

export default DocumentComponent;
