from goldenverba.ingestion.reader.document import Document
from goldenverba.ingestion.chunking.chunk import Chunk


def test_serialization():
    document = Document(text="This is a test")
    Document.serialize_to_verba(document, "./data/serialize.verba")
    document_loaded = Document.deserialize_verba("./data/serialize.verba")

    assert document_loaded.text == "This is a test"


def test_serialization_with_chunks():
    document = Document(text="This is a test")
    document.chunks = [
        Chunk(text="This is a chunk"),
        Chunk(text="This is another chunk"),
    ]
    Document.serialize_to_verba(document, "./data/serialize_with_chunks.verba")
    document_loaded = Document.deserialize_verba("./data/serialize_with_chunks.verba")

    assert document_loaded.text == "This is a test"
    assert len(document_loaded.chunks) == 2
    assert document_loaded.chunks[0].text == "This is a chunk"
