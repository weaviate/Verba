import glob
import os

from haystack.nodes import PreProcessor
from haystack.schema import Document
from verba.ingestion.util import hash_string

from pathlib import Path

from wasabi import msg  # type: ignore[import]

# Chunking


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


# Creating Haystack Documents


def convert_files(files: dict, doc_type: str = "Documentation") -> list[Document]:
    """Converts list of strings to list of Documents
    @parameter files : dict - Dictionary with filenames and their content
    @parameter doc_type : str - Document type (code, blogpost, podcast)
    @returns list[Document] - A list of haystack documents
    """
    raw_docs = []
    for file_name in files:
        doc = Document(
            content=files[file_name],
            meta={
                "doc_name": file_name,
                "doc_hash": hash_string(file_name),
                "doc_type": doc_type,
                "doc_link": "",
            },
        )
        msg.info(f"Converted {doc.meta['doc_name']}")
        raw_docs.append(doc)

    msg.good(f"All {len(raw_docs)} files successfully loaded")

    return raw_docs
