import os
import glob
from pathlib import Path

from wasabi import msg  # type: ignore[import]

from haystack.schema import Document
from weaviate import Client

from verba.ingestion.util import download_nltk, setup_client
from verba.ingestion.preprocess import load_directory, convert_files, chunking_data

from dotenv import load_dotenv

load_dotenv()


def import_documents(client: Client, documents: list[Document]) -> dict:
    """Imports a list of document to the Weaviate Client and returns a list of UUID for the chunks to match
    @parameter client : Client - Weaviate Client
    @parameter documents : list[Document] - List of whole documents
    @returns dict - The UUID list
    """
    doc_uuid_map = {}

    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(documents):
            msg.info(
                f"({i+1}/{len(documents)}) Importing document {d.meta['doc_name']}"
            )

            properties = {
                "text": str(d.content),
                "doc_name": str(d.meta["doc_name"]),
                "doc_type": str(d.meta["doc_type"]),
                "doc_link": str(d.meta["doc_link"]),
            }

            uuid = client.batch.add_data_object(properties, "Document")
            uuid_key = str(d.meta["doc_hash"]).strip().lower()
            doc_uuid_map[uuid_key] = uuid

    msg.good("Imported all docs")
    return doc_uuid_map


def import_chunks(client: Client, chunks: list[Document], doc_uuid_map: dict) -> None:
    """Imports a list of chunks to the Weaviate Client and uses a list of UUID for the chunks to match
    @parameter client : Client - Weaviate Client
    @parameter chunks : list[Document] - List of chunks of documents
    @parameter doc_uuid_map : dict  UUID list of documents the chunks belong to
    @returns None
    """
    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(chunks):
            msg.info(
                f"({i+1}/{len(chunks)}) Importing chunk of {d.meta['doc_name']} ({d.meta['_split_id']})"
            )

            uuid_key = str(d.meta["doc_hash"]).strip().lower()
            uuid = doc_uuid_map[uuid_key]

            properties = {
                "text": str(d.content),
                "doc_name": str(d.meta["doc_name"]),
                "doc_uuid": uuid,
                "doc_type": str(d.meta["doc_type"]),
                "chunk_id": int(d.meta["_split_id"]),
            }

            client.batch.add_data_object(properties, "Chunk")

    msg.good("Imported all chunks")


def import_data(dir_path: Path):
    # Ensure all NLTK requirements are set
    download_nltk()

    msg.divider("Starting data import")

    # Setup Client
    client = setup_client(
        openai_key=os.environ.get("OPENAI_API_KEY", ""),
        weaviate_url=os.environ.get("WEAVIATE_URL", ""),
        weaviate_key=os.environ.get("WEAVIATE_API_KEY", ""),
    )

    if not client:
        msg.fail("Client setup failed")
        return

    file_contents = load_directory(dir_path)
    documents = convert_files(file_contents)
    chunks = chunking_data(documents)

    uuid_map = import_documents(client=client, documents=documents)
    import_chunks(client=client, chunks=chunks, doc_uuid_map=uuid_map)
