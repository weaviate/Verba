'use client'

import React, { useState, useEffect } from 'react';
import { SettingsConfiguration } from "../Settings/types"
import { DocumentChunk, Document } from '../Document/types';

import DocumentComponent from '../Document/DocumentComponent';
import DocumentSearchComponent from './DocumentSearchComponent';

interface DocumentViewerComponentProps {
    settingConfig: SettingsConfiguration;
    APIHost: string | null;
}

const DocumentViewerComponent: React.FC<DocumentViewerComponentProps> = ({ APIHost, settingConfig }) => {

    const [documents, setDocuments] = useState<Document[] | null>([])
    const [documentTime, setDocumentTime] = useState(0);
    const [selectedDocument, setSelectedDocument] = useState<DocumentChunk | null>(null)
    const [triggerReset, setTriggerReset] = useState(false)

    return (
        <div className="flex sm:flex-col md:flex-row justify-center items-start gap-3 ">
            {/* Chat Interface */}
            <div className='sm:w-full md:w-2/4'>
                <DocumentSearchComponent triggerReset={triggerReset} documents={documents} setDocuments={setDocuments} APIHost={APIHost} setSelectedDocument={setSelectedDocument} settingConfig={settingConfig} selectedDocument={selectedDocument} />
            </div>

            <div className='sm:w-full md:w-2/4'>
                <DocumentComponent setTriggerReset={setTriggerReset} deletable={true} setDocuments={setDocuments} setSelectedChunk={setSelectedDocument} selectedChunk={selectedDocument} APIhost={APIHost} settingConfig={settingConfig} selectedDocument={null} />
            </div>

        </div >
    );
};

export default DocumentViewerComponent;
