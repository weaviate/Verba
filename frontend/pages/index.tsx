import { useState, useEffect, useRef } from "react";
import { ChatComponent, Message } from "../components/ChatComponent";
import { DocumentComponent } from "../components/DocumentComponent";

export const apiHost = 'verba-private:8001';

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
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [userInput, setUserInput] = useState("");
  const [documentTitle, setDocumentTitle] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [documentLink, setDocumentLink] = useState("#");
  const [documentChunks, setDocumentChunks] = useState<DocumentChunk[]>([]);
  const [focusedDocument, setFocusedDocument] = useState<DocumentChunk | null>(
    null
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [isFetching, setIsFetching] = useState(false);

  const handleSendMessage = async (e?: React.FormEvent, message?: string) => {
    e?.preventDefault();

    const sendInput = message || userInput;

    if (sendInput.trim()) {
      setMessages((prev) => [...prev, { type: "user", content: sendInput }]);

      setUserInput("");
      // Clear the suggestions list
      setSuggestions([]);

      // Start the API call
      setIsFetching(true);

      try {
        const response = await fetch(apiHost + "/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: sendInput }),
        });

        const data = await response.json();

        setDocumentChunks([]);
        setDocumentChunks(data.documents);

        if (data.system) {
          setMessages((prev) => [
            ...prev,
            { type: "system", content: data.system },
          ]);
        }
      } catch (error) {
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
          const response = await fetch(apiHost + "/get_document", {
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
      const response = await fetch(apiHost + "/suggestions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      setSuggestions(data.suggestions); // Assuming the returned data structure contains a "suggestions" field
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
    }
  };

  // Debounce the fetchSuggestions function to prevent rapid requests
  const debouncedFetchSuggestions = debounce(fetchSuggestions, 25);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value);
    debouncedFetchSuggestions(e.target.value);
  };

  const handleSuggestionClick = async (suggestion: string) => {
    // Update the userInput with the clicked suggestion
    setUserInput(suggestion);
    handleSendMessage(undefined, suggestion);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-12 text-gray-900">
      <div className="flex flex-col w-full items-start">
        <div className="mb-4">
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

          <h1 className="text-8xl font-bold mt-2">Verba</h1>
          <p className="text-sm mt-1 text-gray-400">
            Retrieval Augmented Generation system powered by Weaviate
          </p>
        </div>
        <div className="p-1 flex overflow-x-auto justify-center w-full mb-2">
          {documentChunks.map((chunk, index) => (
            <button
              key={chunk.doc_name + index}
              onClick={() => setFocusedDocument(chunk)}
            >
              <div
                className={`${DOC_TYPE_COLORS[chunk.doc_type]
                  } rounded-lg text-xs hover-container shadow-lg border-2 hover:border-white border-black mx-2 p-4 ${DOC_TYPE_COLOR_HOVER[chunk.doc_type]
                  } animate-pop-in`}
              >
                <div className="flex items-center">
                  <span className="font-bold">{chunk.doc_name}</span>
                </div>
                <div className="flex justify-between space-x-1 mt-3">
                  <div className="text-xs bg-white bg-opacity-50 p-2 rounded-lg">
                    {chunk.doc_type}
                  </div>
                  <div className="text-xs bg-white bg-opacity-50 p-2 rounded-lg">
                    {" "}
                    Score {Math.round(chunk._additional.score * 10000)}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
        <div className="flex w-full space-x-4">
          <div className="w-1/2 p-2 border-2 shadow-lg h-2/3 border-gray-900 rounded-xl animate-pop-in">
            {/* Header */}
            <div className="rounded-t-xl bg-yellow-200 p-4 flex justify-between items-center">
              Verba Chat
            </div>

            {/* ChatComponent */}
            <ChatComponent
              onUserMessageSubmit={messages}
              isFetching={isFetching}
            />

            {/* Input area */}
            <form
              className="rounded-b-xl bg-gray-800 p-4"
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
            <div className="mt-2 bg-gray-200 rounded-md relative">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-2 hover:bg-gray-300 cursor-pointer text-sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          </div>
          <div className="w-1/2 space-y-4">
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
    </main>
  );
}
