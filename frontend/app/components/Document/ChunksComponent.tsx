'use client'
import React, { useState, useEffect, useRef } from 'react';
import { DocumentChunk } from '../Document/types';
import CountUp from 'react-countup';

import StatusLabel from '../Chat/StatusLabel';

interface ChunksComponentComponentProps {
    chunks: DocumentChunk[]
    selectedChunk: DocumentChunk | null
    chunkTime: number;
    setSelectedChunk: (c: DocumentChunk | null) => void;
}

const ChunksComponent: React.FC<ChunksComponentComponentProps> = ({
    chunks,
    selectedChunk,
    chunkTime,
    setSelectedChunk
}) => {

    useEffect(() => {
        if (chunks.length > 0) {
            setSelectedChunk(chunks[0])
        } else {
            setSelectedChunk(null)
        }
    }, [chunks]);

    return (
        <div className='flex flex-col gap-2' >
            {/*Chunks*/}
            <div className="flex flex-col bg-bg-alt-verba rounded-lg shadow-lg p-5 text-text-verba gap-3 md:h-[17vh] lg:h-[65vh] overflow-auto">
                <div className='flex lg:flex-col md:flex-row gap-5'>
                    <div className='flex md:flex-row lg:flex-col gap-2 justify-center items-center'>
                        <StatusLabel status={true} true_text='WindowRetriever' false_text='No Caching' />
                        <StatusLabel status={false} true_text='Caching' false_text='OpenAIEmbedder' />
                    </div>
                    {chunks.length > 0 && (
                        <div className='sm:hidden md:flex items-center justify-center'>
                            <p className='items-center justify-center text-text-alt-verba text-xs'>
                                {chunks.length} chunks retrieved in {chunkTime} seconds.
                            </p>
                        </div>
                    )}
                </div>
                <div className='flex md:flex-row lg:flex-col gap-2'>
                    {chunks.map((chunk, index) => (
                        <button key={chunk.doc_name + index} onClick={() => setSelectedChunk(chunk)} className={`btn md:btn-md lg:btn-lg sm:w-1/3 lg:w-full flex justify-start gap-4 ${selectedChunk?.chunk_id === chunk.chunk_id && selectedChunk.doc_uuid === chunk.doc_uuid ? ("bg-secondary-verba") : ("bg-button-verba")} hover:button-hover-verba`}>
                            <div className={`sm:hidden md:flex md:text-sm text-base w-1/6`}>
                                <CountUp end={Math.round(chunk.score * 100)} />
                            </div>
                            <div className='flex flex-col items-start truncate md:w-4/6'>
                                <p className="text-xs lg:text-sm text-text-verba">{chunk.doc_name}</p>
                                <p className="text-xs text-text-alt-verba">{chunk.doc_type}</p>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div >
    );
};

export default ChunksComponent;
