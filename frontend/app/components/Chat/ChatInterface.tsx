"use client";

import React, { useState, useEffect, useRef } from "react";
import InfoComponent from "../Navigation/InfoComponent";
import { SettingsConfiguration } from "../Settings/types";
import { IoMdAddCircle } from "react-icons/io";
import { FaFileImport } from "react-icons/fa";
import { MdCancel } from "react-icons/md";
import { GoFileDirectoryFill } from "react-icons/go";
import { TbPlugConnected } from "react-icons/tb";
import { IoChatbubbleSharp } from "react-icons/io5";
import { FaHammer } from "react-icons/fa";
import { MdOutlineRefresh } from "react-icons/md";
import { IoIosSend } from "react-icons/io";
import { BiError } from "react-icons/bi";

import { getWebSocketApiHost } from "./util";

import { QueryPayload, DataCountPayload, ChunkScore } from "./types";

import ChatConfig from "./ChatConfig";
import ChatMessage from "./ChatMessage";
import { Message } from "./types";

import UserModalComponent from "../Navigation/UserModal";

import { RAGConfig } from "../RAG/types";

interface ChatInterfaceProps {
  APIHost: string | null;
  settingConfig: SettingsConfiguration;
  RAGConfig: RAGConfig | null;
  selectedDocument: string | null;
  setSelectedDocument: (s: string | null) => void;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  setSelectedChunkScore: (c: ChunkScore[]) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  APIHost,
  settingConfig,
  RAGConfig,
  setRAGConfig,
  selectedDocument,
  setSelectedDocument,
  setSelectedChunkScore,
}) => {
  const [selectedSetting, setSelectedSetting] = useState("Chat");

  const isFetching = useRef<boolean>(false);
  const [fetchingStatus, setFetchingStatus] = useState<
    "DONE" | "CHUNKS" | "RESPONSE"
  >("DONE");

  const [previewText, setPreviewText] = useState("");
  const lastMessageRef = useRef<null | HTMLDivElement>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [socketOnline, setSocketOnline] = useState(false);
  const [reconnect, setReconnect] = useState(false);

  const [context, setContext] = useState("");

  const [selectedDocumentScore, setSelectedDocumentScore] = useState<
    string | null
  >(null);

  const [currentDatacount, setCurrentDatacount] = useState(0);

  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  const currentEmbeddingModel = RAGConfig
    ? RAGConfig["Embedder"].components[RAGConfig["Embedder"].selected].config[
        "Model"
      ].value
    : "No Embedding Model";

  const sendUserMessage = async () => {
    if (isFetching.current || APIHost === null) {
      return;
    }

    const sendInput = userInput;
    setUserInput("");

    if (sendInput.trim()) {
      try {
        isFetching.current = true;
        setFetchingStatus("CHUNKS");
        setMessages((prev) => [...prev, { type: "user", content: sendInput }]);

        const response = await fetch(APIHost + "/api/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: sendInput,
            config: { RAG: RAGConfig, SETTING: settingConfig },
          }),
        });
        const data: QueryPayload = await response.json();

        if (data.error != "") {
          setMessages((prev) => [
            ...prev,
            { type: "error", content: data.error },
          ]);
          isFetching.current = false;
          setFetchingStatus("DONE");
        } else {
          setMessages((prev) => [
            ...prev,
            { type: "retrieval", content: data.documents },
          ]);
          if (data.documents.length > 0) {
            setSelectedDocument(data.documents[0].uuid);
            setSelectedDocumentScore(
              data.documents[0].uuid +
                data.documents[0].score +
                data.documents[0].chunks.length
            );
            setSelectedChunkScore(data.documents[0].chunks);

            {
              /* Send WebSocket Message to generate answer based on context */
            }

            if (data.context) {
              streamResponses(sendInput, data.context);
              setContext(data.context);
              setFetchingStatus("RESPONSE");
            }
          }
        }
      } catch (error) {
        console.error("Failed to fetch from API:", error);
        setMessages((prev) => [
          ...prev,
          { type: "error", content: "Failed to fetch from API" },
        ]);
        isFetching.current = false;
        setFetchingStatus("DONE");
      }
    }
  };

  const streamResponses = (query?: string, context?: string) => {
    if (socket?.readyState === WebSocket.OPEN) {
      const filteredMessages = messages
        .filter((msg) => msg.type === "user" || msg.type === "system")
        .map((msg) => ({
          type: msg.type,
          content: msg.content,
        }));

      const data = JSON.stringify({
        query: query,
        context: context,
        conversation: filteredMessages,
        rag_config: RAGConfig,
      });
      socket.send(data);
    } else {
      console.error("WebSocket is not open. ReadyState:", socket?.readyState);
    }
  };

  const handleKeyDown = (e: any) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      sendUserMessage(); // Submit form
    }
  };

  const retrieveDatacount = async () => {
    try {
      const embedding_model = RAGConfig
        ? RAGConfig["Embedder"].components[RAGConfig["Embedder"].selected]
            .config["Model"].value
        : "No Embedding Model";
      const response = await fetch(APIHost + "/api/get_datacount", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ embedding_model: embedding_model }),
      });
      const data: DataCountPayload = await response.json();

      if (data) {
        setCurrentDatacount(data.datacount);
      }
    } catch (error) {
      console.error("Failed to fetch from API:", error);
    }
  };

  const reconnectToVerba = () => {
    setReconnect((prevState) => !prevState);
  };

  useEffect(() => {
    setReconnect(true);
  }, []);

  useEffect(() => {
    if (RAGConfig) {
      retrieveDatacount();
    } else {
      setCurrentDatacount(0);
    }
  }, [currentEmbeddingModel]);

  // Setup WebSocket and messages to /ws/generate_stream
  useEffect(() => {
    const socketHost = getWebSocketApiHost();
    const localSocket = new WebSocket(socketHost);

    localSocket.onopen = () => {
      console.log("WebSocket connection opened to " + socketHost);
      setSocketOnline(true);
    };

    localSocket.onmessage = (event) => {
      let data;

      if (!isFetching.current) {
        setPreviewText("");
        return;
      }

      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error("Received data is not valid JSON:", event.data);
        return; // Exit early if data isn't valid JSON
      }
      const newMessageContent = data.message;
      setPreviewText((prev) => prev + newMessageContent);

      if (data.finish_reason === "stop") {
        isFetching.current = false;
        setFetchingStatus("DONE");
        const full_text = data.full_text;
        if (data.cached) {
          const distance = data.distance;
          setMessages((prev) => [
            ...prev,
            {
              type: "system",
              content: full_text,
              cached: true,
              distance: distance,
            },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            { type: "system", content: full_text },
          ]);
        }
        setPreviewText("");
      }
    };

    localSocket.onerror = (error) => {
      console.error("WebSocket Error:", error);
      setSocketOnline(false);
      isFetching.current = false;
      setFetchingStatus("DONE");
    };

    localSocket.onclose = (event) => {
      if (event.wasClean) {
        console.log(
          `WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`
        );
      } else {
        console.error("WebSocket connection died");
      }
      setSocketOnline(false);
      isFetching.current = false;
      setFetchingStatus("DONE");
    };

    setSocket(localSocket);

    return () => {
      if (localSocket.readyState !== WebSocket.CLOSED) {
        localSocket.close();
      }
    };
  }, [reconnect]);

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-between h-min w-full">
        <div className="flex gap-2 justify-start items-center">
          <InfoComponent
            settingConfig={settingConfig}
            tooltip_text="Use the Chat interface to interact with your data and to perform Retrieval Augmented Generation (RAG)"
            display_text={"Chat"}
          />
        </div>
        <div className="flex gap-3 justify-end">
          <button
            onClick={() => {
              setSelectedSetting("Chat");
            }}
            className={`flex ${selectedSetting === "Chat" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <IoChatbubbleSharp size={15} />
            <p>Chat</p>
          </button>

          <button
            onClick={() => {
              setSelectedSetting("Config");
            }}
            className={`flex ${selectedSetting === "Config" ? "bg-primary-verba hover:bg-button-hover-verba" : "bg-button-verba hover:bg-button-hover-verba"} border-none btn text-text-verba gap-2`}
          >
            <FaHammer size={15} />
            <p>Config</p>
          </button>
        </div>
      </div>

      <div className="bg-bg-alt-verba rounded-2xl flex flex-col p-6 h-full w-full overflow-y-auto overflow-x-hidden">
        <div
          className={`flex flex-col gap-3 ${selectedSetting === "Chat" ? "flex flex-col gap-3 " : "hidden"}`}
        >
          <div className="flex w-full justify-start items-center text-text-alt-verba gap-2">
            {currentDatacount === 0 && <BiError size={15} />}
            {currentDatacount === 0 && (
              <p className="text-text-alt-verba text-sm items-center flex">{`${currentDatacount} documents embedded by ${currentEmbeddingModel}`}</p>
            )}
          </div>
          {messages.map((message, index) => (
            <div
              key={"Message_" + index}
              className={`${message.type === "user" ? "text-right" : ""}`}
            >
              <ChatMessage
                message={message}
                message_index={index}
                settingConfig={settingConfig}
                selectedDocument={selectedDocumentScore}
                setSelectedDocumentScore={setSelectedDocumentScore}
                setSelectedDocument={setSelectedDocument}
                setSelectedChunkScore={setSelectedChunkScore}
              />
            </div>
          ))}
          {previewText && (
            <ChatMessage
              message={{ type: "system", content: previewText, cached: false }}
              message_index={-1}
              settingConfig={settingConfig}
              selectedDocument={selectedDocumentScore}
              setSelectedDocumentScore={setSelectedDocumentScore}
              setSelectedDocument={setSelectedDocument}
              setSelectedChunkScore={setSelectedChunkScore}
            />
          )}
          {isFetching.current && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-3">
                <span className="text-text-alt-verba loading loading-dots loading-md"></span>
                <p className="text-text-alt-verba">
                  {fetchingStatus === "CHUNKS" && "Retrieving..."}
                  {fetchingStatus === "RESPONSE" && "Generating..."}
                </p>
                <button className="btn btn-circle btn-sm bg-bg-alt-verba hover:bg-warning-verba hover:text-text-verba text-text-alt-verba shadow-none border-none text-sm">
                  <MdCancel size={15} />
                </button>
              </div>
            </div>
          )}
        </div>
        {selectedSetting === "Config" && (
          <ChatConfig RAGConfig={RAGConfig} setRAGConfig={setRAGConfig} />
        )}
      </div>

      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        {socketOnline ? (
          <div className="flex gap-2 items-center justify-end w-full">
            <label className="input flex items-center gap-2 w-full bg-bg-verba">
              <input
                type="text"
                className="grow w-full"
                placeholder={
                  currentDatacount > 0
                    ? `Chatting with ${currentDatacount} documents...`
                    : `No documents detected...`
                }
                onKeyDown={handleKeyDown}
                value={userInput}
                onChange={(e) => {
                  setUserInput(e.target.value);
                }}
              />
            </label>

            <button
              type="button"
              onClick={(e) => {
                sendUserMessage();
              }}
              className="btn btn-square border-none bg-primary-verba hover:bg-button-hover-verba"
            >
              <IoIosSend size={15} />
            </button>

            <button
              type="button"
              onClick={() => {
                setMessages([]);
                setSelectedDocument(null);
                setSelectedChunkScore([]);
                setSelectedDocumentScore(null);
              }}
              className="btn btn-square border-none bg-button-verba hover:bg-button-hover-verba"
            >
              <MdOutlineRefresh size={18} />
            </button>
          </div>
        ) : (
          <div className="flex gap-2 items-center justify-end w-full">
            <button
              onClick={reconnectToVerba}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2"
            >
              <TbPlugConnected size={15} />
              <p>Reconnect to Verba</p>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
