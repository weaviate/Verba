import { useState, useEffect, useCallback } from "react";
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

export const apiHost = getApiHost();
const bgUrl = process.env.NODE_ENV === 'production'
  ? 'static/'
  : '/';


type DocumentChunk = {
  text: string;
  doc_name: string;
  chunk_id: number;
  doc_uuid: string;
  doc_type: DocType;
  _additional: { score: number };
};

export type DocType = "Documentation" | "Blog";
export const DOC_TYPE_COLORS: Record<DocType, string> = {
  Documentation: "bg-green-300",
  Blog: "bg-yellow-200",
};

export const DOC_TYPE_COLOR_HOVER: Record<DocType, string> = {
  Documentation: "hover:bg-green-400",
  Blog: "hover:bg-yellow-300",
};

export default function Home() {
  const [showModal, setShowModal] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [userInput, setUserInput] = useState("");
  const [documentTitle, setDocumentTitle] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [documentLink, setDocumentLink] = useState("#");
  const [documentChunks, setDocumentChunks] = useState<DocumentChunk[]>([]);
  const [apiStatus, setApiStatus] = useState<string>('Offline'); // API status
  const [focusedDocument, setFocusedDocument] = useState<DocumentChunk | null>(
    null
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [isFetching, setIsFetching] = useState(false);

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

  // UseEffect hook to check the API health on initial load
  useEffect(() => {
    checkApiHealth();
  }, [checkApiHealth]);

  const handleSendMessage = async (e?: React.FormEvent, message?: string) => {
    e?.preventDefault();

    const sendInput = message || userInput;

    if (sendInput.trim()) {
      setMessages((prev) => [...prev, { type: "user", content: sendInput }]);

      // Clear the suggestions list
      setSuggestions([]);

      setUserInput("");

      // Start the API call
      setIsFetching(true);

      try {
        checkApiHealth()
        const response = await fetch(apiHost + "/api/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: sendInput }),
        });

        const data = await response.json();
        checkApiHealth()
        setDocumentChunks([]);
        setDocumentChunks(data.documents);
        setSuggestions([]);

        if (data.system) {
          setMessages((prev) => [
            ...prev,
            { type: "system", content: data.system },
          ]);
        }
      } catch (error) {
        checkApiHealth()
        console.error("Failed to fetch from API:", error);
      } finally {
        setIsFetching(false);
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

  const fetchSuggestions = async (query: string) => {
    try {
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
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
    }
  };

  // Debounce the fetchSuggestions function to prevent rapid requests
  const debouncedFetchSuggestions = debounce(fetchSuggestions, 200);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value);
    debouncedFetchSuggestions(e.target.value);
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
      {showModal && <ImportModalComponent onClose={() => setShowModal(false)} apiHost={apiHost} />}
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
            <div className="ml-16 animate-pop-in">
              <button
                className="flex items-center space-x-2 bg-gray-200 text-black p-3  rounded-lg  hover:bg-green-400 border-2 border-black hover:border-white hover-container shadow-md"
                onClick={() => setShowModal(true)}
              >
                <FaPlus />
                <span>Add Documents</span>
              </button>
            </div>
            <ConfigModal component="embedders" apiHost={apiHost}></ConfigModal>
          </div>
        </div>
        <div className="p-1 lg:flex overflow-x-auto justify-center h-32 w-full mb-2 hidden">
          {documentChunks.map((chunk, index) => (
            <button
              key={chunk.doc_name + index}
              onClick={() => setFocusedDocument(chunk)}
            >
              <div
                className={`bg-none
                  } rounded-lg text-xs hover-container mx-1 h-28 w-48 p-1 animate-pop-in`}
              >
                <div className={`text-xs mb-1 ${focusedDocument === chunk ? '' : 'fade-in-out'} ${DOC_TYPE_COLORS[chunk.doc_type]} p-2 rounded-lg w-full`}>
                  {chunk.doc_type}
                </div>
                <div className="flex space-x-2 mt-1">
                  <div className={`flex items-center rounded-md bg-gray-200 p-2 truncate h-16 border-2 shadow-md hover:border-white border-black ${focusedDocument === chunk ? DOC_TYPE_COLORS[chunk.doc_type] : DOC_TYPE_COLOR_HOVER[chunk.doc_type]}`}>
                    <div className={`text-sm font-bold ${DOC_TYPE_COLORS[chunk.doc_type]} p-2 rounded-lg`}>
                      {" "}
                      <CountUp end={Math.round(chunk._additional.score * 10000)} />
                    </div>
                    <p className="font-bold ml-1">{chunk.doc_name}</p>
                  </div>

                </div>
              </div>
            </button>
          ))}
        </div>
        <div className="flex w-full space-x-4">
          <div className="lg:w-1/2 md:w-full sm:w-full p-2 border-2 shadow-lg lg:h-2/3 sm:h-full md:h-full border-gray-900 rounded-xl animate-pop-in">

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
                    {apiStatus + " v0.3.0"}
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
                placeholder="What is a vector database?"
                className="w-full p-2 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </form>
            <div className="absolute mt-2 p-2 z-10 w-1/2 left-5 text-center justify-center">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index + suggestion}
                  className="p-2 hover:bg-green-300 bg-gray-200 cursor-pointer shadow-md rounded-md text-xs animate-press-in mt-2 hover-container"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {renderBoldedSuggestion(suggestion, userInput)}
                </div>
              ))}
            </div>
          </div>
          <div className="w-1/2 space-y-4 hidden lg:block">
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