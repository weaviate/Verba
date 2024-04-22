'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration } from "../Settings/types"

import AdminConsoleComponent from '../Status/AdminConsole';
import StatusConsoleComponent from '../Status/StatusConsole';

import { StatusPayload, Status, SchemaStatus } from '../Status/types';
import { RAGComponent, RAGConfig, RAGComponentClass } from './types';

import { TextFieldSetting, NumberFieldSetting } from '../Settings/types';

import TextFieldRAGComponent from './TextFieldRAGComponent';

interface RAGConfigComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
    RAGConfig: RAGConfig;
    RAGConfigTitle: string;
    RAGComponents: RAGComponentClass
    setRAGConfig: (r_: any) => void;
}

const RAGConfigComponent: React.FC<RAGConfigComponentProps> = ({ APIHost, settingConfig, RAGConfig, RAGConfigTitle, RAGComponents, setRAGConfig }) => {

    const [files, setFiles] = useState<FileList | null>(null)

    const onSelectComponent = (_selected: string) => {
        setRAGConfig((prevConfig: any) => {
            const newConfig = JSON.parse(JSON.stringify(prevConfig));
            newConfig[RAGConfigTitle].selected = _selected;
            return newConfig;
        });
    };

    const handleUploadFiles = (event: React.ChangeEvent<HTMLInputElement>) => {
        console.log("TRIGGERED")
        if (event.target.files && event.target.files[0]) {
            setFiles(event.target.files)
        }
    };

    const renderSettingComponent = (title: any, setting_type: TextFieldSetting | NumberFieldSetting) => {

        if (!RAGConfig) {
            return null
        }

        switch (setting_type.type) {
            case 'text':
                return <TextFieldRAGComponent title={title} RAGConfig={RAGConfig} TextFieldSetting={setting_type} RAGComponentTitle={RAGComponents.selected} RAGConfigTitle={RAGConfigTitle} setRAGConfig={setRAGConfig} />;
            case 'number':
                return null;
            default:
                return null;
        }
    };


    return (
        <div className="flex sm:flex-col md:flex-row justify-center items-start gap-3 w-full">
            <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 h-[65vh] overflow-auto w-full">

                <div className='flex flex-col'>
                    <p className='text-lg'>Select a {RAGConfigTitle}</p>
                </div>

                <div className='grid grid-cols-1 lg:grid-cols-2 gap-2'>
                    {RAGComponents && Object.entries(RAGComponents.components).map(([key, value]) => (
                        <button onClick={() => { onSelectComponent(key) }} className={`btn ${key === RAGComponents.selected ? ("bg-secondary-verba") : ("bg-button-verba")} hover:bg-button-hover-verba`}>
                            <p>
                                {key}
                            </p>
                        </button>
                    ))}
                </div>

                <div className='flex flex-col gap-1'>
                    <div className='flex lg:flex-row flex-col gap-1'>
                        <p className='lg:text-base text-xs'>You selected: </p>
                        <p className='font-bold lg:text-base text-sm'>{RAGComponents.selected}</p>
                    </div>
                    <p className='text-sm text-text-alt-verba'>{RAGComponents.components[RAGComponents.selected].description}</p>
                </div>

                <div className=' flex-col gap-4 grid grid-cols-1 lg:grid-cols-1'>
                    {RAGConfig && Object.entries(RAGComponents.components[RAGComponents.selected].config).map(([key, settingValue]) => (
                        renderSettingComponent(key, settingValue)
                    ))}
                </div>

                {RAGComponents.components[RAGComponents.selected].type === "UPLOAD" && (
                    <div className='flex lg:flex-row flex-col gap-3'>
                        <div className='flex flex-col gap-2 items-center'>
                            <div className='flex'>
                                <button onClick={() => document.getElementById(RAGConfigTitle + RAGComponents.selected + "_upload")?.click()} className="btn border-none bg-button-verba hover:bg-secondary-verba ">Add Files</button>
                                <input id={RAGConfigTitle + RAGComponents.selected + "_upload"} type="file" onChange={handleUploadFiles} className="hidden" multiple />
                            </div>
                            {files && (
                                <div className='flex'>
                                    <button onClick={() => { setFiles(null) }} className="btn text-sm border-none bg-warning-verba hover:bg-button-hover-verba ">Clear Files</button>
                                </div>
                            )}
                        </div>
                        {files && (
                            <div className='flex gap-2'>
                                <p className='flex text-text-alt-verba text-sm '>Files:</p>
                                <div className='flex flex-col gap-1 overflow-y-auto h-[15vh] border-2 p-2 rounded-lg border-bg-verba'>
                                    {files && Array.from(files).map((file, index) => (
                                        <p key={index + file.name}>{file.name}</p>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                <div>

                </div>

            </div >

        </div >
    );
};

export default RAGConfigComponent;
