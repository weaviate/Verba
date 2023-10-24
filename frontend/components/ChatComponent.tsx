import { useState, useEffect, useRef } from "react";
import Typewriter from "typewriter-effect";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import PulseLoader from "react-spinners/PulseLoader";

interface ChatComponentProps {
  onUserMessageSubmit: Message[];
  isFetching: boolean;
  setHandleGenerateStreamMessageRef: (ref: React.MutableRefObject<Function | null>) => void;
  apiHost: string;
}

export interface Message {
  type: "user" | "system";
  content: string;
}

export function ChatComponent({
  onUserMessageSubmit,
  isFetching,
  setHandleGenerateStreamMessageRef,
  apiHost,
}: ChatComponentProps) {
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const lastMessageRef = useRef<null | HTMLDivElement>(null);
  const [accumulatingMessage, setAccumulatingMessage] = useState<string>("");
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const handleGenerateStreamMessageRef = useRef<Function | null>(null);

  useEffect(() => {
    // Pass the ref up to the parent
    setHandleGenerateStreamMessageRef(handleGenerateStreamMessageRef);
  }, [setHandleGenerateStreamMessageRef]);

  useEffect(() => {
    const localSocket = new WebSocket("ws://" + apiHost + '/ws/generate_stream');

    localSocket.onopen = () => {
      console.log("WebSocket connection opened.");
    };

    localSocket.onmessage = (event) => {
      console.log(event.data)
      const data = event.data;
      // Depending on the structure of your server response, 
      // you might need to extract the message differently.
      const newMessage = data.message;
      console.log(accumulatingMessage)
      setAccumulatingMessage(prev => prev + newMessage);

      // If the message is complete, add it to messageHistory
      if (data.finish_reason === "stop") {
        setMessageHistory(prev => [...prev, { type: "system", content: accumulatingMessage }]);
        setAccumulatingMessage(""); // Reset accumulating message
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
          <span
            className={`inline-block p-3 rounded-xl animate-press-in shadow-md font-mono text-sm ${message.type === "user" ? "bg-yellow-200" : "bg-white"
              }`}
          >
            {message.type === "system"
              ? parseMessage(message.content).map((segment, segIndex) => {
                if (segment.type === "text") {
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
      {isFetching && (
        <div className="flex items-center pl-4 mb-4">
          <PulseLoader color={"#292929"} loading={true} size={10} speedMultiplier={0.75} />
        </div>
      )}
    </div>
  );
}
