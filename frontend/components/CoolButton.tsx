// CoolButton.tsx
import React from 'react';
import { FaCopy } from 'react-icons/fa'; // Importing the React icon from FontAwesome


interface CoolButtonProps {
    main: string;
    sub: string;
    onClick: () => void;
    available?: boolean;
    clipboard: boolean;
    subBgColor?: string; // Optional prop to control the background color of the sub span
    mainBgColor?: string;
    isActive?: boolean; // optional prop for button active state
    title?: string;   // optional prop for hover tooltip
}

const CoolButton: React.FC<CoolButtonProps> = ({ main, sub, onClick, clipboard, available = true, subBgColor = 'green', mainBgColor = 'yellow', isActive = false, title = '' }) => {

    const handleCopyToBillboard = () => {
        navigator.clipboard.writeText(main).then(
            function () {
                console.log('Text successfully copied to clipboard!');
            },
            function (err) {
                console.error('Unable to copy text: ', err);
            }
        );
    };

    return (
        <button
            onClick={onClick}
            title={title}
            disabled={!available}
            className={`relative flex items-center justify-center text-black text-lg mt-4 ${isActive ? `bg-${mainBgColor}-300` : 'bg-gray-300'} rounded-lg font-bold border-2 border-black animate-pop-in-late p-4 w-full shadow-md mr-6 ${isActive ? `hover:bg-${mainBgColor}-400` : 'hover:bg-gray-200'} hover:border-white`}        >
            {clipboard ? <div role="button" onClick={handleCopyToBillboard} className="p-3 rounded cursor-pointer">
                <FaCopy size={20} className="text-gray-400 hover:text-white" />
            </div> : ""}
            <span className="block truncate">{main}</span>
            <span className={`block absolute top-2/3 mt-3 text-sm bg-${subBgColor}-300 rounded-lg px-2 truncate text-xs`}>
                {sub}
            </span>
        </button>
    );
};

export default CoolButton;