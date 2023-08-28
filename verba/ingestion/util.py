import hashlib
import ssl

import nltk
import openai
import weaviate  # type: ignore[import]
from weaviate import Client
from typing import Optional

from wasabi import msg  # type: ignore[import]


def setup_client(
    openai_key: str, weaviate_url: str, weaviate_key: str
) -> Optional[Client]:
    """Hash a string
    @parameter openai_key : str - OpenAI API Key
    @parameter weaviate_url : str - Weaviate URL to cluster
    @parameter weaviate_key : str - Weaviate API Key
    @returns Optional[Client] - The Weaviate Client
    """

    if not openai_key:
        msg.fail("OpenAI Key not set")
        return None

    elif not weaviate_url:
        msg.fail("Weaviate URL not set")
        return None

    elif not weaviate_key:
        msg.fail("Weaviate Key not set")
        return None

    openai.api_key = openai_key
    url = weaviate_url
    auth_config = weaviate.AuthApiKey(api_key=weaviate_key)

    client = weaviate.Client(
        url=url,
        additional_headers={"X-OpenAI-Api-Key": openai.api_key},
        auth_client_secret=auth_config,
    )

    msg.good("Client connected to Weaviate Instance")

    return client


def hash_string(text: str) -> str:
    """Hash a string
    @parameter text : str - The string to hash
    @returns str - Hashed string
    """
    # Create a new sha256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the bytes-like object (filepath)
    sha256.update(text.encode())

    # Return the hexadecimal representation of the hash
    return str(sha256.hexdigest())


def download_nltk() -> None:
    """Download the needed nltk punkt package if missing"""
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download("punkt")
