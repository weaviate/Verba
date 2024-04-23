'use client'

import React, { useState, useEffect } from 'react';
import ChatInterfaceComponent from './ChatInterface';
import { SettingsConfiguration } from "../Settings/types"
import { DocumentChunk } from '../Document/types';

import ChunksComponent from '../Document/ChunksComponent';
import DocumentComponent from '../Document/DocumentComponent';

interface ChatComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ APIHost, settingConfig }) => {

    const [chunks, setChunks] = useState<DocumentChunk[]>([])
    const [chunkTime, setChunkTime] = useState(0);
    const [selectedChunk, setSelectedChunk] = useState<DocumentChunk | null>(null)

    return (
        <div className="flex sm:flex-col md:flex-row justify-between items-start gap-3 ">

            {/* Chat Interface */}
            <div className='sm:w-full md:w-1/2 lg:w-2/6'>
                <ChatInterfaceComponent settingConfig={settingConfig} APIHost={APIHost} setChunks={setChunks} setChunkTime={setChunkTime} />
            </div>

            <div className='flex lg:flex-row sm:flex-col justify-between items-start sm:w-full md:w-1/2 lg:w-4/6 gap-3'>
                {/* Chunk Selection */}
                <div className='sm:w-full lg:w-1/4'>
                    <ChunksComponent chunks={chunks} selectedChunk={selectedChunk} setSelectedChunk={setSelectedChunk} chunkTime={chunkTime} />
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
