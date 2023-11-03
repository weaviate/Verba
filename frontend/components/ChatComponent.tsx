import { useState, useEffect, useRef } from "react";
import Typewriter from "typewriter-effect";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import PulseLoader from "react-spinners/PulseLoader";
import { FaCopy } from 'react-icons/fa';
import { BsDatabaseFillCheck } from 'react-icons/bs';

interface ChatComponentProps {
  onUserMessageSubmit: Message[];
  isFetching: boolean;
  setHandleGenerateStreamMessageRef: (ref: React.MutableRefObject<Function | null>) => void;
  apiHost: string;
}

export interface Message {
  type: "user" | "system";
  content: string;
  typewriter: boolean;
  cached?: boolean;
  distance?: string;
}

export function ChatComponent({
  onUserMessageSubmit,
  isFetching,
  setHandleGenerateStreamMessageRef,
  apiHost,
}: ChatComponentProps) {
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const lastMessageRef = useRef<null | HTMLDivElement>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const handleGenerateStreamMessageRef = useRef<Function | null>(null);
  const [previewMessage, setPreviewMessage] = useState("");
  const [showNotification, setShowNotification] = useState(false);

  const getWebSocketApiHost = () => {
    if (process.env.NODE_ENV === 'development') {
      return 'ws://localhost:8000/ws/generate_stream';
    }

    // If you're serving the app directly through FastAPI, generate the WebSocket URL based on the current location.
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/ws/generate_stream`;
  };

  const handleCopyToBillboard = (text: string) => {
    navigator.clipboard.writeText(text).then(
      function () {
        console.log('Text successfully copied to clipboard!');

        // Show the notification
        setShowNotification(true);

        // Hide the notification after 3 seconds
        setTimeout(() => {
          setShowNotification(false);
        }, 3000);
      },
      function (err) {
        console.error('Unable to copy text: ', err);
      }
    );
  };


  useEffect(() => {
    // Pass the ref up to the parent
    setHandleGenerateStreamMessageRef(handleGenerateStreamMessageRef);
  }, [setHandleGenerateStreamMessageRef]);

  useEffect(() => {
    const localSocket = new WebSocket(getWebSocketApiHost());

    localSocket.onopen = () => {
      console.log("WebSocket connection opened.");
    };

    localSocket.onmessage = (event) => {
      let data;

      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error("Received data is not valid JSON:", event.data);
        return; // Exit early if data isn't valid JSON
      }
      const newMessageContent = data.message;
      setPreviewMessage(prev => prev + newMessageContent);

      if (data.finish_reason === "stop") {
        const full_text = data.full_text
        if (data.cached) {
          const distance = data.distance
          setMessageHistory(prev => [...prev, { type: "system", content: full_text, typewriter: false, cached: true, distance: distance }]);
        } else {
          setMessageHistory(prev => [...prev, { type: "system", content: full_text, typewriter: false }]);
        }
        setPreviewMessage("");  // Reset for the next message
      }
    };

    localSocket.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    localSocket.onclose = (event) => {
      if (event.wasClean) {
        console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
      } else {
        console.error("WebSocket connection died");
      }
    };

    setSocket(localSocket);

    return () => {
      if (localSocket.readyState !== WebSocket.CLOSED) {
        localSocket.close();
      }
    };
  }, []);


  handleGenerateStreamMessageRef.current = (query?: string, context?: string) => {
    if (socket?.readyState === WebSocket.OPEN) {
      console.log(messageHistory)
      const data = JSON.stringify({ query: query, context: context, conversation: messageHistory });
      socket.send(data);
    } else {
      console.error("WebSocket is not open. ReadyState:", socket?.readyState);
    }
  };

  type Segment =
    | { type: "text"; content: string }
    | { type: "code"; language: string; content: string };

  // Helper function to parse message into segments
  const parseMessage = (content: string) => {
    const regex = /```(.*?)\n([\s\S]*?)```/g; // Matches code blocks and the specified language
    const segments: Segment[] = [];
    let lastEndIndex = 0;

    content.replace(regex, (match, language, codeContent, index) => {
      if (index > lastEndIndex) {
        segments.push({
          type: "text",
          content: content.slice(lastEndIndex, index),
        });
      }

      segments.push({
        type: "code",
        language: language.trim(),
        content: codeContent.trim(),
      });
      lastEndIndex = index + match.length;
      return match;
    });

    if (lastEndIndex < content.length) {
      segments.push({ type: "text", content: content.slice(lastEndIndex) });
    }

    return segments;
  };

  useEffect(() => {
    if (
      onUserMessageSubmit.length &&
      (messageHistory.length === 0 ||
        onUserMessageSubmit[onUserMessageSubmit.length - 1].content !==
        messageHistory[messageHistory.length - 1].content)
    ) {
      const newMessage = onUserMessageSubmit[onUserMessageSubmit.length - 1];
      setMessageHistory((prev) => [...prev, newMessage]);
    }
  }, [onUserMessageSubmit]);

  useEffect(() => {
    if (lastMessageRef.current) {
      const lastMessage = messageHistory[messageHistory.length - 1];

      // If it's a system message with the Typewriter effect
      if (lastMessage.type === "system") {
        // Calculate the delay needed based on the message length and Typewriter delay
        const delay = lastMessage.content.length * 25;
        setTimeout(() => {
          lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
        }, delay);
      } else {
        lastMessageRef.current.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messageHistory]);

  return (
    <div className="bg-gray-100 p-4 overflow-y-auto h-[35vh]">
      {messageHistory.map((message, index) => (
        <div
          ref={index === messageHistory.length - 1 ? lastMessageRef : null}
          key={index}
          className={`mb-4 ${message.type === "user" ? "text-right" : ""}`}
        >
          <div className="flex">
            {message.type === "system" && (<button
              onClick={() => handleCopyToBillboard(message.content)}
              className={`rounded-md flex py-2 px-3 bg-gray-200 text-black hover-container mb-1 hover:bg-green-300`}
            >
              <FaCopy size={15} />
              <span className="text-xs ml-2">
                Copy
              </span>
            </button>)}
            {message.type === "system" && message.cached && (<button
              className={`rounded-md flex ml-2 py-2 px-3 bg-gray-200 text-black hover-container mb-1 hover:bg-green-300`}
            >
              <BsDatabaseFillCheck size={15} />
              <span className="text-xs ml-2">
                Cached ({message.distance})
              </span>
            </button>)}
          </div>
          <span
            className={`inline-block p-3 rounded-xl animate-press-in shadow-md font-mono text-sm ${message.type === "user" ? "bg-yellow-200" : "bg-white"
              }`}
          >
            {message.type === "system"
              ? parseMessage(message.content).map((segment, segIndex) => {
                if (segment.type === "text" && message.typewriter) {
                  return (
                    <Typewriter
                      key={segIndex}
                      onInit={(typewriter) => {
                        typewriter
                          .typeString(segment.content || "N/A")
                          .start();
                      }}
                      options={{ delay: 15 }}
                    />
                  );
                } else if (segment.type === "text" && !message.typewriter) {
                  return (
                    <p key={segIndex}>{segment.content}</p>
                  );
                } else if (segment.type === "code") {
                  return (
                    <SyntaxHighlighter
                      key={segIndex}
                      language={segment.language}
                      style={oneLight}
                      className="rounded p-2"
                    >
                      {segment.content}
                    </SyntaxHighlighter>
                  );
                }
                return null;
              })
              : message.content}
          </span>
        </div>
      ))}

      {/* Render the preview message if available */}
      {previewMessage && (
        <div className="mb-4">
          <span className="inline-block p-3 rounded-xl animate-press-in shadow-md font-mono text-sm bg-white">
            {parseMessage(previewMessage).map((segment, segIndex) => {
              if (segment.type === "text") {
                return (
                  <p key={segIndex}>{segment.content}</p>
                );
              } else if (segment.type === "code") {
                return (
                  <SyntaxHighlighter key={segIndex} language={segment.language} style={oneLight} className="rounded p-2">
                    {segment.content}
                  </SyntaxHighlighter>
                );
              }
              return null;
            })}
          </span>
        </div>
      )}

      {isFetching && (
        <div className="flex items-center pl-4 mb-4">
          <PulseLoader color={"#292929"} loading={true} size={10} speedMultiplier={0.75} />
        </div>
      )}
      {showNotification && (
        <div className="fixed bottom-5 left-5 animate-pop-in bg-green-500 text-white px-4 py-2 rounded text-sm shadow-md mt-4 mr-4 transition-opacity opacity-100">
          Text copied!
        </div>
      )}
    </div>
  );
}
