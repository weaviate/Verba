import { useState, useEffect, useCallback, useRef } from "react";
import { ChatComponent, Message } from "../components/ChatComponent";
import { DocumentComponent } from "../components/DocumentComponent";
import ImportModalComponent from "../components/ImportModalComponent";
import ConfigModal from "../components/ConfigModal";
import { FaPlus } from "react-icons/fa";
import CountUp from 'react-countup';

export const getApiHost = () => {
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  return "";
};

export const getApiHostNoHttp = () => {
  if (process.env.NODE_ENV === 'development') {
    return 'localhost:8000';
  }
  return "";
};

export const apiHost = getApiHost();
const bgUrl = process.env.NODE_ENV === 'production'
  ? 'static/'
  : '/';


type DocumentChunk = {
  text: string;
  doc_name: string;
  chunk_id: number;
  doc_uuid: string;
  doc_type: string;
  score: number;
};

export default function Home() {
  const [showModal, setShowModal] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [userInput, setUserInput] = useState("");
  const [streamable, setStreamable] = useState(false);
  const [documentTitle, setDocumentTitle] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [documentLink, setDocumentLink] = useState("#");
  const [documentChunks, setDocumentChunks] = useState<DocumentChunk[]>([]);
  const [apiStatus, setApiStatus] = useState<string>('Offline'); // API status
  const [focusedDocument, setFocusedDocument] = useState<DocumentChunk | null>(
    null
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [production, setProduction] = useState<boolean>(false);
  const [isFetching, setIsFetching] = useState(false);
  const [isFetchingSuggestion, setIsFetchingSuggestions] = useState(false);
  const handleGenerateStreamMessageRef = useRef<Function | null>(null);

  // Function for checking the health of the API
  const checkApiHealth = useCallback(async () => {
    try {
      // Change ENDPOINT based on your setup (Default to localhost:8000)
      const response = await fetch(apiHost + '/api/health');

      if (response.status === 200) {
        setApiStatus('Online');
      } else {
        setApiStatus('Offline');
      }
    } catch (error) {
      setApiStatus('Offline');
    }
  }, []);

  useEffect(() => {
    const fetchProduction = async () => {
      try {
        const response = await fetch(apiHost + "/api/get_production", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const response_data = await response.json();

        if (response_data.production == true) {
          console.log("In Production Mode")
        } else {
          console.log("In Normal Mode")
        }

        // Update the document title and text
        setProduction(response_data.production);
      } catch (error) {
        console.error("Failed to fetch document:", error);
      }
    }

    fetchProduction();
  }, []);

  // UseEffect hook to check the API health on initial load
  useEffect(() => {
    checkApiHealth();
  }, [checkApiHealth]);

  const handleGenerateMessage = async (query?: string, context?: string) => {

    try {
      console.log(messages)
      const answerResponse = await fetch(apiHost + "/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query, context: context, conversation: messages }), // context will be added once we get it from the first API call,
      });

      const answerData = await answerResponse.json();

      if (answerData.system) {
        setMessages((prev) => [
          ...prev,
          { type: "system", content: answerData.system, typewriter: true },
        ]);
      }
    } catch (error) {
      console.error("Failed to fetch from API:", error);
    } finally {
      setIsFetching(false);
    }
  }

  const setHandleGenerateStreamMessage = (ref: React.MutableRefObject<Function | null>) => {
    handleGenerateStreamMessageRef.current = ref.current;
  };

  const handleGenerateStreamMessage = (query?: string, context?: string) => {
    if (handleGenerateStreamMessageRef.current) {
      handleGenerateStreamMessageRef.current(query, context);
    }
  };

  const generatorStreamable = (streamable: boolean) => {
    setStreamable(streamable)
  }

  const handleSendMessage = async (e?: React.FormEvent, message?: string) => {
    e?.preventDefault();

    const sendInput = message || userInput;

    if (sendInput.trim()) {
      setMessages((prev) => [...prev, { type: "user", content: sendInput, typewriter: true }]);

      // Clear the suggestions list
      setSuggestions([]);
      setUserInput("");

      // Start the API call
      setIsFetching(true);

      try {
        checkApiHealth();

        // Start both API calls in parallel
        const queryResponse = await fetch(apiHost + "/api/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: sendInput }),
        })

        const queryData = await queryResponse.json();
        checkApiHealth();
        setDocumentChunks([]);
        setDocumentChunks(queryData.documents);
        setSuggestions([]);

        if (queryData.context != "") {
          if (streamable) {
            handleGenerateStreamMessage(sendInput, queryData.context)
          } else {
            handleGenerateMessage(sendInput, queryData.context)
          }
        } else {
          setIsFetching(false)
          setMessages((prev) => [
            ...prev,
            { type: "system", content: "Your Verba has no data yet :(", typewriter: true },
          ]);
        }

      } catch (error) {
        checkApiHealth();
        console.error("Failed to fetch from API:", error);
      }
    }
  };

  useEffect(() => {
    // Now, set the first chunk as the focused document inside this useEffect
    if (documentChunks && documentChunks.length > 0) {
      setFocusedDocument(documentChunks[0]);
    }
  }, [documentChunks]);

  useEffect(() => {
    const fetchDocument = async () => {
      if (focusedDocument && focusedDocument.doc_uuid) {
        try {
          const response = await fetch(apiHost + "/api/get_document", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ document_id: focusedDocument.doc_uuid }),
          });
          const documentData = await response.json();

          // Update the document title and text
          setDocumentTitle(documentData.document.properties.doc_name);
          setDocumentText(documentData.document.properties.text);
          setDocumentLink(documentData.document.properties.doc_link);
        } catch (error) {
          console.error("Failed to fetch document:", error);
        }
      }
    };

    fetchDocument();
  }, [focusedDocument]);

  function debounce(func: (...args: any[]) => void, wait: number) {
    let timeout: number | null = null;

    return function executedFunction(...args: any[]) {
      const later = () => {
        if (timeout !== null) {
          clearTimeout(timeout);
        }
        func(...args);
      };

      if (timeout !== null) {
        clearTimeout(timeout);
      }
      timeout = window.setTimeout(later, wait);
    };
  }

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const fetchSuggestions = async (query: string) => {
    try {
      setIsFetchingSuggestions(true);
      const response = await fetch(apiHost + "/api/suggestions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (userInput != '') {
        setSuggestions(data.suggestions);
      }
      await delay(1000);
      setIsFetchingSuggestions(false)
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
      setIsFetchingSuggestions(false)
    }
  };

  // Debounce the fetchSuggestions function to prevent rapid requests
  const debouncedFetchSuggestions = debounce(fetchSuggestions, 1500);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value);
    if (!isFetchingSuggestion) {
      fetchSuggestions(e.target.value);
    }
  };

  const handleSuggestionClick = async (suggestion: string) => {
    // Update the userInput with the clicked suggestion
    setUserInput(suggestion);
    handleSendMessage(undefined, suggestion);
  };

  const escapeRegExp = (string: string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
  };

  const renderBoldedSuggestion = (suggestion: string, userInput: string) => {
    const escapedUserInput = escapeRegExp(userInput);
    const parts = suggestion.split(new RegExp(`(${escapedUserInput})`, 'gi'));
    return (
      <span>
        {parts.map((part, i) => (
          <span key={i} className={part.toLowerCase() === userInput.toLowerCase() ? 'font-bold text-sm' : ''}>
            {part}
          </span>
        ))}
      </span>
    );
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-10 text-gray-900">
      {showModal && <ImportModalComponent onClose={() => {
        setShowModal(false)
      }} apiHost={apiHost} />}
      <div className="flex flex-col w-full items-start">
        <div className="mb-2">
          <div className="flex justify-between items-center w-full"> {/* <-- flexbox container */}
            <div className="flex-none">
              <div className="bg-yellow-200 border-2 border-gray-800 rounded-lg shadow-lg animate-pop-in hover-container mr-4 ">
                <img src={`${bgUrl}verba.png`} alt="Verba Logo" className=" w-24 h-24 shadow-lg" />
              </div>
            </div>
            <div className="flex-1">
              <h1 className=" text-6xl font-bold">Verba</h1>
              <div className="flex text-lg">
                <span className="bg-opacity-0 rounded px-2 py-1 hover-container animate-pop-in">
                  The
                </span>
                <span className="bg-opacity-0 rounded font-bold px-2 py-1 hover-container animate-pop-in-late">
                  Golden
                </span>
                <span className="bg-yellow-200 rounded px-2 py-1 hover-container animate-pop-more-late">
                  RAGtriever
                </span>
              </div>
            </div>
            <div className="lg:flex sm:grid sm:grid-cols-2 sm:gap-y-2 md:grid md:grid-cols-2 md:gap-x-4 md:gap-y-4 justify-between items-center mx-auto p-4 ml-10">
              <div className="ml-5 animate-pop-in">
                <div className="flex items-center">
                  <button
                    className="flex items-center sm:w-32 md:w-44 space-x-2 mr-8 bg-gray-200 text-black p-3  rounded-lg  hover:bg-green-400 border-2 border-black hover:border-white hover-container shadow-md"
                    onClick={() => setShowModal(true)}
                  >
                    <FaPlus />
                    <span className='truncate'>Add Documents</span>
                  </button>
                </div>
              </div>
              <ConfigModal component="embedders" apiHost={apiHost} onGeneratorSelect={generatorStreamable} production={production}></ConfigModal>
              <ConfigModal component="retrievers" apiHost={apiHost} onGeneratorSelect={generatorStreamable} production={production}></ConfigModal>
              <ConfigModal component="generators" apiHost={apiHost} onGeneratorSelect={generatorStreamable} production={production}></ConfigModal>
            </div>
          </div>
        </div>
        <div className={`lg:flex md:flex ${documentChunks.length <= 8 ? 'full:justify-center' : ''} justify-items-start overflow-x-auto h-36 w-full mb-2 hidden`}>
          {documentChunks.map((chunk, index) => (
            <button
              key={chunk.doc_name + index}
              onClick={() => setFocusedDocument(chunk)}
            >
              <div
                className={`bg-none
                  } rounded-lg text-xs hover-container mx-1 h-28 w-48 p-1 animate-pop-in`}
              >
                <div className={`text-xs mb-1 ${focusedDocument === chunk ? '' : 'fade-in-out'} bg-yellow-300 p-2 rounded-lg w-full`}>
                  {chunk.doc_type}
                </div>
                <div className="flex space-x-2 mt-1">
                  <div className={`flex items-center rounded-md bg-gray-200 p-2 truncate h-16 border-2 shadow-md hover:border-white border-black ${focusedDocument === chunk ? "bg-green-300" : "bg-gray-300"}`}>
                    <div className={`text-sm font-bold bg-green-300 p-2 rounded-lg`}>
                      {" "}
                      <CountUp end={Math.round(chunk.score * 100)} />
                    </div>
                    <p className="font-bold ml-1">{chunk.doc_name}</p>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
        <div className="flex w-full space-x-4 overflow-y-auto mb-20">
          <div className="lg:w-1/2 md:w-full sm:w-full p-2 border-2 shadow-lg border-gray-900 rounded-xl animate-pop-in">

            {/* Header */}
            <div className="rounded-t-xl bg-gray-200 p-4 flex justify-between items-center">
              🐕 RAGtriever Chat
              <div className="text-xs text-white font-mono flex justify-center">
                <a href="https://github.com/weaviate/Verba" target="_blank" rel="noopener noreferrer">
                  <span
                    className={`rounded-indicator hover-container text-white p-2 ${apiStatus === 'Online'
                      ? 'bg-green-500 hover:bg-green-400'
                      : 'bg-red-500 hover:bg-red-400'
                      }`}
                  >
                    {apiStatus + " v0.4.0"}
                  </span>
                </a>
                <a href="https://www.weaviate.io" target="_blank" rel="noopener noreferrer">
                  <span
                    className="rounded-indicator text-white bg-gray-400 hover:bg-gray-300 ml-2 p-2 hover-container">
                    Powered by Weaviate ❤️
                  </span>
                </a>
              </div>
            </div>

            {/* ChatComponent */}
            <ChatComponent
              onUserMessageSubmit={messages}
              isFetching={isFetching}
              apiHost={getApiHostNoHttp()}
              setHandleGenerateStreamMessageRef={setHandleGenerateStreamMessage}
              setIsFetching={setIsFetching}
            />

            {/* Input area */}
            <form
              className="rounded-b-xl bg-gray-500 p-4 relative"
              onSubmit={handleSendMessage}
            >
              <input
                type="text"
                value={userInput}
                onChange={handleInputChange}
                disabled={isFetching}
                placeholder="What is a vector database?"
                className="w-full p-2 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </form>
            <div className="absolute mt-2 p-2 z-10 w-1/2 left-5 text-center justify-center flex flex-wrap">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index + suggestion}
                  className="p-2 hover:bg-green-300 bg-gray-200 cursor-pointer shadow-md rounded-md text-xs animate-press-in mt-2 mr-4 hover-container"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {renderBoldedSuggestion(suggestion, userInput)}
                </div>
              ))}
            </div>
          </div>
          <div className="w-1/2 space-y-4 hidden lg:block md:block">
            <DocumentComponent
              title={documentTitle}
              text={documentText}
              extract={focusedDocument?.text}
              docLink={documentLink}
              type={focusedDocument?.doc_type}
            />
          </div>
        </div>
      </div>
    </main >
  );
}