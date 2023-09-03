import glob
import os
import json

from goldenverba.ingestion.util import hash_string

from spacy.tokens import Doc
from spacy.language import Language

from weaviate import Client

from pathlib import Path

from wasabi import msg  # type: ignore[import]

# Chunking


def chunk_docs(
    raw_docs: list[Doc],
    nlp: Language,
    split_length: int = 150,
    split_overlap: int = 50,
) -> list[Doc]:
    """Splits a list of docs into smaller chunks
    @parameter raw_docs : list[Doc] - List of docs
    @parameter split_length : int - Chunk length (words, sentences, paragraphs)
    @parameter split_overlap : int - Overlapping words, sentences, paragraphs
    @returns list[Doc] - List of splitted docs
    """
    msg.info("Starting splitting process")
    chunked_docs = []
    for doc in raw_docs:
        chunked_docs += chunk_doc(doc, nlp, split_length, split_overlap)
    msg.good(f"Successful splitting (total {len(chunked_docs)})")
    return chunked_docs


def chunk_doc(
    doc: Doc, nlp: Language, split_length: int, split_overlap: int
) -> list[Doc]:
    """Splits a doc into smaller chunks
    @parameter doc : Doc - spaCy Doc
    @parameter nlp : Language - spaCy NLP object
    @parameter split_length : int - Chunk length (words, sentences, paragraphs)
    @parameter split_overlap : int - Overlapping words, sentences, paragraphs
    @returns list[Doc] - List of chunks from original doc
    """
    if split_length > len(doc) or split_length < 1:
        return []

    if split_overlap >= split_length:
        return []

    doc_chunks = []
    i = 0
    split_id_counter = 0
    while i < len(doc):
        start_idx = i
        end_idx = i + split_length
        if end_idx > len(doc):
            end_idx = len(doc)  # Adjust for the last chunk

        doc_chunk = nlp.make_doc(doc[start_idx:end_idx].text)
        doc_chunk.user_data = doc.user_data.copy()
        doc_chunk.user_data["_split_id"] = split_id_counter
        split_id_counter += 1

        doc_chunks.append(doc_chunk)

        # Exit loop if this was the last possible chunk
        if end_idx == len(doc):
            break

        i += split_length - split_overlap  # Step forward, considering overlap

    return doc_chunks


# Loading Files from Directory


def load_suggestions(file_path: Path) -> dict:
    """Loads json file with suggestions

    @param dir_path : Path - Path to directory
    @returns dict - Dictionary of filename (key) and their content (value)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check if data is a list
    if not isinstance(data, list):
        msg.warn(f"{file_path} is not a list.")
        return []

    # Check if every item in the list is a string
    if not all(isinstance(item, str) for item in data):
        msg.warn(f"{file_path} is not a list of strings.")
        return []

    return data


def load_file(file_path: Path) -> dict:
    """Loads text file

    @param dir_path : Path - Path to directory
    @returns dict - Dictionary of filename (key) and their content (value)
    """
    file_contents = {}
    file_types = ["txt", "md", "mdx"]

    if file_path.suffix not in file_types:
        msg.warn(f"{file_path.suffix} not supported")
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        msg.info(f"Reading {str(file_path)}")
        file_contents[str(file_path)] = f.read()
    msg.good(f"Loaded {len(file_contents)} files")
    return file_contents


def load_directory(dir_path: Path) -> dict:
    """Loads text files from a directory and its subdirectories.

    @param dir_path : Path - Path to directory
    @returns dict - Dictionary of filename (key) and their content (value)
    """
    # Initialize an empty dictionary to store the file contents
    file_contents = {}

    # Convert dir_path to string, in case it's a Path object
    dir_path_str = str(dir_path)

    # Create a list of file types you want to read
    file_types = ["txt", "md", "mdx"]

    # Loop through each file type
    for file_type in file_types:
        # Use glob to find all the files in dir_path and its subdirectories matching the current file_type
        files = glob.glob(f"{dir_path_str}/**/*.{file_type}", recursive=True)

        # Loop through each file
        for file in files:
            msg.info(f"Reading {str(file)}")
            with open(file, "r", encoding="utf-8") as f:
                # Read the file and add its content to the dictionary
                file_contents[str(file)] = f.read()

    msg.good(f"Loaded {len(file_contents)} files")
    return file_contents


# Creating spaCy Documents


def convert_files(
    client: Client, files: dict, nlp: Language, doc_type: str = "Documentation"
) -> list[Doc]:
    """Converts list of strings to list of Documents
    @parameter files : dict - Dictionary with filenames and their content
    @parameter nlp : dict - A NLP Language model
    @parameter doc_type : str - Document type (code, blogpost, podcast)
    @returns list[Doc] - A list of spaCy documents
    """
    raw_docs = []
    for file_name in files:
        doc = nlp(text=files[file_name])
        doc.user_data = {
            "doc_name": file_name,
            "doc_hash": hash_string(file_name),
            "doc_type": doc_type,
            "doc_link": "",
        }
        msg.info(f"Converted {doc.user_data['doc_name']}")
        if not check_if_file_exits(client, file_name):
            raw_docs.append(doc)
        else:
            msg.warn(f"{file_name} already exists in database")

    msg.good(f"All {len(raw_docs)} files successfully loaded")

    return raw_docs


def check_if_file_exits(client: Client, doc_name: str) -> bool:
    results = (
        client.query.get(
            class_name="Document",
            properties=[
                "doc_name",
            ],
        )
        .with_where(
            {
                "path": ["doc_name"],
                "operator": "Equal",
                "valueText": doc_name,
            }
        )
        .with_limit(1)
        .do()
    )

    if results["data"]["Get"]["Document"]:
        return True
    else:
        return False
