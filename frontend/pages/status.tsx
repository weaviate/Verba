import { useState, useEffect } from "react";
import CoolButton from "../components/CoolButton";
import { getApiHost } from "@/pages";

export default function StatusPage() {

    const apiHost = getApiHost()
    const bgUrl = process.env.NODE_ENV === 'production'
        ? 'static/'
        : '/';

    // Define states to hold the retrieved values
    const [type, setType] = useState("");
    const [connected, setConnected] = useState("Offline");
    const [libraries, setLibraries] = useState({});
    const [variables, setVariables] = useState({});
    const [schemas, setSchemas] = useState({});
    const [showModal, setShowModal] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const handleReset = () => {
        setIsLoading(true); // Start loading
        fetch(apiHost + "/api/reset")
            .then(response => response.json())
            .then(data => {
                console.log('Reset successful:', data);
                setShowModal(false);
                setIsLoading(false);
                window.location.reload();  // Refresh page
            })
            .catch(error => {
                console.error('Error during reset:', error);
                setIsLoading(false); // Stop loading if there's an error
            });
    };


    useEffect(() => {
        fetch(apiHost + "/api/get_status")
            .then(response => response.json())
            .then(data => {
                setType(data.type);
                setLibraries(data.libraries);
                setVariables(data.variables);
                setSchemas(data.schemas)
                setConnected("Online")
            })
            .catch(error => {
                console.error("Error fetching the data:", error);
            });
    }, []);

    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-10 text-gray-900">
            <div className="flex flex-col w-full items-start">
                <div className="mb-2">
                    <div className="flex justify-between items-center w-full"> {/* <-- flexbox container */}
                        <div className="flex-none">
                            <div className="bg-yellow-200 border-2 border-gray-800 rounded-lg shadow-lg animate-pop-in hover-container mr-4 ">
                                <img src={`${bgUrl}verba.png`} alt="Verba Logo" className=" w-24 h-24 shadow-lg" />
                            </div>
                        </div>
                        <div className="flex-1">
                            <h1 className=" text-6xl font-bold">Verba</h1>
                            <div className="flex text-lg">
                                <span className="bg-opacity-0 rounded px-2 py-1 hover-container animate-pop-in">
                                    The
                                </span>
                                <span className="bg-opacity-0 rounded font-bold px-2 py-1 hover-container animate-pop-in-late">
                                    Golden
                                </span>
                                <span className="bg-yellow-200 rounded px-2 py-1 hover-container animate-pop-more-late">
                                    RAGtriever
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="flex mt-16 space-x-4 w-full justify-center items-start"> {/* Adjusted container for the three sections */}
                    {/* First Section */}
                    <div className="flex-1 border-2 border-black bg-white bg-opacity-20 rounded-lg shadow-md backdrop-filter max-h-[50vh] backdrop-blur-md p-4 w-full overflow-y-auto animate-pop-in">
                        <h2 className="text-lg font-bold mb-4">🐕 Verba Status</h2>
                        <p className="text-xs font-bold mb-4 text-gray-600">This view shows whether your Verba Client is connected to the Backend and which Deployment of Weaviate you are using</p>
                        <hr></hr>
                        <div className="grid grid-rows-2 gap-2 mt-4">
                            <CoolButton main="Backend" sub={connected} clipboard={connected == "Online" ? true : false} subBgColor={connected == "Online" ? 'green' : 'red'} onClick={() => console.log("Connected button clicked")} />
                            <CoolButton main={type ? type : "Weaviate"} sub={connected} clipboard={connected == "Online" ? true : false} subBgColor={connected == "Online" ? 'green' : 'red'} onClick={() => console.log("Type button clicked")} />
                        </div>
                    </div>
                    {/* Second Section */}
                    <div className="flex-1 border-2 border-black bg-white bg-opacity-20 rounded-lg shadow-md backdrop-filter max-h-[50vh] backdrop-blur-md p-4 overflow-y-auto w-full animate-pop-in">
                        <h2 className="text-lg font-bold mb-4">📚 Libraries & Variables</h2>
                        <p className="text-xs font-bold mb-4 text-gray-600">This view shows the available libraries and set variables</p>
                        <hr />
                        <div className="grid grid-rows-2 gap-2 mt-4">
                            {Object.entries(libraries).map(([key, value]) => (
                                <CoolButton
                                    clipboard={true}
                                    key={key}
                                    main={key}
                                    subBgColor={value ? 'green' : 'red'}
                                    sub={value ? 'Library Installed' : 'Library not installed'}
                                    onClick={() => console.log(`${key} button clicked`)}
                                />
                            ))}
                            {Object.entries(variables).map(([key, value]) => (
                                <CoolButton
                                    clipboard={true}
                                    key={key}
                                    main={key}
                                    subBgColor={value ? 'green' : 'red'}
                                    sub={value ? 'Variable Available' : 'Variable not set'}
                                    onClick={() => console.log(`${key} button clicked`)}
                                />
                            ))}
                        </div>
                    </div>
                    {/* Third Section */}
                    <div className="flex-1 bg-white border-2 border-black bg-opacity-20 rounded-lg shadow-md backdrop-filter max-h-[50vh] backdrop-blur-md p-4 w-full overflow-y-auto animate-pop-in">
                        <div className="flex justify-between items-center mb-4"> {/* Container for the title and button */}
                            <h2 className="text-lg font-bold">📝 Schemas & Objects</h2>
                            <button onClick={() => setShowModal(true)} className="text-xs bg-gray-400 text-white hover:bg-red-400 hover-container px-3 py-2 rounded-lg">
                                ❌ Reset Verba
                            </button>
                        </div>
                        <p className="text-xs font-bold mb-4 text-gray-600">This view shows all schemas and their object count</p>
                        <hr />
                        <div className="grid grid-rows-2 gap-2 mt-4">
                            {Object.entries(schemas).map(([key, value]) => (
                                <CoolButton
                                    clipboard={true}
                                    key={key}
                                    main={key}
                                    subBgColor={'yellow'}
                                    sub={value + ' objects'}
                                    onClick={() => console.log(`${key} button clicked`)}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
            {showModal && (
                <div className="fixed inset-0 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-black animate-pop-in">
                        <h3 className="font-bold mb-4">⚠️ Warning</h3>
                        <p>Are you sure? This will remove all existing data.</p>
                        <div className="flex justify-end mt-4">
                            <button onClick={() => setShowModal(false)} className="mr-2 px-4 py-2 bg-gray-300 hover:bg-gray-200 rounded">
                                No
                            </button>
                            <button onClick={handleReset} className="px-4 py-2 bg-red-500 hover:bg-red-400 text-white rounded">
                                {isLoading ? "Resetting..." : "Yes"} {/* Show spinner if loading, otherwise show "Yes" */}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}