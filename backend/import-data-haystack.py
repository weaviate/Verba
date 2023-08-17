import weaviate  # type: ignore[import]
import typer
import os

import openai

from pathlib import Path
from wasabi import msg  # type: ignore[import]

import re

from haystack.nodes import TextConverter
from haystack.nodes import PreProcessor
from haystack.schema import Document

from fetch_weaviate_data import fetch_docs, download_file

from dotenv import load_dotenv

load_dotenv()


def download_nltk() -> None:
    """Download the needed nltk punkt package if missing
    @returns None
    """
    import nltk
    import ssl

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download("punkt")


def clean_mdx(document_str: str) -> str:
    """Preprocess and clean documents from mdx markings
    @parameter document_str : str - Document text
    @returns str - The preprocessed and cleaned document text
    """

    # Step 1: Remove everything above <!-- truncate -->
    text = re.sub(r"(?s)^.*?<!-- truncate -->\n?", "", document_str)

    # Step 2: Remove import statements
    text = re.sub(r"import .*?;\n?", "", text)

    # Remove all HTML-like tags
    text = re.sub(r"<[^>]+>", "", text)

    # Step 4: Remove tags with three double dots and their corresponding closing tags
    text = re.sub(r":::.*?\n", "", text)
    text = re.sub(r":::\n?", "", text)

    return text


def download_mdx(
    owner: str,
    repo: str,
    folder_path: str,
    token: str = None,
    doc_type: str = "Documentation",
) -> list[Document]:
    """Downloads .mdx files from Github
    @parameter owner : str - Repo owner
    @parameter repo : str - Repo name
    @parameter folder_path : str - Directory in repo to fetch from
    @parameter token : str - Github token
    @parameter doc_type : str - Document type (code, blogpost, podcast)
    @returns list[Document] - A list of haystack documents
    """
    msg.divider(
        f"Starting data type {doc_type} loading from {owner}/{repo}/{folder_path}"
    )
    doc_names = fetch_docs(owner, repo, folder_path, token)
    raw_docs = []
    for doc_name in doc_names:
        fetched_text, link, path = download_file(owner, repo, doc_name, token)
        doc = Document(
            content=clean_mdx(fetched_text),
            meta={"doc_name": str(path), "doc_type": doc_type, "doc_link": link},
        )
        msg.info(f"Loaded {str(path)}")
        raw_docs.append(doc)

    msg.good(f"All {len(raw_docs)} files successfully loaded")

    return raw_docs


def load_mdx(dir_path: Path, doc_type: str = "Documentation") -> list[Document]:
    """Load .mdx files from a local directory
    @parameter dir_path : Path - Directory path
    @parameter doc_type : str - Document type (code, blogpost, podcast)
    @returns list[Document] - A list of haystack documents
    """
    msg.divider("Starting data reading")
    directory = Path(dir_path)
    raw_docs = []

    for file in directory.iterdir():
        if file.suffix == ".md" or file.suffix == ".mdx":
            with open(file, "r") as reader:
                doc = reader.read()
            doc = Document(
                content=clean_mdx(doc),
                meta={
                    "doc_name": str(file),
                    "doc_type": doc_type,
                    "doc_link": str(file),
                },
            )
            msg.info(f"Loaded {str(file)}")
            raw_docs.append(doc)

    msg.good(f"All {len(raw_docs)} files successfully loaded inside {dir_path}")

    return raw_docs


def processing_data(raw_docs: list[Document]) -> list[Document]:
    """Splits a list of docs into smaller chunks
    @parameter raw_docs : list[Document] - List of docs
    @returns list[Document] - List of splitted docs
    """
    msg.info("Starting splitting process")
    preprocessor = PreProcessor(
        clean_empty_lines=False,
        clean_whitespace=False,
        clean_header_footer=False,
        split_by="sentence",
        split_length=12,
        split_overlap=4,
        split_respect_sentence_boundary=False,
    )
    chunked_docs = preprocessor.process(raw_docs)
    msg.good(f"Successful splitting (total {len(chunked_docs)})")
    return chunked_docs


def main() -> None:
    download_nltk()

    msg.divider("Starting data import")

    # Define OpenAI API key, Weaviate URL, and auth configuration
    openai.api_key = os.environ.get("OPENAI_API_KEY", "")
    url = os.environ.get("WEAVIATE_URL", "")
    auth_config = weaviate.AuthApiKey(api_key=os.environ.get("WEAVIATE_API_KEY", ""))

    # Setup OpenAI API key and Weaviate client
    if openai.api_key != "":
        msg.good("Open AI API Key available")
        if url:
            client = weaviate.Client(
                url=url,
                additional_headers={"X-OpenAI-Api-Key": openai.api_key},
                auth_client_secret=auth_config,
            )
        else:
            msg.warn("Server URL not available")
            return
    else:
        msg.warn("Open AI API Key not available")
        return

    msg.good("Client connected to Weaviate Instance")

    raw_docs = download_mdx(
        "weaviate",
        "weaviate-io",
        "developers/",
        os.environ.get("GITHUB_TOKEN", ""),
        "Code Documentation",
    )
    chunked_docs = processing_data(raw_docs)

    doc_uuid_map = {}

    # Insert whole docs
    with client.batch as batch:
        batch.batch_size = 5
        for i, d in enumerate(raw_docs):
            msg.info(f"({i+1}/{len(raw_docs)}) Importing document {d.meta['doc_name']}")

            properties = {
                "text": str(d.content),
                "doc_name": str(d.meta["doc_name"]),
                "doc_type": str(d.meta["doc_type"]),
                "doc_link": str(d.meta["doc_link"]),
            }

            uuid = client.batch.add_data_object(properties, "Document")
            uuid_key = str(d.meta["doc_name"]).strip().lower()
            doc_uuid_map[uuid_key] = uuid

    msg.good("Imported all docs")

    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(chunked_docs):
            msg.info(
                f"({i+1}/{len(chunked_docs)}) Importing chunk of {d.meta['doc_name']} ({d.meta['_split_id']})"
            )

            uuid_key = str(d.meta["doc_name"]).strip().lower()
            uuid = doc_uuid_map[uuid_key]

            properties = {
                "text": str(d.content),
                "doc_name": str(d.meta["doc_name"]),
                "doc_uuid": uuid,
                "chunk_id": int(d.meta["_split_id"]),
            }

            client.batch.add_data_object(properties, "Chunk")

    msg.good("Imported all chunks imported")


if __name__ == "__main__":
    typer.run(main)
