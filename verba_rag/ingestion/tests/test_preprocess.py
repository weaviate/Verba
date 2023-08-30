from verba_rag.ingestion import preprocess


def test_document_conversion():
    # Test cases to assert
    test_cases = {
        "test_file": """
# Verba 
The Golden RAGtriever.
Welcome to Verba The Golden RAGtriever, an open-source project aimed at providing an easy usable retrieval augmented generation (RAG) app. 
Use it to interact with your data in just a handful of steps!
Verba is a WIP project and many important features and updates are on their way!"""
    }

    docs = preprocess.convert_files(test_cases)
    doc = docs[0]

    assert len(list(doc.sents)) == 4
