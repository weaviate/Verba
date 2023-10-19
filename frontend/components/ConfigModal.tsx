import React, { useState, useEffect } from 'react';
import { TbVectorTriangle } from "react-icons/tb";
import { useDropzone } from 'react-dropzone';
import CoolButton from "../components/CoolButton";
import HashLoader from "react-spinners/HashLoader";
import { Component } from "../components/ImportModalComponent";


interface ConfigModalProps {
    component: string;
    apiHost: string;
}

const ConfigModal: React.FC<ConfigModalProps> = ({ component = "embedders", apiHost }) => {

    const [components, setComponents] = useState<Component[]>([]);
    const [selectedComponent, setSelectedComponent] = useState<Component>();
    const [isListVisible, setListVisible] = useState<boolean>(false);
    const [isTooltipVisible, setTooltipVisible] = useState<boolean>(false);

    const toggleListVisibility = () => {
        setListVisible(prevState => !prevState);
    };

    const handleComponentSelection = async (selectedComponent: Component) => {
        setSelectedComponent(selectedComponent);
        toggleListVisibility()
        try {
            const response = await fetch(`${apiHost}/api/set_component`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "component": component, "selected_component": selectedComponent.name }),
            });
            // Handle the response if necessary
        } catch (error) {
            console.error("Error setting component:", error);
        }
    };


    useEffect(() => {
        // Fetch the list of readers from your API when the component mounts
        const fetchReaders = async () => {
            try {
                const response = await fetch(`${apiHost}/api/get_component`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ "component": component })
                });

                const data = await response.json();
                setSelectedComponent(data.selected_component)
                setComponents(data.components);


            } catch (error) {
                console.error("Error fetching readers:", error);
            }
        }
        fetchReaders();
    }, [apiHost]);

    return (
        <div className="ml-16 animate-pop-in">
            <div className="flex items-center"> {/* Wrapped button and tooltip in flex container */}
                <button
                    onClick={toggleListVisibility}
                    className="flex items-center space-x-2 bg-gray-200 text-black p-3 rounded-lg hover:bg-fuchsia-400 border-2 border-black hover:border-white hover-container shadow-md"
                >
                    <TbVectorTriangle />
                    <span className='truncate'>{selectedComponent?.name ? selectedComponent.name : "None"}</span>
                </button>
                <div className="relative ml-2" onMouseEnter={() => setTooltipVisible(true)}  // Show tooltip on mouse enter
                    onMouseLeave={() => setTooltipVisible(false)} >
                    <button className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 border-2 border-gray-400 hover:border-white hover-container shadow-md">
                        ?
                    </button>
                    {/* Tooltip */}
                    {isTooltipVisible && (
                        <div className="absolute flex transform text-xs mt-2 w-60 bg-gray-200 p-2 rounded-lg shadow-lg text-black z-10">
                            {selectedComponent?.description}
                        </div>
                    )}
                </div>
            </div>
            {
                isListVisible && (
                    <div className="absolute flex p-1 max-h-[50vh] animate-pop-in overflow-y-auto z-10 mt-2 items-center justify-center">
                        <div className="grid grid-rows-1 gap-2">
                            {components.filter(_component => _component.name !== selectedComponent?.name).map(_component => (
                                <button
                                    key={_component.name}
                                    onClick={() => handleComponentSelection(_component)}
                                    className='bg-gray-300 rounded-lg p-2 shadow-md animate-pop-in-late hover-container hover:bg-gray-200 truncate'
                                    disabled={!_component.available}
                                >
                                    <span>{_component.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default ConfigModal;