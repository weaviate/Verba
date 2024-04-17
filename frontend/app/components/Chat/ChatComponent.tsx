'use client'

import React, { useState, useEffect } from 'react';
import ChatInterfaceComponent from './ChatInterface';
import { SettingsConfiguration } from "../Settings/types"
import { DocumentChunk } from '../Document/types';

interface ChatComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ APIHost, settingConfig }) => {

    const [chunks, setChunks] = useState<DocumentChunk[]>([])

    return (
        <div className="flex sm:flex-col justify-between items-start gap-5">

            {/* Chat Interface */}
            <div className='sm:w-full md:w-1/2 lg:w-2/6'>
                <ChatInterfaceComponent settingConfig={settingConfig} APIHost={APIHost} setChunks={setChunks} />
            </div>

            {/* Chunk Selection */}
            <div className='w-1/3'>

            </div>

            {/* Document Viewer */}
            <div className='w-1/3'>

            </div>

        </div >
    );
};

export default ChatComponent;
