import React, { useState, useEffect } from 'react';
import { FaPlus, FaTimes } from "react-icons/fa";

type ImportModalProps = {
    onClose: () => void;
    apiHost: string;
}

type Reader = {
    name: string;
    description: string;
    input_form: 'UPLOAD' | 'INPUT';
};

const ImportModal: React.FC<ImportModalProps> = ({ onClose, apiHost }) => {
    const [readers, setReaders] = useState<Reader[]>([]);
    const [selectedOption, setSelectedOption] = useState<string>("Reader");
    const [selectedReader, setSelectedReader] = useState<Reader | null>(null);
    const [files, setFiles] = useState<string[]>([]);
    const [docType, setDocType] = useState<string>("Documentation");
    const [fileContents, setFileContents] = useState<string[]>([]);
    const [filePath, setFilePath] = useState<string>("");
    const [inputFileKey, setInputFileKey] = useState<number>(Date.now());  // Using the current timestamp as the initial key  
    const [apiResponse, setApiResponse] = useState<{ status: number, status_msg: string } | null>(null);

    useEffect(() => {
        // Fetch the list of readers from your API when the component mounts
        const fetchReaders = async () => {
            try {
                const response = await fetch(apiHost + '/api/get_readers');
                const data = await response.json();
                setReaders(data.readers);
                if (data.readers && data.readers.length > 0) {
                    setSelectedReader(data.readers[0]);
                }
            } catch (error) {
                console.error("Error fetching readers:", error);
            }
        }
        fetchReaders();
    }, [apiHost]);

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            const filesArray = Array.from(event.target.files);
            const contents: string[] = [];

            for (const file of filesArray) {
                const content = await file.text();
                contents.push(file.name + "<VERBASPLIT>" + content);
            }

            setFileContents(contents);
        }
    };

    const handleFilePathInput = (event: React.ChangeEvent<HTMLInputElement>) => {
        setFilePath(event.target.value);
    };

    const handleImport = async () => {
        if (!selectedReader) {
            console.error("No reader selected!");
            return;
        }

        let payload;

        if (selectedReader.input_form === 'UPLOAD') {
            payload = {
                reader: selectedReader.name,
                contents: fileContents,
                document_type: docType
            };
        } else {
            payload = {
                reader: selectedReader.name,
                contents: [filePath],
                document_type: docType
            };
        }

        try {
            const response = await fetch(`${apiHost}/api/load_data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok) {
                // Clear files and path after successful import
                setFiles([]);
                setFileContents([]);
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

    return (
        <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center z-50">
            <div className="absolute w-full h-full bg-black opacity-50"></div>
            <div className="bg-gray-200 border-2 border-black lg:w-2/5 md:w-full md:m-3 z-10 rounded-xl shadow-md animate-pop-in">
                <div className="flex justify-start items-center mb-4 p-4">
                    <button onClick={onClose} className="mr-3 bg-red-500 text-white hover:bg-red-600 shadow-md hover-container p-2 rounded-full flex items-center justify-center">
                        <FaTimes />
                    </button>
                    <button onClick={() => setSelectedOption("Reader")} className={`${"Reader" === selectedOption ? 'bg-yellow-200' : 'bg-gray-200'} text-black text-lg rounded-lg font-bold border-2 border-black animate-pop-in-late p-4 w-full hover-container shadow-md mr-6 hover:bg-yellow-300 hover:border-white`}>Reader</button>
                    <button onClick={() => setSelectedOption("Chunking")} className={`${"Chunking" === selectedOption ? 'bg-cyan-200' : 'bg-gray-200'} text-black text-lg rounded-lg font-bold border-2 border-black animate-pop-in-late p-4 w-full hover-container shadow-md mr-6 hover:bg-cyan-300 hover:border-white`}>Chunking</button>
                    <button onClick={() => setSelectedOption("Embedding")} className={`${"Embedding" === selectedOption ? 'bg-fuchsia-200' : 'bg-gray-200'} bg-gray-200 text-black text-lg rounded-lg font-bold border-2 border-black animate-pop-in-late p-4 w-full hover-container shadow-md hover:bg-fuchsia-300 hover:border-white`}>Embedding</button>

                </div>
                <div className="flex p-4">
                    {/* Left column for the list of readers */}
                    <div className="w-2/5 pr-2 border-r border-gray-300 overflow-y-auto">
                        <ul>
                            {readers.map((reader, index) => (
                                <button
                                    onClick={() => setSelectedReader(reader)}
                                    className={`${reader.name === selectedReader?.name ? 'bg-green-300' : 'bg-gray-200'} text-black text-lg truncate rounded-lg font-bold border-2 mb-3 border-black animate-pop-in-late p-4 w-full shadow-md hover:bg-green-400 hover:border-white`}
                                    key={index}
                                    title={reader.name} // hover tooltip in case of truncation
                                >
                                    {reader.name}
                                </button>
                            ))}
                        </ul>
                    </div>
                    {/* Right column for configurations */}
                    <div className="w-3/5 p-4">
                        <div className='mb-6'>
                            {selectedReader && selectedReader.input_form === 'UPLOAD' ? (
                                <div className=''>
                                    <h3 className='mb-2'>Upload documents</h3>
                                    <input
                                        key={inputFileKey}
                                        type="file"
                                        multiple
                                        accept=".txt,.md,.mdx"
                                        onChange={handleFileChange}
                                    />
                                </div>
                            ) : selectedReader && selectedReader.input_form === 'INPUT' ? (
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
                            ) : null}
                        </div>
                        <div className='text-center shadow-md rounded-lg p-4 hover-container overflow-y-auto mb-6'>
                            <p>{selectedReader?.description}</p>
                        </div>
                        <div className="flex justify-end">
                            <button
                                onClick={handleImport} className="flex items-center bg-gray-200 text-black p-3 rounded-lg hover:bg-green-400 border-2 border-black hover:border-white hover-container shadow-md"
                            >

                                <FaPlus />
                                <span>Import</span>
                            </button>
                        </div>
                    </div >
                </div>
                {
                    apiResponse && (
                        <div
                            className={`p-4 rounded-lg shadow-md m-4 animate-pop-in hover-container
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
