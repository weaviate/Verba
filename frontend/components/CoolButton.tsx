// CoolButton.tsx
import React from 'react';

interface CoolButtonProps {
    main: string;
    sub: string;
    onClick: () => void;
    subBgColor?: string; // Optional prop to control the background color of the sub span
}

const CoolButton: React.FC<CoolButtonProps> = ({ main, sub, onClick, subBgColor = 'green' }) => {
    return (
        <button onClick={onClick} className={`relative flex items-center justify-center text-black text-lg mt-2 bg-gray-300 rounded-lg font-bold border-2 border-black animate-pop-in-late p-4 w-full hover-container shadow-md mr-6 hover:bg-gray-200 hover:border-white`}>
            <span className="block truncate">{main}</span>
            <span className={`block absolute top-2/3 mt-3 text-sm bg-${subBgColor}-300 rounded-lg px-2 truncate`}>
                {sub}
            </span>
        </button>
    );
};

export default CoolButton;