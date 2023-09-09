import os
from pathlib import Path

from wasabi import msg  # type: ignore[import]

import spacy

from goldenverba.ingestion.util import (
    setup_client,
    import_documents,
    import_chunks,
    import_suggestions,
)
from goldenverba.ingestion.preprocess import (
    load_directory,
    convert_files,
    chunk_docs,
    load_file,
    load_suggestions,
)

from goldenverba.ingestion.schema.schema_generation import (
    init_cache,
    init_documents,
    init_suggestion,
)

from dotenv import load_dotenv

load_dotenv()


def import_data(path_str: str, model: str):
    data_path = Path(path_str)
    msg.divider("Starting data import")

    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    # Setup Client
    client = setup_client()

    if not client:
        msg.fail("Client setup failed")
        return

    if not client.schema.exists("Document"):
        init_documents()
    if not client.schema.exists("Cache"):
        init_cache()
    if not client.schema.exists("Suggestion"):
        init_suggestion()

    msg.info("All schemas available")

    file_contents = {}
    suggestions = []
    if data_path.is_file():
        if data_path.suffix == ".json":
            suggestions = load_suggestions(data_path)
        else:
            file_contents = load_file(data_path)
    else:
        file_contents = load_directory(data_path)

    if file_contents:
        documents = convert_files(client, file_contents, nlp=nlp)
        if documents:
            chunks = chunk_docs(documents, nlp)
            uuid_map = import_documents(client=client, documents=documents)
            import_chunks(client=client, chunks=chunks, doc_uuid_map=uuid_map)

    elif suggestions:
        import_suggestions(client=client, suggestions=suggestions)

    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()
