import { useState, useEffect } from "react";
import { DocumentComponent } from "../components/DocumentComponent";
import { FixedSizeList as List } from "react-window";
import { DocType, DOC_TYPE_COLORS, DOC_TYPE_COLOR_HOVER, getApiHost } from "@/pages";

type Document = {
    doc_name: string;
    doc_type: DocType;
    doc_link: string;
    _additional: { id: string };
};

const apiHost = getApiHost()
const bgUrl = process.env.NODE_ENV === 'production'
    ? 'static/'
    : '/';


export default function DocumentOnly() {
    const [searchQuery, setSearchQuery] = useState("");
    const [documentTitle, setDocumentTitle] = useState("");
    const [documentText, setDocumentText] = useState("");
    const [documentType, setDocumentType] = useState<DocType>("Documentation");
    const [documentLink, setDocumentLink] = useState("#");
    const [documents, setDocuments] = useState<Document[]>([]);
    const [focusedDocument, setFocusedDocument] = useState<Document | null>(null);

    const fetchDocuments = async (query = "") => {
        try {
            const endpoint = query
                ? `${apiHost}/api/search_documents`
                : `${apiHost}/api/get_all_documents`;

            const body = query ? { "query": query } : {};

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body),
            });

            const data = await response.json();

            // Assuming the data is an array of documents
            setDocuments(data.documents);
        } catch (error) {
            console.error(`Failed to fetch documents: ${error}`);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    useEffect(() => {
        const fetchDocument = async () => {
            if (focusedDocument && focusedDocument._additional.id) {
                try {
                    const response = await fetch(apiHost + "/api/get_document", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            document_id: focusedDocument._additional.id,
                        }),
                    });
                    const documentData = await response.json();

                    // Update the document title and text
                    setDocumentTitle(documentData.document.properties.doc_name);
                    setDocumentText(documentData.document.properties.text);
                    setDocumentType(documentData.document.properties.doc_type);
                    setDocumentLink(documentData.document.properties.doc_link);
                } catch (error) {
                    console.error("Failed to fetch document:", error);
                }
            }
        };

        fetchDocument();
    }, [focusedDocument]);

    // Handle form submission
    const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const form = e.currentTarget;
        const formData = new FormData(form);
        const query = formData.get("searchInput");  // 'searchInput' is the name attribute of input field

        fetchDocuments(query as string);
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-10 text-gray-900">
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
                    </div>
                </div>
                <div className="flex w-full space-x-4 mt-12">
                    <div className="w-1/2 p-2 border-2 shadow-lg h-2/3 border-gray-900 rounded-xl animate-pop-in">
                        <div className="rounded-t-xl bg-yellow-200 p-4 flex justify- between items-center">
                            <form
                                className="rounded-b-xl p-4 w-full"
                                onSubmit={handleSearch}
                            >
                                <input
                                    type="text"
                                    name="searchInput"
                                    placeholder="Search for documents"
                                    className="w-full p-2 rounded-md bg-white text-gray-900 placeholder-gray-400"
                                />
                            </form>
                        </div>
                        {documents.length > 0 && (

                            <List
                                height={528}
                                itemCount={documents.length}
                                itemSize={100}
                                width={825}
                            >
                                {({ index, style }) => (
                                    <button
                                        style={style}
                                        key={index}
                                        className=" w-full p-4 animate-pop-in-late"
                                        onClick={() => setFocusedDocument(documents[index])} // Add click handler
                                    >
                                        <p
                                            className={`${DOC_TYPE_COLORS[documents[index].doc_type]
                                                } p-8 w-full rounded-md shadow-md ${DOC_TYPE_COLOR_HOVER[documents[index].doc_type]
                                                }`}
                                        >
                                            {documents[index].doc_name}
                                        </p>
                                    </button>
                                )}
                            </List>
                        )}
                    </div>
                    <div className="w-1/2 space-y-4">
                        <DocumentComponent
                            title={documentTitle}
                            text={documentText}
                            extract={""}
                            docLink={documentLink}
                            type={documentType}
                        />
                    </div>
                </div>
            </div>
        </main>
    );
}