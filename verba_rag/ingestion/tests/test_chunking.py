from verba_rag.ingestion.preprocess import chunk_doc
import spacy


nlp = spacy.blank("en")


def test_split_length_greater_than_doc_length():
    doc = nlp("This is a test.")
    chunks = chunk_doc(doc, nlp, 50, 5)
    assert chunks == []


def test_split_length_less_than_one():
    doc = nlp("This is a test.")
    chunks = chunk_doc(doc, nlp, 0, 5)
    assert chunks == []


def test_split_overlap_greater_than_split_length():
    doc = nlp("This is a test.")
    chunks = chunk_doc(doc, nlp, 5, 5)
    assert chunks == []


def test_overlap():
    doc = nlp("This is a test sentence. Another test sentence.")
    chunks = chunk_doc(doc, nlp, 5, 2)
    assert len(chunks) == 3
    assert chunks[0].text == "This is a test sentence"
    assert chunks[1].text == "test sentence. Another test"
    assert chunks[2].text == "Another test sentence."


def test_empty_doc():
    doc = nlp("")
    chunks = chunk_doc(doc, nlp, 5, 2)
    assert chunks == []


def test_non_overlapping_windows():
    doc = nlp("This is a short sentence. Another short one. And another.")
    chunks = chunk_doc(doc, nlp, 5, 0)
    assert len(chunks) == 3
    assert chunks[0].text == "This is a short sentence"
    assert chunks[1].text == ". Another short one."
    assert chunks[2].text == "And another."


def test_overlapping_windows():
    doc = nlp("This is a short sentence. Another short one. And another.")
    chunks = chunk_doc(doc, nlp, 5, 2)
    assert len(chunks) == 4


def test_varying_lengths():
    doc = nlp("This is a short sentence. Another short one. And another.")
    chunks = chunk_doc(doc, nlp, 3, 1)
    assert len(chunks) == 6


def test_long_lengths():
    doc = nlp("This is a short sentence. Another short one. And another.")
    chunks = chunk_doc(doc, nlp, 11, 2)
    assert len(chunks) == 2
