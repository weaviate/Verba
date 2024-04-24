'use client'

import React, { useState, useEffect } from 'react';
import { FaStar } from "react-icons/fa";

interface ComponentStatusProps {
    component_name: string
    Icon: typeof FaStar;
    changeTo: string;
    changePage: (p: string) => void;
}

const ComponentStatus: React.FC<ComponentStatusProps> = ({ component_name, Icon, changeTo, changePage }) => {

    return (
        <button onClick={() => changePage(changeTo)} className={`btn btn-sm w-full border-none p-2 rounded-lg text-text-verba text-sm bg-button-verba hover:bg-primary-verba }`}>
            <Icon size={15} />
            <p className={`text-xs "text-text-verba`}>
                {component_name}
            </p>
        </button>
    );
};

export default ComponentStatus;
