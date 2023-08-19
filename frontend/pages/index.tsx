import { useState, useEffect, useRef } from 'react';
import { ChatComponent, Message } from '../components/ChatComponent';
import { DocumentComponent } from '../components/DocumentComponent';

type DocumentChunk = {
  text: string;
  doc_name: string;
  chunk_id: number;
  doc_uuid: string;
};

export default function Home() {

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [documentTitle, setDocumentTitle] = useState("Weaviate Blogpost");
  const [documentText, setDocumentText] = useState("This is an example blogpost");
  const [documentLink, setDocumentLink] = useState("#");
  const [documentChunks, setDocumentChunks] = useState<DocumentChunk[]>([]);
  const [focusedDocument, setFocusedDocument] = useState<DocumentChunk | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isFetching, setIsFetching] = useState(false);


  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (userInput.trim()) {
      setMessages((prev) => [...prev, { type: 'user', content: userInput }]);

      const sendInput = userInput
      setUserInput('');

      // Start the API call
      setIsFetching(true);

      try {
        const response = await fetch("http://localhost:8000/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ query: sendInput })
        });

        const data = await response.json();

        setDocumentChunks(data.documents);

        if (data.system) {
          setMessages((prev) => [...prev, { type: 'system', content: data.system }]);
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
          const response = await fetch("http://localhost:8000/get_document", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ document_id: focusedDocument.doc_uuid })
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

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-12 text-gray-900">
      <div className="flex flex-col w-full items-start">
        <div className="mb-4">
          <div className="flex text-lg">
            <span className="bg-opacity-0 rounded px-2 py-1 hover-container animate-pop-in">search,</span>
            <span className="bg-opacity-0 rounded px-2 py-1 hover-container animate-pop-in-late">find,</span>
            <span className="bg-yellow-200 rounded px-2 py-1 hover-container animate-pop-more-late">generate</span>
          </div>
          <h1 className="text-8xl font-bold mt-2">Verba</h1>
          <p className="text-md mt-1 text-gray-400">Retrieval Augmented Generation system powered by Weaviate</p>
        </div>
        <div className="p-1 flex overflow-x-auto justify-center shadow-lg rounded-lg w-full"> {/* Removed max-width and added w-full to span the full width */}
          {documentChunks.map((chunk, index) => (
            <button
              key={chunk.chunk_id}
              onClick={() => setFocusedDocument(chunk)}
              className="bg-green-300 hover:bg-green-400 text-xs font-bold py-2 px-4 m-2 w-1/2 rounded animate-pop-in" // Added w-1/2 for width, and text-xs for smaller text
            >
              {index}.  {chunk.doc_name} {/* Display the index number followed by the document name */}
            </button>
          ))}
        </div>
        <div className="flex w-full space-x-4">
          <div className="w-1/2 p-2 border-2 shadow-lg h-2/3 border-gray-900 rounded-xl animate-pop-in">
            {/* Header */}
            <div className="rounded-t-xl bg-yellow-200 p-4 flex justify-between items-center">
              Verba Chat
              <button onClick={() => setSettingsOpen(!settingsOpen)}>
                Settings
              </button>
            </div>

            {settingsOpen && (
              <div className="bg-yellow-100 p-4">
                {/* Dropdowns */}
                <div className="flex space-x-4 mb-4">
                  <select className="border rounded-md p-2" placeholder="Dropdown 1">
                    <option value="" disabled selected>Select an option</option>
                    {/* Example options */}
                    <option value="option1">gpt3.5</option>
                  </select>

                  <select className="border rounded-md p-2" placeholder="Dropdown 2">
                    <option value="" disabled selected>Select another option</option>
                    {/* Example options */}
                    <option value="optionA">BM25 Search</option>
                    <option value="optionB">Vector Search</option>
                    <option value="optionB">Hybrid Search</option>
                  </select>
                </div>

                {/* Slider */}
                <div className="flex items-center mb-4">
                  <input type="range" min="1" max="10" className="flex-grow mr-2" />
                  <span>5</span>
                </div>

                {/* Checkbox */}
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    Generative Search
                  </label>
                </div>
              </div>
            )}

            {/* ChatComponent */}
            <ChatComponent onUserMessageSubmit={messages} isFetching={isFetching} />

            {/* Input area */}
            <form className="rounded-b-xl bg-gray-800 p-4" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={userInput}
                onChange={e => setUserInput(e.target.value)}
                placeholder="What is a vector database?"
                className="w-full p-2 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </form>
          </div>
          <div className="w-1/2 space-y-4">
            <DocumentComponent title={documentTitle} text={documentText} extract={focusedDocument?.text} docLink={documentLink} />
          </div>
        </div>
      </div>
    </main>
  )
}
