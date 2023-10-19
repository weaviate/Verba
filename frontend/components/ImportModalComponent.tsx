import React, { useState, useEffect } from 'react';
import { FaPlus, FaTimes } from "react-icons/fa";
import { useDropzone } from 'react-dropzone';
import CoolButton from "../components/CoolButton";
import HashLoader from "react-spinners/HashLoader";

type ImportModalProps = {
    onClose: () => void;
    apiHost: string;
}

export type Component = {
    name: string;
    description: string;
    input_form: 'UPLOAD' | 'INPUT' | 'CHUNKER' | 'TEXT';
    available: boolean;
    message: string;
    units?: number,
    overlap?: number
};

const ImportModal: React.FC<ImportModalProps> = ({ onClose, apiHost }) => {
    const [readers, setReaders] = useState<Component[]>([]);
    const [chunker, setChunker] = useState<Component[]>([]);
    const [embedder, setEmbedder] = useState<Component[]>([]);
    const [selectedOption, setSelectedOption] = useState<string>("Reader");
    const [selectedReader, setSelectedReader] = useState<Component | null>(null);
    const [selectedChunker, setSelectedChunker] = useState<Component | null>(null);
    const [chunkUnits, setChunkUnits] = useState<number>(100);
    const [chunkOverlap, setChunkOverlap] = useState<number>(50);
    const [selectedEmbedder, setSelectedEmbedder] = useState<Component | null>(null);

    const [loadingState, setLoadingState] = useState<boolean>(false);

    const [droppedFiles, setDroppedFiles] = useState<File[]>([]);
    const [filePath, setFilePath] = useState<string>("");

    const [docType, setDocType] = useState<string>("Documentation");
    const [inputFileKey, setInputFileKey] = useState<number>(Date.now());  // Using the current timestamp as the initial key  
    const [apiResponse, setApiResponse] = useState<{ status: number, status_msg: string } | null>(null);

    useEffect(() => {
        // Fetch the list of readers from your API when the component mounts
        const fetchReaders = async () => {
            try {
                const response = await fetch(apiHost + '/api/get_components');
                const data = await response.json();
                setReaders(data.readers);
                setChunker(data.chunker);
                setEmbedder(data.embedder);

                if (data.readers && data.readers.length > 0) {
                    setSelectedReader(data.default_values.last_reader);
                    handleChunkerSelection(data.default_values.last_chunker)
                    setSelectedEmbedder(data.default_values.last_embedder)
                    setDocType(data.default_values.last_document_type)
                }
            } catch (error) {
                console.error("Error fetching readers:", error);
            }
        }
        fetchReaders();
    }, [apiHost]);

    const handleFilePathInput = (event: React.ChangeEvent<HTMLInputElement>) => {
        setFilePath(event.target.value);
    };

    const handleImport = async () => {
        if (!selectedReader || !selectedChunker || !selectedEmbedder) {
            console.error("Missing component");
            return;
        }

        setLoadingState(true);

        const fileNames: string[] = droppedFiles.map(file => file.name);

        // Read the File objects to get their bytes and convert them to base64 strings
        const promises = droppedFiles.map(file => {
            return new Promise<string>((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    // Convert ArrayBuffer to base64 string
                    const base64String = btoa(
                        Array.from(new Uint8Array(reader.result as ArrayBuffer)).map(
                            (byte) => String.fromCharCode(byte)
                        ).join('')
                    );
                    resolve(base64String);
                };
                reader.readAsArrayBuffer(file);
            });
        });

        const fileBytesBase64 = await Promise.all(promises);

        let payload = {
            reader: selectedReader.name,
            chunker: selectedChunker.name,
            embedder: selectedEmbedder.name,
            fileBytes: fileBytesBase64,
            fileNames: fileNames,
            filePath: filePath,
            document_type: docType,
            chunkUnits: chunkUnits,
            chunkOverlap: chunkOverlap,

        };

        try {
            const response = await fetch(`${apiHost}/api/load_data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            setLoadingState(false);

            if (response.ok) {
                // Clear files and path after successful import
                setDroppedFiles([]);
                setFilePath("");

                // Reset the input file by changing its key
                setInputFileKey(Date.now());
            } else {
                console.error("Error from server:", data);
            }

            setApiResponse(data);

            // Handle the response as needed, e.g., show a success message
        } catch (error) {
            console.error("Error importing data:", error);
            // Handle the error as needed, e.g., show an error message
        }
    };

    const onDrop = async (acceptedFiles: File[]) => {
        setDroppedFiles(prevFiles => [...prevFiles, ...acceptedFiles]);
    };

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: {
            'text/txt': ['.txt', '.md', '.mdx'],
            'text/verba': ['.verba']
        }
    });

    const handleChunkerSelection = (chunk: Component) => {
        setSelectedChunker(chunk);
        if (chunk.units !== undefined) {
            setChunkUnits(chunk.units);
        }
        if (chunk.overlap !== undefined) {
            setChunkOverlap(chunk.overlap);
        }
    };


    const handleChunkerUnitsSelection = (value: number) => {
        setChunkUnits(value);
        if (selectedChunker) {
            selectedChunker.units = value;
            setSelectedChunker({ ...selectedChunker });
        }
    };

    const handleChunkerOverlapSelection = (value: number) => {
        setChunkOverlap(value);
        if (selectedChunker) {
            selectedChunker.overlap = value;
            setSelectedChunker({ ...selectedChunker });
        }
    };

    const handleRemoveAllFiles = () => {
        setDroppedFiles([]);
    };

    return (
        <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center z-50">
            <div className="absolute w-full h-full bg-black opacity-50"></div>
            <div className="bg-gray-200 border-2 border-black lg:w-2/5 md:w-full md:m-3 z-10 rounded-xl shadow-md animate-pop-in">
                <div className="flex justify-start items-center mb-4 p-4">
                    <button onClick={onClose} className="mr-3 bg-red-500 text-white hover:bg-red-600 shadow-md hover-container p-2 rounded-full flex items-center justify-center">
                        <FaTimes />
                    </button>
                    <button onClick={() => setSelectedOption("Reader")} className={`${"Reader" === selectedOption ? 'bg-yellow-200' : 'bg-gray-200'} text-black text-lg rounded-lg font-bold border-2 border-black animate-pop-in-late truncate p-4 w-full hover-container shadow-md mr-6 hover:bg-yellow-300 hover:border-white`}>{selectedReader?.name}</button>
                    <button onClick={() => setSelectedOption("Chunking")} className={`${"Chunking" === selectedOption ? 'bg-cyan-200' : 'bg-gray-200'} text-black text-lg rounded-lg font-bold border-2 border-black animate-pop-in-late p-4 truncate w-full hover-container shadow-md mr-6 hover:bg-cyan-300 hover:border-white`}>{selectedChunker?.name}</button>
                    <button onClick={() => setSelectedOption("Embedding")} className={`${"Embedding" === selectedOption ? 'bg-fuchsia-200' : 'bg-gray-200'} bg-gray-200 text-black text-lg rounded-lg font-bold border-2 border-black truncate animate-pop-in-late p-4 w-full hover-container shadow-md hover:bg-fuchsia-300 hover:border-white`}>{selectedEmbedder?.name}</button>

                </div>
                <div className="flex p-4">
                    {/* Left column for the list of readers */}
                    <div className="w-2/5 pr-2 border-r border-gray-300 overflow-y-auto max-h-80">
                        <ul>
                            {selectedOption === "Reader" ? (
                                readers.map((reader, index) => (
                                    <CoolButton
                                        key={reader.name + index}
                                        main={reader.name}
                                        clipboard={false}
                                        sub={reader.available ? '' : reader.message} // You can add any subtitle here or leave it empty if not needed.
                                        onClick={() => setSelectedReader(reader)}
                                        subBgColor={reader.available ? 'green' : 'red'}
                                        isActive={reader.name === selectedReader?.name}
                                        available={reader.available}
                                        title={reader.name}
                                    />
                                ))
                            ) : selectedOption === "Chunking" ? (
                                chunker.map((chunk, index) => (
                                    <CoolButton
                                        key={chunk.name + index}
                                        main={chunk.name}
                                        clipboard={false}
                                        sub={chunk.available ? '' : chunk.message} // You can add any subtitle here or leave it empty if not needed.
                                        onClick={() => handleChunkerSelection(chunk)}
                                        mainBgColor='cyan'
                                        subBgColor={chunk.available ? 'green' : 'red'}
                                        isActive={chunk.name === selectedChunker?.name}
                                        available={chunk.available}
                                        title={chunk.name}
                                    />
                                ))
                            ) : selectedOption === "Embedding" ? (
                                embedder.map((embedder, index) => (
                                    <CoolButton
                                        key={embedder.name + index}
                                        main={embedder.name}
                                        clipboard={false}
                                        sub={embedder.available ? '' : embedder.message}
                                        available={embedder.available} // You can add any subtitle here or leave it empty if not needed.
                                        onClick={() => setSelectedEmbedder(embedder)}
                                        mainBgColor='fuchsia'
                                        subBgColor={embedder.available ? 'green' : 'red'}
                                        isActive={embedder.name === selectedEmbedder?.name}
                                        title={embedder.name}
                                    />
                                ))
                            ) : null}
                        </ul>
                    </div>
                    {/* Right column for configurations */}
                    <div className="w-3/5 p-4">
                        <div className='mb-6'>
                            {selectedOption === "Reader" && selectedReader && selectedReader.input_form === 'UPLOAD' ? (
                                <div className=''>
                                    <h3 className='mb-2'>📁 Upload documents</h3>
                                    <div {...getRootProps()} className="border-dashed border-2 p-4 border-white rounded-lg">
                                        <input {...getInputProps()} />
                                        <p className='text-sm text-gray-500'>Drop your files here, or click to select files</p>
                                    </div>
                                    <div className='my-6'>
                                        {droppedFiles.length > 0 && (
                                            <div className="flex items-center space-x-2 mb-2">
                                                <span className="truncate">{droppedFiles.length} files selected</span>
                                                <button onClick={handleRemoveAllFiles} className="bg-red-500 p-1 rounded-full hover:bg-red-600">
                                                    <FaTimes />
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                    <div className="mb-2">
                                        <label htmlFor="docType" className="block text-sm font-medium text-gray-700">Document Type</label>
                                        <input
                                            type="text"
                                            id="docType"
                                            name="docType"
                                            value={docType}
                                            onChange={(e) => setDocType(e.target.value)}
                                            className="mt-1 focus:ring-yellow p-3
                                            -500 focus:border-yellow-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                            placeholder="Documentation"
                                        />
                                    </div>
                                </div>
                            ) : selectedOption === "Reader" && selectedReader && selectedReader.input_form === 'INPUT' ? (
                                <div className=''>
                                    <h3 className='mb-2'>Provide File Path</h3>
                                    <input
                                        type="text"
                                        value={filePath}
                                        placeholder="Enter absolute path"
                                        onChange={handleFilePathInput}
                                        className='p-2 rounded-lg w-full'
                                    />
                                </div>
                            ) : selectedOption === "Chunking" && selectedChunker?.input_form === 'CHUNKER' ? (
                                <div className='flex space-x-2'>
                                    <h3 className='mb-2'>Units</h3>
                                    <input
                                        type="number"
                                        value={chunkUnits}
                                        placeholder="Start Size"
                                        onChange={(e) => setChunkUnits(Number(e.target.value))}
                                        className='p-2 rounded-lg w-1/2'
                                    />
                                    <h3 className='mb-2'>Overlap</h3>
                                    <input
                                        type="number"
                                        value={chunkOverlap}
                                        placeholder="End Size"
                                        onChange={(e) => setChunkOverlap(Number(e.target.value))}
                                        className='p-2 rounded-lg w-1/2'
                                    />
                                </div>
                            ) : selectedOption === "Embedding" && selectedEmbedder?.input_form === 'TEXT' ? (
                                <div className='flex space-x-2'>

                                </div>
                            ) : null}
                        </div>
                        <div className='text-center shadow-md rounded-lg p-4 hover-container overflow-y-auto mb-6'>
                            <p>{selectedOption === "Reader" ? selectedReader?.description : selectedOption === "Chunking" ? selectedChunker?.description : selectedEmbedder?.description}</p>
                        </div>
                        <div className="flex justify-end">
                            <button
                                onClick={handleImport}
                                disabled={loadingState} // Disable the button when loading
                                className={`flex items-center space-x-2 bg-gray-200 text-black p-3 rounded-lg border-2 border-black hover-container shadow-md ${loadingState ? 'cursor-not-allowed hover:bg-gray-200' : 'hover:bg-green-400 hover:border-white'}`}
                            >
                                {loadingState ? (
                                    // Display when loading
                                    <>
                                        <HashLoader color='#292929' loading={true} size={20} speedMultiplier={0.75} />
                                        <span>Importing...</span>
                                    </>
                                ) : (
                                    // Display when not loading
                                    <>
                                        <FaPlus />
                                        <span>Import</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div >
                </div>
                {
                    apiResponse && (
                        <div
                            className={`p-4 rounded-lg shadow-md m-4 hover-container animate-pop-in
                ${apiResponse.status === 200 ? 'bg-green-400' : 'bg-red-400'}`}>
                            {apiResponse.status_msg}
                        </div>
                    )
                }
            </div>
        </div >
    );
}

export default ImportModal;
