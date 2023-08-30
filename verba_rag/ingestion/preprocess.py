import glob
import os

from verba_rag.ingestion.util import hash_string

from spacy.tokens import Doc
from spacy.language import Language

from pathlib import Path

from wasabi import msg  # type: ignore[import]

# Chunking


def chunk_docs(
    raw_docs: list[Doc],
    nlp: Language,
    split_length: int = 200,
    split_overlap: int = 100,
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


def load_directory(dir_path: Path) -> dict:
    """Loads text files from a directory
    @parameter dir_path : Path - Path to directoy
    @returns dict - Dictionary of filename (key) and their content (value)
    """
    # Initialize an empty list to store the file contents
    file_contents = {}

    # Convert dir_path to string, in case it's a Path object
    dir_path_str = str(dir_path)

    # Create a list of file types you want to read
    file_types = ["*.txt", "*.md", "*.mdx"]

    # Loop through each file type
    for file_type in file_types:
        # Use glob to find all the files in dir_path matching the current file_type
        files = glob.glob(os.path.join(dir_path_str, file_type))

        # Loop through each file
        for file in files:
            msg.info(f"Reading {str(file)}")
            with open(file, "r", encoding="utf-8") as f:
                # Read the file and add its content to the list
                file_contents[str(file)] = f.read()

    msg.good(f"Loaded {len(file_contents)} files")
    return file_contents


# Creating spaCy Documents


def convert_files(
    files: dict, nlp: Language, doc_type: str = "Documentation"
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
        raw_docs.append(doc)

    msg.good(f"All {len(raw_docs)} files successfully loaded")

    return raw_docs
