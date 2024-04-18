'use client'
import React, { useState, useEffect, useRef } from 'react';
import { DocumentChunk } from '../Document/types';

interface DocumentComponentProps {
    selectedChunk: DocumentChunk | null
}

const DocumentComponent: React.FC<DocumentComponentProps> = ({
    selectedChunk
}) => {

    return (
        <div className='flex flex-col gap-2' >
            {/*Chat Messages*/}
            <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-5 md:h-[47vh] lg:h-[65vh] overflow-auto">

            </div >
        </div >
    );
};

export default DocumentComponent;
