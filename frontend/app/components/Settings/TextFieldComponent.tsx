'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration, TextFieldSetting } from "./types"

interface TextFieldComponentProps {
    title: string;
    TextFieldSetting: TextFieldSetting
    setting: "Customization" | "Chat"

    settingsConfig: SettingsConfiguration
    setSettingsConfig: (settings: any) => void;

}

const TextFieldComponent: React.FC<TextFieldComponentProps> = ({ title, TextFieldSetting, setting, settingsConfig, setSettingsConfig }) => {


    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newText = e.target.value;
        setSettingsConfig((prevConfig: any) => {
            // Creating a deep copy of prevConfig to avoid mutating the original state directly
            const newConfig = JSON.parse(JSON.stringify(prevConfig));

            // Updating the copied state
            newConfig[setting].settings[title].text = newText;

            // Return the updated copy
            return newConfig;
        });
    };

    return (
        <div className='flex justify-center items-center gap-4'>
            <div className='flex w-1/3'>
                <p>
                    {TextFieldSetting.description}
                </p>
            </div>
            <div className='flex w-2/3'>
                <label className="input input-bordered flex items-center gap-2 w-full">
                    <input
                        type="text"
                        className="grow"
                        placeholder={title}
                        value={(settingsConfig[setting].settings as any)[title].text}
                        onChange={handleChange} />
                </label>
            </div>

        </div>

    );
};

export default TextFieldComponent;
