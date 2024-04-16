'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration, TextFieldSetting, ImageFieldSetting, CheckboxSetting, ColorSetting, BaseSettings } from "./types"
import { FaPaintBrush } from "react-icons/fa";
import { IoChatbubbleSharp } from "react-icons/io5";
import { FaCheckCircle } from "react-icons/fa";
import { MdCancel } from "react-icons/md";

import TextFieldComponent from './TextFieldComponent';
import ImageFieldComponent from './ImageFieldComponent';
import ColorFieldComponent from './ColorFieldComponent';

import SettingButton from "./settings_button"

interface SettingsComponentProps {
    settingsConfig: SettingsConfiguration
    setSettingsConfig: (settings: SettingsConfiguration) => void;

    settingTemplate: string
    setSettingTemplate: (s: string) => void;
}

const SettingsComponent: React.FC<SettingsComponentProps> = ({ settingsConfig, setSettingsConfig, settingTemplate, setSettingTemplate }) => {

    const [setting, setSetting] = useState<"Customization" | "Chat" | "">("Customization")
    const [currentSettingsConfig, setCurrentSettingsConfig] = useState<SettingsConfiguration>(JSON.parse(JSON.stringify(settingsConfig)))

    const [availableTemplate, setAvailableTemplate] = useState<string[]>(Object.keys(BaseSettings))

    useEffect(() => {

        setAvailableTemplate(Object.keys(BaseSettings))
        setCurrentSettingsConfig(JSON.parse(JSON.stringify(settingsConfig)))

    }, [settingTemplate, settingsConfig]);

    const iconSize = 20

    const applyChanges = () => {
        setSettingsConfig(currentSettingsConfig)
    }

    const revertChanges = () => {
        setCurrentSettingsConfig(BaseSettings[settingTemplate])
        setSettingsConfig(BaseSettings[settingTemplate])
    }

    const renderSettingComponent = (title: any, setting_type: TextFieldSetting | ImageFieldSetting | CheckboxSetting | ColorSetting) => {

        if (setting === "") {
            return null
        }

        switch (setting_type.type) {
            case 'text':
                return <TextFieldComponent title={title} setting={setting} TextFieldSetting={setting_type} settingsConfig={currentSettingsConfig} setSettingsConfig={setCurrentSettingsConfig} />;
            case 'image':
                return <ImageFieldComponent title={title} setting={setting} ImageFieldSetting={setting_type} settingsConfig={currentSettingsConfig} setSettingsConfig={setCurrentSettingsConfig} />;
            case 'check':
                return "Checkbox"
            case 'color':
                return <ColorFieldComponent title={title} setting={setting} ColorSetting={setting_type} settingsConfig={currentSettingsConfig} setSettingsConfig={setCurrentSettingsConfig} />;
            default:
                return null;
        }
    };

    const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const name = e.target.value;
        setSettingTemplate(name); // Update the selected template state
    };

    return (
        <div className="flex justify-between items-start gap-5">

            {/* Setting Options */}
            <div className='flex flex-col gap-5 w-1/4'>
                <div className='flex flex-col justify-center items-center gap-5'>
                    <p className='md:text-base lg:text-lg text-text-alt-verba'>Settings</p>
                    <div className='flex flex-col w-full bg-bg-alt-verba p-5 rounded-lg shadow-lg gap-2'>
                        <SettingButton Icon={FaPaintBrush} iconSize={iconSize} title='Customize Verba' currentSetting={setting} setSetting={setSetting} setSettingString='Customization' />
                        <SettingButton Icon={IoChatbubbleSharp} iconSize={iconSize} title='Chat Settings' currentSetting={setting} setSetting={setSetting} setSettingString='Chat' />
                    </div>
                </div>
                {setting != "" && (
                    <div className='sm:hidden md:flex flex-col justify-center items-center gap-5'>
                        <p className=' md:text-base lg:text-lg text-text-alt-verba'>Description</p>
                        <div className='flex flex-col w-full bg-bg-alt-verba p-5 rounded-lg shadow-lg gap-2'>
                            <p className='sm:text-xs md:text-sm lg:text-base'> {settingsConfig[setting] ? settingsConfig[setting].description : ""}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Configuration Options */}
            <div className='flex flex-col justify-center items-center gap-5 w-3/4'>
                <div className='flex flex-row gap-2 items-center justify-center'>
                    <p className='text-lg text-text-alt-verba'>Configuration</p>
                    <select value={settingTemplate} onChange={handleTemplateChange} className="select select-sm text-xs bg-bg-alt-verba text-text-verba">
                        {availableTemplate.map((template) => (
                            <option>{template}</option>
                        ))}
                    </select>
                </div>
                <div className='flex flex-col w-full bg-bg-alt-verba p-10 rounded-lg shadow-lg h-[70vh] gap-2 overflow-y-scroll'>
                    <p className='font-bold text-2xl mb-5'>{setting}</p>
                    <div className=' flex-coll gap-4 grid grid-cols-3'>
                        {setting && Object.entries(settingsConfig[setting].settings).map(([key, settingValue]) => (
                            renderSettingComponent(key, settingValue)
                        ))}
                    </div>
                    <div className='flex justify-end gap-2 mt-3'>
                        <button onClick={applyChanges} className="btn flex items-center justify-center border-none text-text-verba bg-secondary-verba hover:bg-button-hover-verba">
                            <FaCheckCircle />
                            <p className="">Apply</p>
                        </button>
                        <button onClick={revertChanges} className="btn flex items-center justify-center border-none text-text-verba bg-warning-verba hover:bg-button-hover-verba">
                            <MdCancel />
                            <p className="">Reset</p>
                        </button>
                    </div>
                </div>
            </div>

        </div >
    );
};

export default SettingsComponent;
