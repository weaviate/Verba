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

interface StatusConsoleComponentProps {

    title: string;
    status: Status | null;
    isFetching: boolean;
    settingConfig: SettingsConfiguration
}

const StatusConsoleComponent: React.FC<StatusConsoleComponentProps> = ({
    title, status, isFetching, settingConfig
}) => {

    return (
        <div className='flex flex-col gap-2' >
            <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-6 h-[65vh] overflow-auto">

                <div className='flex gap-2'>
                    <p className='text-text-verba font-bold text-lg'>
                        {title}
                    </p>
                </div>

                {isFetching && (
                    <div className="flex items-center justify-center pl-4 mb-4 gap-3">
                        <PulseLoader color={settingConfig.Customization.settings.text_color.color} loading={true} size={10} speedMultiplier={0.75} />
                    </div>
                )}


                <div className='flex flex-col gap-2'>
                    {status && Object.entries(status).map(([key, value]) => (
                        <StatusCard title={key} value={null} checked={value} />
                    ))}

                </div>

            </div>
        </div >
    );
};

export default StatusConsoleComponent;
