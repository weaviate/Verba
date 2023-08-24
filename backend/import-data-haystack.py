import weaviate  # type: ignore[import]
import typer
import os

import hashlib

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


def clean_filename(file_path: str, document_type: str):
    if document_type == "Documentation":
        # Split the path into its components
        parts = file_path.split(os.sep)

        # Check if there are at least two parts to extract
        if len(parts) < 2:
            return None

        # Extract the last two parts
        last_two = parts[-2:]

        # Remove the file extension from the last part
        filename_without_extension = os.path.splitext(last_two[-1])[0]

        # If the filename is "index", use the last two directories as filename
        if filename_without_extension == "index":
            cleaned_name = "-".join(last_two)
        else:
            last_two[-1] = filename_without_extension
            cleaned_name = "-".join(last_two)

        # Remove numbers followed by an underscore at the beginning of each part
        cleaned_parts = [re.sub(r"^\d+_", "", part) for part in cleaned_name.split("-")]

        return "-".join(cleaned_parts)
    else:
        return file_path


def transform_to_url(file_path):
    base_url = "https://weaviate.io/"

    # Remove the file extension
    without_extension = os.path.splitext(file_path)[0]

    # Concatenate the base_url with the modified path
    full_url = os.path.join(base_url, without_extension)

    return full_url


def hash_filepath(filepath) -> str:
    # Create a new sha256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the bytes-like object (filepath)
    sha256.update(filepath.encode())

    # Return the hexadecimal representation of the hash
    return str(sha256.hexdigest())


def data_cleaning(document_str: str, document_type: str) -> str:
    """Preprocess and clean documents from mdx markings
    @parameter document_str : str - Document text
    @returns str - The preprocessed and cleaned document text
    """

    if document_type == "Documentation":
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

    return document_str


def data_filtering(document_path: str, document_type: str) -> bool:
    if document_type == "Documentation":
        # Split the document path into its components
        components = document_path.split("/")
        # Check if any component starts with '_'
        for component in components:
            if component.startswith("_"):
                msg.warn(f"Skipping {document_path}")
                return False
        return True
    else:
        return True


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
        try:
            fetched_text, link, path = download_file(owner, repo, doc_name, token)
        except Exception as e:
            msg.fail(str(e))

        if data_filtering(path, doc_type):
            doc = Document(
                content=data_cleaning(fetched_text, doc_type),
                meta={
                    "doc_name": clean_filename(str(path), doc_type),
                    "doc_hash": hash_filepath(str(path)),
                    "doc_type": doc_type,
                    "doc_link": transform_to_url(str(path)),
                },
            )
            msg.info(f"Loaded {doc.meta['doc_name']}")
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


def chunking_data(
    raw_docs: list[Document],
    split_by: str = "word",
    split_length: int = 200,
    split_overlap: int = 100,
    sentence_boundaries: bool = True,
) -> list[Document]:
    """Splits a list of docs into smaller chunks
    @parameter raw_docs : list[Document] - List of docs
    @parameter split_by : str - Chunk by words, sentences, or paragrapggs
    @parameter split_length : int - Chunk length (words, sentences, paragraphs)
    @parameter split_overlap : int - Overlapping words, sentences, paragraphs
    @parameter sentence_boundaries : bool - Respect sentence boundaries
    @returns list[Document] - List of splitted docs
    """
    msg.info("Starting splitting process")
    preprocessor = PreProcessor(
        clean_empty_lines=False,
        clean_whitespace=False,
        clean_header_footer=False,
        split_by=split_by,
        split_length=split_length,
        split_overlap=split_overlap,
        split_respect_sentence_boundary=sentence_boundaries,
    )
    chunked_docs = preprocessor.process(raw_docs)
    msg.good(f"Successful splitting (total {len(chunked_docs)})")
    return chunked_docs


def setup_client():
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
            return client
        else:
            msg.warn("Server URL not available")
            return None
    else:
        msg.warn("Open AI API Key not available")
        return None


def main() -> None:
    download_nltk()

    msg.divider("Starting data import")

    client = setup_client()

    if client:
        msg.good("Client connected to Weaviate Instance")
    else:
        return

    weaviate_documentation = download_mdx(
        "weaviate",
        "weaviate-io",
        "developers/",
        os.environ.get("GITHUB_TOKEN", ""),
        "Documentation",
    )

    weaviate_data = weaviate_documentation

    chunked_weaviate_data = chunking_data(weaviate_data)

    doc_uuid_map = {}

    # Insert whole docs
    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(weaviate_data):
            msg.info(
                f"({i+1}/{len(weaviate_data)}) Importing document {d.meta['doc_name']}"
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

    with client.batch as batch:
        batch.batch_size = 100
        for i, d in enumerate(chunked_weaviate_data):
            msg.info(
                f"({i+1}/{len(chunked_weaviate_data)}) Importing chunk of {d.meta['doc_name']} ({d.meta['_split_id']})"
            )

            uuid_key = str(d.meta["doc_hash"]).strip().lower()
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
