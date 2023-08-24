import typer
import os

from wasabi import msg  # type: ignore[import]

from haystack.schema import Document
from weaviate import Client

from util import download_nltk, setup_client
from preprocess_weaviate import retrieve_documentation, retrieve_blogs

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


def main() -> None:
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
        return

    # Download and preprocess data
    weaviate_blog, chunked_weaviate_blog = retrieve_blogs()
    weaviate_documentation, chunked_weaviate_documentation = retrieve_documentation()

    weaviate_data = weaviate_documentation + weaviate_blog
    chunked_weaviate_data = chunked_weaviate_blog + chunked_weaviate_documentation

    # Import data
    doc_uuid_map = import_documents(client, weaviate_data)
    import_chunks(client, chunked_weaviate_data, doc_uuid_map)


if __name__ == "__main__":
    typer.run(main)
