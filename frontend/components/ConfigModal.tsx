import React, { useState, useEffect } from 'react';
import { TbVectorTriangle } from "react-icons/tb";
import { LuFileOutput } from "react-icons/lu";
import { MdOutlineQuestionAnswer } from "react-icons/md";
import { Component } from "../components/ImportModalComponent";


interface ConfigModalProps {
    component: string;
    apiHost: string;
    production: boolean;
    onGeneratorSelect: (streamable: boolean) => void;
}

const ConfigModal: React.FC<ConfigModalProps> = ({ component = "embedders", apiHost, onGeneratorSelect, production }) => {

    const [components, setComponents] = useState<Component[]>([]);
    const [selectedComponent, setSelectedComponent] = useState<Component>();
    const [isListVisible, setListVisible] = useState<boolean>(false);
    const [isTooltipVisible, setTooltipVisible] = useState<boolean>(false);

    const mainButtonRef = React.useRef<HTMLButtonElement | null>(null);

    const toggleListVisibility = () => {
        setListVisible(prevState => !prevState);
    };

    const handleComponentSelection = async (selectedComponent: Component) => {
        if (production == true) {
            return
        }
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
        if (component === "generators") {
            onGeneratorSelect(selectedComponent?.streamable ? selectedComponent.streamable : false);
        }
    }, [selectedComponent]);

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
        <div className="ml-5 animate-pop-in">
            <div className="flex items-center"> {/* Wrapped button and tooltip in flex container */}
                <button
                    ref={mainButtonRef}
                    onClick={toggleListVisibility}
                    className={`flex items-center md:w-44 sm:w-32 space-x-2 bg-gray-200 text-black p-3 rounded-lg ${component === "embedders" ? 'hover:bg-fuchsia-300' : component === "retrievers" ? 'hover:bg-indigo-300' : component === "component" ? 'hover:bg-lime-400' : 'hover:bg-lime-400'} border-2 border-black hover:border-white hover-container shadow-md`}
                >
                    {
                        component === "embedders" ? <TbVectorTriangle /> :
                            component === "retrievers" ? <LuFileOutput /> :
                                component === "generators" ? <MdOutlineQuestionAnswer /> :
                                    <TbVectorTriangle />
                    }
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
                                    style={{ width: mainButtonRef.current ? `${mainButtonRef.current.offsetWidth}px` : 'auto' }}
                                    onClick={() => handleComponentSelection(_component)}
                                    className={`bg-gray-300 rounded-lg p-2 shadow-md animate-pop-in-late hover-container ${_component.available ? 'bg-gray-300 hover:bg-green-200' : 'bg-red-300 hover:bg-red-200'} truncate`}
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