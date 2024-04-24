'use client'

import React, { useState, useEffect } from 'react';
import ChatInterfaceComponent from './ChatInterface';
import { SettingsConfiguration } from "../Settings/types"
import { DocumentChunk } from '../Document/types';

import ChunksComponent from '../Document/ChunksComponent';
import DocumentComponent from '../Document/DocumentComponent';

import { RAGConfig } from '../RAG/types';

interface ChatComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
    setCurrentPage: (p: any) => void;
    RAGConfig: RAGConfig | null;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ APIHost, settingConfig, setCurrentPage, RAGConfig }) => {

    const [chunks, setChunks] = useState<DocumentChunk[]>([])
    const [chunkTime, setChunkTime] = useState(0);
    const [selectedChunk, setSelectedChunk] = useState<DocumentChunk | null>(null)

    return (
        <div className="flex sm:flex-col md:flex-row justify-between items-start gap-3 ">

            {/* Chat Interface */}
            <div className='sm:w-full md:w-1/2 lg:w-2/6'>
                <ChatInterfaceComponent RAGConfig={RAGConfig} settingConfig={settingConfig} APIHost={APIHost} setChunks={setChunks} setChunkTime={setChunkTime} setCurrentPage={setCurrentPage} />
            </div>

            <div className='flex lg:flex-row sm:flex-col justify-between items-start sm:w-full md:w-1/2 lg:w-4/6 gap-3'>
                {/* Chunk Selection */}
                <div className='sm:w-full lg:w-1/4'>
                    <ChunksComponent chunks={chunks} RAGConfig={RAGConfig} selectedChunk={selectedChunk} setSelectedChunk={setSelectedChunk} chunkTime={chunkTime} setCurrentPage={setCurrentPage} />
                </div>

                {/* Document Viewer */}
                <div className='sm:w-full lg:w-3/4'>
                    <DocumentComponent setSelectedChunk={setSelectedChunk} selectedChunk={selectedChunk} APIhost={APIHost} settingConfig={settingConfig} deletable={false} selectedDocument={null} />
                </div>
            </div>

        </div >
    );
};

export default ChatComponent;
