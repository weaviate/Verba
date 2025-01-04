"use client";

import React, { useState, useEffect, useRef } from "react";
import { MdCancel, MdOutlineRefresh } from "react-icons/md";
import { TbPlugConnected } from "react-icons/tb";
import { IoChatbubbleSharp } from "react-icons/io5";
import { FaHammer } from "react-icons/fa";
import { IoIosSend } from "react-icons/io";
import { BiError } from "react-icons/bi";
import { IoMdAddCircle } from "react-icons/io";
import VerbaButton from "../Navigation/VerbaButton";

import {
  updateRAGConfig,
  sendUserQuery,
  fetchDatacount,
  fetchRAGConfig,
  fetchSuggestions,
  fetchLabels,
} from "@/app/api";
import { getWebSocketApiHost } from "@/app/util";
import {
  Credentials,
  QueryPayload,
  Suggestion,
  DataCountPayload,
  ChunkScore,
  Message,
  LabelsResponse,
  RAGConfig,
  Theme,
  DocumentFilter,
} from "@/app/types";

import InfoComponent from "../Navigation/InfoComponent";
import ChatConfig from "./ChatConfig";
import ChatMessage from "./ChatMessage";

interface ChatInterfaceProps {
  credentials: Credentials;
  setSelectedDocument: (s: string | null) => void;
  setSelectedChunkScore: (c: ChunkScore[]) => void;
  currentPage: string;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  selectedTheme: Theme;
  production: "Local" | "Demo" | "Production";
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
  documentFilter: DocumentFilter[];
  setDocumentFilter: React.Dispatch<React.SetStateAction<DocumentFilter[]>>;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  production,
  credentials,
  setSelectedDocument,
  setSelectedChunkScore,
  currentPage,
  RAGConfig,
  selectedTheme,
  setRAGConfig,
  addStatusMessage,
  documentFilter,
  setDocumentFilter,
}) => {
  const [selectedSetting, setSelectedSetting] = useState("Chat");

  const isFetching = useRef<boolean>(false);
  const [fetchingStatus, setFetchingStatus] = useState<
    "DONE" | "CHUNKS" | "RESPONSE"
  >("DONE");

  const [previewText, setPreviewText] = useState("");
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [socketOnline, setSocketOnline] = useState(false);
  const [reconnect, setReconnect] = useState(false);

  const [currentSuggestions, setCurrentSuggestions] = useState<Suggestion[]>(
    []
  );

  const [labels, setLabels] = useState<string[]>([]);
  const [filterLabels, setFilterLabels] = useState<string[]>([]);

  const [selectedDocumentScore, setSelectedDocumentScore] = useState<
    string | null
  >(null);

  const [currentDatacount, setCurrentDatacount] = useState(0);

  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isComposing, setIsComposing] = useState(false);

  const currentEmbedding = RAGConfig
    ? (RAGConfig["Embedder"].components[RAGConfig["Embedder"].selected].config[
        "Model"
      ].value as string)
    : "No Config found";
  useState("No Embedding Model");

  useEffect(() => {
    setReconnect(true);
  }, []);

  useEffect(() => {
    if (RAGConfig) {
      retrieveDatacount();
    } else {
      setCurrentDatacount(0);
    }
  }, [currentEmbedding, currentPage, documentFilter]);

  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 0) {
        return [
          {
            type: "system",
            content: selectedTheme.intro_message.text,
          },
        ];
      }
      return prev;
    });
  }, [selectedTheme.intro_message.text]);

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
        addStatusMessage("Finished generation", "SUCCESS");
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
      setReconnect((prev) => !prev);
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
      setReconnect((prev) => !prev);
    };

    setSocket(localSocket);

    return () => {
      if (localSocket.readyState !== WebSocket.CLOSED) {
        localSocket.close();
      }
    };
  }, [reconnect]);

  useEffect(() => {
    if (RAGConfig) {
      retrieveDatacount();
    } else {
      setCurrentDatacount(0);
    }
  }, [RAGConfig]);

  const retrieveRAGConfig = async () => {
    const config = await fetchRAGConfig(credentials);
    if (config) {
      setRAGConfig(config.rag_config);
    } else {
      addStatusMessage("Failed to fetch RAG Config", "ERROR");
    }
  };

  const sendUserMessage = async () => {
    if (isFetching.current || !userInput.trim()) return;

    const sendInput = userInput;
    setUserInput("");
    isFetching.current = true;
    setCurrentSuggestions([]);
    setFetchingStatus("CHUNKS");
    setMessages((prev) => [...prev, { type: "user", content: sendInput }]);

    try {
      addStatusMessage("Sending query...", "INFO");
      const data = await sendUserQuery(
        sendInput,
        RAGConfig,
        filterLabels,
        documentFilter,
        credentials
      );

      if (!data || data.error) {
        handleErrorResponse(data ? data.error : "No data received");
      } else {
        handleSuccessResponse(data, sendInput);
      }
    } catch (error) {
      handleErrorResponse("Failed to fetch from API");
      console.error("Failed to fetch from API:", error);
    }
  };

  const handleErrorResponse = (errorMessage: string) => {
    addStatusMessage("Query failed", "ERROR");
    setMessages((prev) => [...prev, { type: "error", content: errorMessage }]);
    isFetching.current = false;
    setFetchingStatus("DONE");
  };

  const handleSuccessResponse = (data: QueryPayload, sendInput: string) => {
    setMessages((prev) => [
      ...prev,
      { type: "retrieval", content: data.documents, context: data.context },
    ]);

    addStatusMessage(
      "Received " + Object.entries(data.documents).length + " documents",
      "SUCCESS"
    );

    if (data.documents.length > 0) {
      const firstDoc = data.documents[0];
      setSelectedDocument(firstDoc.uuid);
      setSelectedDocumentScore(
        `${firstDoc.uuid}${firstDoc.score}${firstDoc.chunks.length}`
      );
      setSelectedChunkScore(firstDoc.chunks);

      if (data.context) {
        streamResponses(sendInput, data.context);
        setFetchingStatus("RESPONSE");
      }
    } else {
      handleErrorResponse("We couldn't find any chunks to your query");
    }
  };

  const streamResponses = (query?: string, context?: string) => {
    if (socket?.readyState === WebSocket.OPEN) {
      const filteredMessages = messages
        .slice(1) // Skip the first message
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

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  const handleKeyDown = (e: any) => {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
      e.preventDefault(); // Prevent new line
      sendUserMessage(); // Submit form
    }
  };

  const retrieveDatacount = async () => {
    try {
      const data: DataCountPayload | null = await fetchDatacount(
        currentEmbedding,
        documentFilter,
        credentials
      );
      const labels: LabelsResponse | null = await fetchLabels(credentials);
      if (data) {
        setCurrentDatacount(data.datacount);
      }
      if (labels) {
        setLabels(labels.labels);
      }
    } catch (error) {
      console.error("Failed to fetch from API:", error);
      addStatusMessage("Failed to fetch datacount: " + error, "ERROR");
    }
  };

  const reconnectToVerba = () => {
    setReconnect((prevState) => !prevState);
  };

  const onSaveConfig = async () => {
    addStatusMessage("Saved Config", "SUCCESS");
    await updateRAGConfig(RAGConfig, credentials);
  };

  const onResetConfig = async () => {
    addStatusMessage("Reset Config", "WARNING");
    retrieveRAGConfig();
  };

  const handleSuggestions = async () => {
    if (
      RAGConfig &&
      RAGConfig["Retriever"].components[RAGConfig["Retriever"].selected].config[
        "Suggestion"
      ].value
    ) {
      const suggestions = await fetchSuggestions(userInput, 3, credentials);
      if (suggestions) {
        setCurrentSuggestions(suggestions.suggestions);
      }
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* Header */}
      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-3 items-center justify-between h-min w-full">
        <div className="hidden md:flex gap-2 justify-start items-center">
          <InfoComponent
            tooltip_text="Use the Chat interface to interact with your data and perform Retrieval Augmented Generation (RAG). This interface allows you to ask questions, analyze sources, and generate responses based on your stored documents."
            display_text={"Chat"}
          />
        </div>
        <div className="w-full md:w-fit flex gap-3 justify-end items-center">
          <VerbaButton
            title="Chat"
            Icon={IoChatbubbleSharp}
            onClick={() => {
              setSelectedSetting("Chat");
            }}
            selected={selectedSetting === "Chat"}
            disabled={false}
            selected_color="bg-secondary-verba"
          />
          {production != "Demo" && (
            <VerbaButton
              title="Config"
              Icon={FaHammer}
              onClick={() => {
                setSelectedSetting("Config");
              }}
              selected={selectedSetting === "Config"}
              disabled={false}
              selected_color="bg-secondary-verba"
            />
          )}
        </div>
      </div>

      <div className="bg-bg-alt-verba rounded-2xl flex flex-col h-[50vh] md:h-full w-full overflow-y-auto overflow-x-hidden relative">
        {/* New fixed tab */}
        {selectedSetting == "Chat" && (
          <div className="sticky flex flex-col gap-2 top-0 z-9 p-4 backdrop-blur-sm bg-opacity-30 bg-bg-alt-verba rounded-lg">
            <div className="flex gap-2 justify-start items-center">
              <div className="flex gap-2">
                <div className="dropdown dropdown-hover">
                  <label tabIndex={0}>
                    <VerbaButton
                      title="Label"
                      className="btn-sm min-w-min"
                      icon_size={12}
                      text_class_name="text-xs"
                      Icon={IoMdAddCircle}
                      selected={false}
                      disabled={false}
                    />
                  </label>
                  <ul
                    tabIndex={0}
                    className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
                  >
                    {labels.map((label, index) => (
                      <li key={"Label" + index}>
                        <a
                          onClick={() => {
                            if (!filterLabels.includes(label)) {
                              setFilterLabels([...filterLabels, label]);
                            }
                            const dropdownElement =
                              document.activeElement as HTMLElement;
                            dropdownElement.blur();
                            const dropdown = dropdownElement.closest(
                              ".dropdown"
                            ) as HTMLElement;
                            if (dropdown) dropdown.blur();
                          }}
                        >
                          {label}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {(filterLabels.length > 0 || documentFilter.length > 0) && (
                <VerbaButton
                  onClick={() => {
                    setFilterLabels([]);
                    setDocumentFilter([]);
                  }}
                  title="Clear"
                  className="btn-sm max-w-min"
                  icon_size={12}
                  text_class_name="text-xs"
                  Icon={MdCancel}
                  selected={false}
                  disabled={false}
                />
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {filterLabels.map((label, index) => (
                <VerbaButton
                  title={label}
                  key={"FilterLabel" + index}
                  Icon={MdCancel}
                  className="btn-sm min-w-min max-w-[200px]"
                  icon_size={12}
                  selected_color="bg-primary-verba"
                  selected={true}
                  text_class_name="truncate max-w-[200px]"
                  text_size="text-xs"
                  onClick={() => {
                    setFilterLabels(filterLabels.filter((l) => l !== label));
                  }}
                />
              ))}
              {documentFilter.map((filter, index) => (
                <VerbaButton
                  title={filter.title}
                  key={"DocumentFilter" + index}
                  Icon={MdCancel}
                  className="btn-sm min-w-min max-w-[200px]"
                  icon_size={12}
                  selected_color="bg-secondary-verba"
                  selected={true}
                  text_size="text-xs"
                  text_class_name="truncate md:max-w-[100px] lg:max-w-[150px]"
                  onClick={() => {
                    setDocumentFilter(
                      documentFilter.filter((f) => f.uuid !== filter.uuid)
                    );
                  }}
                />
              ))}
            </div>
          </div>
        )}
        <div
          className={`${selectedSetting === "Chat" ? "flex flex-col gap-3 p-4" : "hidden"}`}
        >
          <div className="flex w-full justify-start items-center text-text-alt-verba gap-2">
            {currentDatacount === 0 && <BiError size={15} />}
            {currentDatacount === 0 && (
              <p className="text-text-alt-verba text-sm items-center flex">{`${currentDatacount} documents embedded by ${currentEmbedding}`}</p>
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
                selectedTheme={selectedTheme}
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
              selectedTheme={selectedTheme}
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
                <button
                  onClick={() => {
                    setFetchingStatus("DONE");
                    isFetching.current = false;
                  }}
                  className="btn btn-circle btn-sm bg-bg-alt-verba hover:bg-warning-verba hover:text-text-verba text-text-alt-verba shadow-none border-none text-sm"
                >
                  <MdCancel size={15} />
                </button>
              </div>
            </div>
          )}
        </div>
        {selectedSetting === "Config" && (
          <ChatConfig
            addStatusMessage={addStatusMessage}
            production={production}
            RAGConfig={RAGConfig}
            credentials={credentials}
            setRAGConfig={setRAGConfig}
            onReset={onResetConfig}
            onSave={onSaveConfig}
          />
        )}
      </div>

      <div className="bg-bg-alt-verba rounded-2xl flex gap-2 p-6 items-center justify-end h-min w-full">
        {socketOnline ? (
          <div className="flex gap-2 items-center justify-end w-full relative">
            <div className="relative w-full">
              <textarea
                className="textarea textarea-bordered w-full bg-bg-verba placeholder-text-alt-verb min-h min-h-[40px] max-h-[150px] overflow-y-auto"
                placeholder={
                  currentDatacount > 0
                    ? currentDatacount >= 100
                      ? `Chatting with more than 100 documents...`
                      : `Chatting with ${currentDatacount} documents...`
                    : `No documents detected...`
                }
                onKeyDown={handleKeyDown}
                onCompositionStart={handleCompositionStart}
                onCompositionEnd={handleCompositionEnd}
                value={userInput}
                onChange={(e) => {
                  const newValue = e.target.value;
                  setUserInput(newValue);
                  if ((newValue.length - 1) % 3 === 0) {
                    handleSuggestions();
                  }
                }}
              />
              {currentSuggestions.length > 0 && (
                <ul className="absolute flex gap-2 justify-between top-full left-0 w-full mt-2 z-10 max-h-40 overflow-y-auto">
                  {currentSuggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="p-3 bg-button-verba hover:bg-secondary-verba text-text-alt-verba rounded-xl w-full hover:text-text-verba cursor-pointer"
                      onClick={() => {
                        setUserInput(suggestion.query);
                        setCurrentSuggestions([]);
                      }}
                    >
                      <p className="text-xs lg:text-sm">
                        {suggestion.query.length > 50
                          ? suggestion.query.substring(0, 50) + "..."
                          : suggestion.query
                              .split(new RegExp(`(${userInput})`, "gi"))
                              .map((part, i) =>
                                part.toLowerCase() ===
                                userInput.toLowerCase() ? (
                                  <strong key={i}>{part}</strong>
                                ) : (
                                  part
                                )
                              )}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="flex flex-col gap-1 items-center justify-center">
              <VerbaButton
                type="button"
                Icon={IoIosSend}
                onClick={() => {
                  sendUserMessage();
                }}
                disabled={false}
                selected_color="bg-primary-verba"
              />
              <VerbaButton
                type="button"
                Icon={MdOutlineRefresh}
                onClick={() => {
                  setSelectedDocument(null);
                  setSelectedChunkScore([]);
                  setUserInput("");
                  setSelectedDocumentScore(null);
                  setCurrentSuggestions([]);
                  setMessages([
                    {
                      type: "system",
                      content: selectedTheme.intro_message.text,
                    },
                  ]);
                }}
                disabled={false}
                selected_color="bg-primary-verba"
              />
            </div>
          </div>
        ) : (
          <div className="flex gap-2 items-center justify-end w-full">
            <button
              onClick={reconnectToVerba}
              className="flex btn border-none text-text-verba bg-button-verba hover:bg-button-hover-verba gap-2 items-center"
            >
              <TbPlugConnected size={15} />
              <p>Reconnecting...</p>
              <span className="loading loading-spinner loading-xs"></span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
