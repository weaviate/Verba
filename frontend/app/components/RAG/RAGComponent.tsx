'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration } from "../Settings/types"
import RAGConfigComponent from './RAGConfigComponent';
import { RAGConfig } from './types';
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";

interface RAGComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
    RAGConfig: RAGConfig | null;
    setRAGConfig: (r_: RAGConfig) => void;
    showComponents: string[]
    buttonTitle: string;
}

const RAGComponent: React.FC<RAGComponentProps> = ({ APIHost, settingConfig, RAGConfig, setRAGConfig, showComponents, buttonTitle }) => {

    const [currentRAGSettings, setCurrentRAGSettings] = useState<RAGConfig>(JSON.parse(JSON.stringify(RAGConfig)))

    return (
        <div className="flex sm:flex-col md:flex-row justify-between gap-3 ">
            {currentRAGSettings && Object.entries(currentRAGSettings).map(([key, value]) => (
                showComponents.includes(key) && (
                    <div className='w-full md:w-1/4'>
                        <RAGConfigComponent key={key} settingConfig={settingConfig} APIHost={APIHost} RAGConfig={currentRAGSettings} RAGConfigTitle={key} RAGComponents={value} setRAGConfig={setCurrentRAGSettings} />
                    </div>
                )
            ))}
            <div className='flex flex-col gap-2 w-full md:w-1/4 items-end'>
                <div className='flex flex-row gap-2 w-full'>
                    <button className='btn w-1/2 btn-lg text-base flex gap-2 bg-secondary-verba hover:bg-button-hover-verba text-text-verba'>
                        <FaFileImport />
                        {buttonTitle}
                    </button>
                    <button className='btn w-1/2 btn-lg text-base text-text-verba bg-warning-verba hover:bg-button-hover-verba'>
                        <MdCancel />
                        Clear
                    </button>
                </div>
                {buttonTitle === "Import" && (
                    <div className='flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 h-[58.5vh] overflow-auto w-full'>
                        <div className='flex flex-col'>
                            <p className='text-lg'>Console</p>
                        </div>
                    </div>
                )}
            </div>

        </div>


    );
};

export default RAGComponent;
