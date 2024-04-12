'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration } from "./types"
import { FaPaintBrush } from "react-icons/fa";
import { IoChatbubbleSharp } from "react-icons/io5";

import SettingButton from "./settings_button"

interface SettingsComponentProps {
    settingsConfig: SettingsConfiguration
    setSettingsConfig: (settings: SettingsConfiguration) => void;
}

const SettingsComponent: React.FC<SettingsComponentProps> = ({ settingsConfig, setSettingsConfig }) => {

    const [setting, setSetting] = useState<"Customization" | "Chat" | "">("")

    const iconSize = 20

    return (
        <div className="flex justify-between items-start gap-5">

            {/* Setting Options */}
            <div className='flex flex-col gap-5 w-1/4'>
                <div className='flex flex-col justify-center items-center gap-5'>
                    <p className='md:text-base lg:text-lg text-text-alt-verba'>Settings</p>
                    <div className='flex flex-col w-full bg-white p-5 rounded-lg shadow-lg gap-2'>
                        <SettingButton Icon={FaPaintBrush} iconSize={iconSize} title='Customize Verba' currentSetting={setting} setSetting={setSetting} setSettingString='Customization' />
                        <SettingButton Icon={IoChatbubbleSharp} iconSize={iconSize} title='Chat Settings' currentSetting={setting} setSetting={setSetting} setSettingString='Chat' />
                    </div>
                </div>
                {setting != "" && (
                    <div className='sm:hidden md:flex flex-col justify-center items-center gap-5'>
                        <p className=' md:text-base lg:text-lg text-text-alt-verba'>Description</p>
                        <div className='flex flex-col w-full bg-white p-5 rounded-lg shadow-lg gap-2'>
                            <p className='sm:text-xs md:text-sm lg:text-base'> {settingsConfig[setting] ? settingsConfig[setting].description : ""}</p>
                        </div>
                    </div>
                )}
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
