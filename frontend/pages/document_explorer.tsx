import { useState, useEffect } from "react";
import { DocumentComponent } from "../components/DocumentComponent";
import { FixedSizeList as List } from "react-window";
import { DocType, DOC_TYPE_COLORS, DOC_TYPE_COLOR_HOVER, apiHost } from "@/pages";

type Document = {
    doc_name: string;
    doc_type: DocType;
    doc_link: string;
    _additional: { id: string };
};

export default function DocumentOnly() {
    const [documentTitle, setDocumentTitle] = useState("");
    const [documentText, setDocumentText] = useState("");
    const [documentType, setDocumentType] = useState<DocType>("Documentation");
    const [documentLink, setDocumentLink] = useState("#");
    const [documents, setDocuments] = useState<Document[]>([]);
    const [focusedDocument, setFocusedDocument] = useState<Document | null>(null);

    useEffect(() => {
        const fetchAllDocuments = async () => {
            try {
                const response = await fetch(apiHost + "/get_all_documents_verba");
                const data = await response.json();
                console.log(data);
                // Assuming the data is an array of documents
                setDocuments(data.documents);
            } catch (error) {
                console.error("Failed to fetch all documents:", error);
            }
        };

        fetchAllDocuments();
    }, []);

    useEffect(() => {
        const fetchDocument = async () => {
            if (focusedDocument && focusedDocument._additional.id) {
                try {
                    const response = await fetch(apiHost + "/get_document_verba", {
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
                <div className="flex w-full space-x-4">
                    {documents.length > 0 && (
                        <div className="w-1/2 p-2 border-2 shadow-lg h-2/3 border-gray-900 rounded-xl animate-pop-in">
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
                        </div>
                    )}
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
