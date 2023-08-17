import { useState, useEffect, useRef } from 'react';
import Typewriter from 'typewriter-effect';

interface ChatComponentProps {
    onUserMessageSubmit: Message[];
}

export interface Message {
    type: 'user' | 'system';
    content: string;
}

export function ChatComponent({ onUserMessageSubmit }: ChatComponentProps) {
    const [messageHistory, setMessageHistory] = useState<Message[]>([]);
    const lastMessageRef = useRef<null | HTMLDivElement>(null);

    useEffect(() => {
        if (onUserMessageSubmit.length && (messageHistory.length === 0 || onUserMessageSubmit[onUserMessageSubmit.length - 1].content !== messageHistory[messageHistory.length - 1].content)) {
            const newMessage = onUserMessageSubmit[onUserMessageSubmit.length - 1];
            setMessageHistory(prev => [...prev, newMessage]);
        }
    }, [onUserMessageSubmit]);

    useEffect(() => {
        if (lastMessageRef.current) {
            lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messageHistory]);

    return (
        <div className="bg-gray-100 p-4 overflow-y-auto h-80">
            {messageHistory.map((message, index) => (
                <div
                    ref={index === messageHistory.length - 1 ? lastMessageRef : null}
                    key={index}
                    className={`mb-4 ${message.type === 'user' ? 'text-right' : ''}`}>
                    <span className={`inline-block p-3 rounded-xl animate-press-in shadow-md ${message.type === 'user' ? 'bg-yellow-200' : 'bg-white'}`}>
                        {message.type === 'system' ?
                            <Typewriter
                                onInit={(typewriter) => {
                                    typewriter
                                        .typeString(message.content || 'N/A')
                                        .start();
                                }}
                                options={{ delay: 25 }}
                            />

                            :
                            message.content
                        }
                    </span>
                </div>
            ))}
        </div>
    );
}
