import { useState, useEffect, useRef } from "react";
import Typewriter from "typewriter-effect";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import PulseLoader from "react-spinners/PulseLoader";

interface ChatComponentProps {
  onUserMessageSubmit: Message[];
  isFetching: boolean;
}

export interface Message {
  type: "user" | "system";
  content: string;
}

export function ChatComponent({
  onUserMessageSubmit,
  isFetching,
}: ChatComponentProps) {
  const [messageHistory, setMessageHistory] = useState<Message[]>([]);
  const lastMessageRef = useRef<null | HTMLDivElement>(null);

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
    <div className="bg-gray-100 p-4 overflow-y-auto h-[350px]">
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
