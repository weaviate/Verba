import glob
import os
import json

from goldenverba.ingestion.util import hash_string

from spacy.tokens import Doc
from spacy.language import Language

from weaviate import Client

from pathlib import Path

from wasabi import msg  # type: ignore[import]


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
