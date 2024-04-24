'use client'

import React, { useState } from 'react';
import { SettingsConfiguration } from "../Settings/types"
import RAGConfigComponent from './RAGConfigComponent';
import { RAGConfig, ConsoleMessage, ImportResponse } from './types';
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";

import PulseLoader from "react-spinners/PulseLoader";
import { Settings } from '../Settings/types';

import { processFiles } from './util';

interface RAGComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
    RAGConfig: RAGConfig | null;
    setRAGConfig: (r_: RAGConfig | null) => void;
    showComponents: string[]
    buttonTitle: string;
    settingTemplate: string
    baseSetting: Settings
}

const RAGComponent: React.FC<RAGComponentProps> = ({ APIHost, settingConfig, RAGConfig, setRAGConfig, showComponents, buttonTitle, baseSetting, settingTemplate }) => {

    const [currentRAGSettings, setCurrentRAGSettings] = useState<RAGConfig>(JSON.parse(JSON.stringify(RAGConfig)))
    const [files, setFiles] = useState<FileList | null>(null)
    const [isFetching, setIsFetching] = useState(false)

    const [consoleLog, setConsoleLog] = useState<ConsoleMessage[]>([])

    const saveSettings = () => {
        setRAGConfig(currentRAGSettings)
        if (buttonTitle === "Import") {
            importData()
        } else {
            importConfig()
        }
    }

    const importData = async () => {
        setIsFetching(true)

        if (!files) {
            setIsFetching(false)
            return
        }

        try {
            addToConsole("INFO", "Starting Import")
            const fileData = await processFiles(files);
            setFiles(null)
            if (fileData) {
                const payload = { config: { "RAG": currentRAGSettings, "SETTING": { "selectedTheme": settingTemplate, "themes": baseSetting } }, data: fileData }

                const response = await fetch(APIHost + "/api/import", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                })

                const data: ImportResponse = await response.json();

                if (data) {
                    for (let i = 0; i < data.logging.length; i++) {
                        setConsoleLog(oldItems => [...oldItems, data.logging[i]]);
                    }
                    setIsFetching(false)
                } else {
                    setIsFetching(false)
                }
            } else {
                setIsFetching(false)
            }

        } catch (error) {
            console.error("Failed to fetch from API:", error);
            setIsFetching(false);
        }
    }

    const importConfig = async () => {
        setIsFetching(true)

        try {

            const payload = { config: { "RAG": currentRAGSettings, "SETTING": { "selectedTheme": settingTemplate, "themes": baseSetting } } }

            const response = await fetch(APIHost + "/api/set_config", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            })

            const data: ImportResponse = await response.json();

            if (data) {
                console.log(data)
                setIsFetching(false)
            } else {
                setIsFetching(false)
            }


        } catch (error) {
            console.error("Failed to fetch from API:", error);
            setIsFetching(false);
        }
    }

    const resetSettings = () => {
        setCurrentRAGSettings(JSON.parse(JSON.stringify(RAGConfig)))
        setConsoleLog([])
    }

    const addToConsole = (t: "INFO" | "WARNING" | "SUCCESS" | "ERROR", m: string) => {
        const consoleMsg: ConsoleMessage = { type: t, message: m }
        setConsoleLog(oldItems => [...oldItems, consoleMsg]);

    }

    return (
        <div className="flex sm:flex-col md:flex-row justify-between gap-3 ">
            {currentRAGSettings && Object.entries(currentRAGSettings).map(([key, value]) => (
                showComponents.includes(key) && (
                    <div className='w-full md:w-1/4'>
                        <RAGConfigComponent key={key} files={files} setFiles={setFiles} settingConfig={settingConfig} APIHost={APIHost} RAGConfig={currentRAGSettings} RAGConfigTitle={key} RAGComponents={value} setRAGConfig={setCurrentRAGSettings} />
                    </div>
                )
            ))}
            {currentRAGSettings ? (
                <div className='flex flex-col gap-2 w-full md:w-1/4 items-end'>
                    <div className='flex flex-row gap-2 w-full'>
                        <button disabled={isFetching} onClick={saveSettings} className='btn w-1/2 btn-lg text-base flex gap-2 bg-secondary-verba hover:bg-button-hover-verba text-text-verba'>
                            {isFetching ? (
                                <div>
                                    <div className="flex items-center">
                                        <PulseLoader color={settingConfig.Customization.settings.text_color.color} loading={true} size={10} speedMultiplier={0.75} />
                                    </div>
                                </div>)
                                : (
                                    <div className='flex gap-2 items-center justify-center'>
                                        <FaFileImport />
                                        {buttonTitle}
                                        {files && (
                                            <p className='text-sm'>({files.length})</p>)}
                                    </div>
                                )}
                        </button>
                        <button disabled={isFetching} onClick={resetSettings} className='btn w-1/2 btn-lg text-base text-text-verba bg-warning-verba hover:bg-button-hover-verba'>
                            <MdCancel />
                            Clear
                        </button>
                    </div>
                    {buttonTitle === "Import" && (
                        <div className='flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 h-[58.5vh] overflow-auto w-full'>
                            <div className='flex flex-col'>
                                <p className='text-lg'>Console</p>
                            </div>
                            <div className='flex flex-col gap-2'>
                                {consoleLog && consoleLog.map((msg) => (
                                    <div>
                                        {
                                            msg.type === "INFO" && (
                                                <div className='flex text-text-verba text-sm gap-2'>
                                                    <p className='flex font-bold'>{msg.type}</p>
                                                    <p className='flex font-mono'>{msg.message}</p>
                                                </div>
                                            )
                                        }
                                        {
                                            msg.type === "SUCCESS" && (
                                                <div className='flex text-sm gap-2'>
                                                    <p className='flex font-bold text-secondary-verba '>{msg.type}</p>
                                                    <p className='flex font-mono text-text-verba'>{msg.message}</p>
                                                </div>
                                            )
                                        }
                                        {
                                            msg.type === "ERROR" && (
                                                <div className='flex text-sm gap-2'>
                                                    <p className='flex text-warning-verba font-bold'>{msg.type}</p>
                                                    <p className='flex text-text-verba font-mono'>{msg.message}</p>
                                                </div>
                                            )
                                        }
                                        {
                                            msg.type === "WARNING" && (
                                                <div className='flex text-sm gap-2'>
                                                    <p className='flex text-primary-verba font-bold'>{msg.type}</p>
                                                    <p className='flex text-text-verba font-mono'>{msg.message}</p>
                                                </div>
                                            )
                                        }
                                    </div>

                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ) : (

                <div className='flex items-center justify-center'>
                    <div className="flex items-center justify-center">
                        <PulseLoader color={settingConfig.Customization.settings.text_color.color} loading={true} size={10} speedMultiplier={0.75} />
                        <p>Loading Components...</p>
                    </div>
                </div>)}
        </div>


    );
};

export default RAGComponent;
