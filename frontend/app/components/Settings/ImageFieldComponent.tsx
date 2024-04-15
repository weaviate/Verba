'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration, ImageFieldSetting } from "./types"

interface ImageFieldComponentProps {
    title: string;
    ImageFieldSetting: ImageFieldSetting
    setting: "Customization" | "Chat"

    settingsConfig: SettingsConfiguration
    setSettingsConfig: (settings: any) => void;

}

const ImageFieldComponent: React.FC<ImageFieldComponentProps> = ({ title, ImageFieldSetting, setting, settingsConfig, setSettingsConfig }) => {

    const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            const reader = new FileReader();

            reader.onload = (e) => {
                setSettingsConfig((prevConfig: any) => {
                    // Creating a deep copy of prevConfig to avoid mutating the original state directly
                    const newConfig = JSON.parse(JSON.stringify(prevConfig));

                    // Updating the copied state
                    newConfig[setting].settings[title].src = e.target?.result as string;

                    // Return the updated copy
                    return newConfig;
                });
            };
            reader.readAsDataURL(event.target.files[0]);
        }
    };

    return (
        <div className='flex justify-center items-center gap-4'>
            <div className='flex w-1/3'>
                <p>
                    {ImageFieldSetting.description}
                </p>
            </div>
            <div className='flex w-2/3'>
                <div>
                    <div className="flex justify-center items-center mt-4">
                        <img src={(settingsConfig[setting].settings as any)[title].src} alt="Logo" className="max-w-xs max-h-52 rounded-xl" />
                    </div>
                    <div className='flex justify-center items-center mt-1'>
                        <button onClick={() => document.getElementById("LogoImageInput")?.click()} className="btn text-xs bg-verba text-text-alt-verba">Add Logo</button>
                        <input id={"LogoImageInput"} type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                    </div>
                </div>
            </div>

        </div>

    );
};

export default ImageFieldComponent;
