'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration } from "../Settings/types"

import AdminConsoleComponent from './AdminConsole';

import { StatusPayload, Status, SchemaStatus } from './types';

interface StatusComponentComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
}

const StatusComponent: React.FC<StatusComponentComponentProps> = ({ APIHost, settingConfig }) => {

    const [type, setType] = useState<string | null>(null);
    const [connected, setConnected] = useState<"Online" | "Offline">("Offline");
    const [libraries, setLibraries] = useState<Status | null>(null);
    const [variables, setVariables] = useState<Status | null>(null);
    const [schemas, setSchemas] = useState<SchemaStatus | null>(null);
    const [isFetching, setIsFetching] = useState(false)

    useEffect(() => {
        if (APIHost != null) {
            const fetchStatus = async () => {
                try {
                    setIsFetching(true)

                    const response = await fetch(APIHost + "/api/get_status", {
                        method: "GET",
                    });
                    const data: StatusPayload = await response.json();

                    if (data) {

                        if (data.error) {
                            console.log(data.error)
                        }

                        setType(data.type)
                        setConnected("Online")
                        setLibraries(data.libraries)
                        setVariables(data.variables)
                        setSchemas(data.schemas)
                        setIsFetching(false)

                    } else {
                        console.warn("Status could not be retrieved")
                    }
                } catch (error) {
                    console.error("Failed to fetch document:", error);
                    setConnected("Offline")
                    setType(null)
                    setLibraries(null)
                    setVariables(null)
                    setSchemas(null)
                    setIsFetching(false)
                }
            }

            fetchStatus();
        } else {
            console.warn("Missing API Host for retrieving status")
            setConnected("Offline")
            setType(null)
            setLibraries(null)
            setVariables(null)
            setSchemas(null)
            setIsFetching(false)
        }
    }, []);


    return (
        <div className="flex sm:flex-col md:flex-row justify-center items-start gap-3 ">

            <div className='w-2/3'>
                <AdminConsoleComponent settingConfig={settingConfig} type={type} isFetching={isFetching} connected={connected} schemas={schemas} />
            </div>

            <div className='w-1/3'>

            </div>

            <div className='w-1/3'>

            </div>

        </div >
    );
};

export default StatusComponent;
