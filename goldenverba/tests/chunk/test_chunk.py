from goldenverba.components.chunk import Chunk


def test_chunk_json_serialization_round_trip():
    original_chunk = Chunk(
        content="Chunk content",
        content_without_overlap="Chunk",
        chunk_id="chunk-1",
        start_i=5,
        end_i=15,
    )
    original_chunk.title = "Chunk Title"
    original_chunk.labels = ["invoice", "important"]
    original_chunk.doc_uuid = "doc-123"
    original_chunk.pca = [0.1, 0.2, 0.3]

    restored_chunk = Chunk.from_json(original_chunk.to_json())

    assert restored_chunk.content == original_chunk.content
    assert (
        restored_chunk.content_without_overlap == original_chunk.content_without_overlap
    )
    assert restored_chunk.chunk_id == original_chunk.chunk_id
    assert restored_chunk.start_i == original_chunk.start_i
    assert restored_chunk.end_i == original_chunk.end_i
    assert restored_chunk.title == original_chunk.title
    assert restored_chunk.labels == original_chunk.labels
    assert restored_chunk.doc_uuid == original_chunk.doc_uuid
    assert restored_chunk.pca == original_chunk.pca
    assert isinstance(restored_chunk.doc_uuid, str)
