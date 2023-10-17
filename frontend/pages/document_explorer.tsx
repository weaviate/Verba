import { useState, useEffect } from "react";
import { DocumentComponent } from "../components/DocumentComponent";
import { FixedSizeList as List } from "react-window";
import { DocType, DOC_TYPE_COLORS, DOC_TYPE_COLOR_HOVER, getApiHost } from "@/pages";
import ImportModalComponent from "../components/ImportModalComponent";
import { FaPlus } from "react-icons/fa";
import CoolButton from "../components/CoolButton";

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
    const [showModal, setShowModal] = useState(false);
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
                    </div>
                </div>
                <div className="flex w-full space-x-4 mt-12">
                    <div className="flex-1 bg-white bg-opacity-20 rounded-lg shadow-md backdrop-filter max-h-[50vh] backdrop-blur-md p-4 w-1/3 animate-pop-in">
                        <div className="p-2">
                            <h2 className="text-lg font-bold mb-4">📚 Documents</h2>
                            <p className="text-xs font-bold mb-4 text-gray-600">Search through your imported documents</p>
                            <div className="rounded-lg flex justify- between items-center">

                                <form
                                    className="rounded-b-xl p-2 w-full"
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
                            <hr />
                        </div>
                        {documents.length > 0 && (

                            <List
                                height={528}
                                itemCount={documents.length}
                                itemSize={100}
                                width={550}
                            >
                                {({ index, style }) => (
                                    <CoolButton
                                        key={documents[index].doc_name}
                                        main={documents[index].doc_name}
                                        clipboard={true}
                                        sub={documents[index].doc_type}
                                        onClick={() => setFocusedDocument(documents[index])}
                                        title={documents[index].doc_name}
                                    />
                                )}
                            </List>
                        )}
                    </div>
                    <div className="w-2/3 space-y-4">
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