import os
from pathlib import Path

from wasabi import msg  # type: ignore[import]

import spacy

from verba_rag.ingestion.util import (
    setup_client,
    import_documents,
    import_chunks,
)
from verba_rag.ingestion.preprocess import load_directory, convert_files, chunk_docs

from dotenv import load_dotenv

load_dotenv()


def import_data(dir_path: Path):
    msg.divider("Starting data import")

    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    # Setup Client
    client = setup_client()

    if not client:
        msg.fail("Client setup failed")
        return

    file_contents = load_directory(dir_path)
    documents = convert_files(file_contents, nlp=nlp)
    chunks = chunk_docs(documents, nlp)

    uuid_map = import_documents(client=client, documents=documents)
    import_chunks(client=client, chunks=chunks, doc_uuid_map=uuid_map)
