from goldenverba.ingestion.chunking.wordchunker import WordChunker
from goldenverba.ingestion.reader.document import Document

chunker = WordChunker()


def test_split_length_greater_than_doc_length():
    documents = [Document(text="This is a test")]
    modified_documents = chunker.chunk(documents, 50, 5)
    assert modified_documents[0].chunks == []


def test_split_length_less_than_one():
    documents = [Document(text="This is a test")]
    modified_documents = chunker.chunk(documents, 0, 5)
    assert modified_documents[0].chunks == []


def test_split_overlap_greater_than_split_length():
    documents = [Document(text="This is a test")]
    modified_documents = chunker.chunk(documents, 5, 5)
    assert modified_documents[0].chunks == []


def test_overlap():
    documents = [Document(text="This is a test sentence. Another test sentence.")]
    modified_documents = chunker.chunk(documents, 5, 2)
    assert modified_documents[0].chunks[0].text == "This is a test sentence"
    assert modified_documents[0].chunks[1].text == "test sentence. Another test"
    assert modified_documents[0].chunks[2].text == "Another test sentence."


def test_empty_doc():
    documents = [Document(text="")]
    modified_documents = chunker.chunk(documents, 5, 2)
    assert modified_documents[0].chunks == []


def test_non_overlapping_windows():
    documents = [
        Document(text="This is a short sentence. Another short one. And another.")
    ]
    modified_documents = chunker.chunk(documents, 5, 0)
    assert modified_documents[0].chunks[0].text == "This is a short sentence"
    assert modified_documents[0].chunks[1].text == ". Another short one."
    assert modified_documents[0].chunks[2].text == "And another."


def test_overlapping_windows():
    documents = [
        Document(text="This is a short sentence. Another short one. And another.")
    ]
    modified_documents = chunker.chunk(documents, 5, 2)
    assert len(modified_documents[0].chunks) == 4


def test_varying_lengths():
    documents = [
        Document(text="This is a short sentence. Another short one. And another.")
    ]
    modified_documents = chunker.chunk(documents, 3, 1)
    assert len(modified_documents[0].chunks) == 6


def test_long_lengths():
    documents = [
        Document(text="This is a short sentence. Another short one. And another.")
    ]
    modified_documents = chunker.chunk(documents, 11, 2)
    assert len(modified_documents[0].chunks) == 2
