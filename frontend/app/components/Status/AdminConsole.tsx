'use client'
import React, { useState, useEffect, useRef } from 'react';
import { DocumentChunk } from '../Document/types';
import CountUp from 'react-countup';
import { SettingsConfiguration } from '../Settings/types';

import { StatusPayload, Status, SchemaStatus } from './types';
import { MdDelete } from "react-icons/md";

import StatusLabel from '../Chat/StatusLabel';
import StatusCard from './StatusCard';
import PulseLoader from "react-spinners/PulseLoader";

interface AdminConsoleComponentProps {

    type: string | null;
    connected: string;
    schemas: SchemaStatus | null;
    isFetching: boolean
    settingConfig: SettingsConfiguration
}

const AdminConsoleComponent: React.FC<AdminConsoleComponentProps> = ({
    type,
    connected, isFetching, schemas, settingConfig
}) => {

    return (
        <div className='flex flex-col gap-2' >
            <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-6 h-[65vh] overflow-auto">
                <div className='flex lg:flex-row flex-col gap-2'>
                    <p className='text-text-verba font-bold text-lg'>
                        Admin Console
                    </p>
                    <div className='flex gap-2'>
                        <StatusLabel status={type !== null} true_text={type ? type : ""} false_text={type ? type : ""} />
                        <StatusLabel status={connected === "Online"} true_text={connected} false_text="Connecting..." />
                    </div>
                </div>

                {isFetching && (
                    <div className="flex items-center justify-center pl-4 mb-4 gap-3">
                        <PulseLoader color={settingConfig.Customization.settings.text_color.color} loading={true} size={10} speedMultiplier={0.75} />
                        <p>
                            Loading Stats
                        </p>
                    </div>
                )}

                {connected === "Online" && (
                    <div className='gap-2 grid grid-cols-2'>
                        <button className='btn bg-button-verba text-text-verba hover:bg-warning-verba flex gap-2'>
                            <div className='hidden lg:flex'>
                                <MdDelete />
                            </div>
                            <p className='flex text-xs'>
                                Reset Verba
                            </p>
                        </button>
                        <button className='btn bg-button-verba text-text-verba hover:bg-warning-verba flex gap-2'>
                            <div className='hidden lg:flex'>
                                <MdDelete />
                            </div>
                            <p className='flex text-xs'>
                                Reset Documents
                            </p>
                        </button>
                        <button className='btn bg-button-verba text-text-verba hover:bg-warning-verba flex gap-2'>
                            <div className='hidden lg:flex'>
                                <MdDelete />
                            </div>
                            <p className='flex text-xs'>
                                Reset Cache
                            </p>
                        </button>
                        <button className='btn bg-button-verba text-text-verba hover:bg-warning-verba flex gap-2'>
                            <div className='hidden lg:flex'>
                                <MdDelete />
                            </div>
                            <p className='flex text-xs'>
                                Reset Suggestion
                            </p>
                        </button>
                    </div>
                )}


                <div className='flex flex-col gap-2'>
                    {schemas && Object.entries(schemas).map(([key, value]) => (
                        <StatusCard key={key + "SCHEMA"} title={key} value={value} checked={false} />
                    ))}

                </div>

            </div>
        </div >
    );
};

export default AdminConsoleComponent;
