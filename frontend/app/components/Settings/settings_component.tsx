'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration } from "./types"
import { FaPaintBrush } from "react-icons/fa";
import { IoChatbubbleSharp } from "react-icons/io5";

interface SettingsComponentProps {
    settingsConfig: SettingsConfiguration
    setSettingsConfig: (settings: SettingsConfiguration) => void;
}

const SettingsComponent: React.FC<SettingsComponentProps> = ({ settingsConfig, setSettingsConfig }) => {

    const [setting, setSetting] = useState("")

    const iconSize = 20

    return (
        <div className="flex justify-between items-start gap-5">

            {/* Setting Options */}
            <div className='flex flex-col gap-5 w-1/4'>
                <div className='flex flex-col justify-center items-center gap-5'>
                    <p className='text-lg text-text-alt-verba'>Settings</p>
                    <div className='flex flex-col w-full bg-white p-5 rounded-lg shadow-lg gap-2'>
                        <button className={`btn btn-lg flex items-center justify-center border-none ${setting === "Customization" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setSetting("Customization") }}>
                            <FaPaintBrush size={iconSize} />
                            <p className="text-lg">Customize Verba</p>
                        </button>
                        <button className={`btn btn-lg flex items-center justify-center border-none ${setting === "Chat" ? ("bg-primary-verba hover:bg-white") : "bg-verba-bg text-text-alt-verba"}`} onClick={(e) => { setSetting("Chat") }}>
                            <IoChatbubbleSharp size={iconSize} />
                            <p className="text-lg">Chat Settings</p>
                        </button>
                    </div>
                </div>
                <div className='flex flex-col justify-center items-center gap-5'>
                    <p className='text-lg text-text-alt-verba'>Description</p>
                    <div className='flex flex-col w-full bg-white p-5 rounded-lg shadow-lg gap-2'>
                        <p> {settingsConfig[setting] ? settingsConfig[setting].description : ""}</p>
                    </div>
                </div>
            </div>

            {/* Configuration Options */}
            <div className='flex flex-col justify-center items-center gap-5 w-3/4'>
                <p className='text-lg text-text-alt-verba'>Configuration</p>
                <div className='flex flex-col w-full bg-white p-5 rounded-lg shadow-lg h-[70vh] gap-2'>

                </div>
            </div>

        </div>
    );
};

export default SettingsComponent;
