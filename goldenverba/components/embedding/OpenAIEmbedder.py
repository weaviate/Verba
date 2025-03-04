import os
import json
from typing import List
import io

import aiohttp
from wasabi import msg

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token


class OpenAIEmbedder(Embedding):
    """OpenAIEmbedder for Verba."""

    def __init__(self):
        super().__init__()
        self.name = "OpenAI"
        self.description = "Vectorizes documents and queries using OpenAI"

        # If a different key is set for the OpenAI embedding, use it
        api_key = get_token("OPENAI_EMBED_API_KEY")
        api_key = api_key if api_key else get_token("OPENAI_API_KEY")

        # Fetch available models
        base_url = os.getenv("OPENAI_EMBED_BASE_URL")
        base_url = (
            base_url
            if base_url
            else os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        models = self.get_models(api_key, base_url)

        # Set up configuration
        default_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        self.config = {
            "Model": InputConfig(
                type="dropdown",
                value=default_model,
                description="Select an OpenAI Embedding Model",
                values=models,
            )
        }

        # Add API Key and URL configs if not set in environment
        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="OpenAI API Key (or set OPENAI_EMBED_API_KEY or OPENAI_API_KEY env var)",
                values=[],
            )
        if (
            os.getenv("OPENAI_EMBED_BASE_URL") is None
            and os.getenv("OPENAI_BASE_URL") is None
        ):
            self.config["URL"] = InputConfig(
                type="text",
                value=base_url,
                description="OpenAI API Base URL (if different from default)",
                values=[],
            )

    async def vectorize(self, config: dict, content: List[str]) -> List[List[float]]:
        """Vectorize the input content using OpenAI's API."""
        model = config.get("Model", {"value": "text-embedding-ada-002"}).value
        key_name = (
            "OPENAI_EMBED_API_KEY"
            if get_token("OPENAI_EMBED_API_KEY")
            else "OPENAI_API_KEY"
        )
        api_key = get_environment(
            config, "API Key", key_name, "No OpenAI API Key found"
        )
        base_url_name = (
            "OPENAI_EMBED_BASE_URL"
            if os.getenv("OPENAI_EMBED_BASE_URL")
            else "OPENAI_BASE_URL"
        )
        base_url = get_environment(config, "URL", base_url_name, "No OpenAI URL found")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {"input": content, "model": model}

        # Convert payload to BytesIO object
        payload_bytes = json.dumps(payload).encode("utf-8")
        payload_io = io.BytesIO(payload_bytes)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{base_url}/embeddings",
                    headers=headers,
                    data=payload_io,
                    timeout=30,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if "data" not in data:
                        raise ValueError(f"Unexpected API response: {data}")

                    embeddings = [item["embedding"] for item in data["data"]]
                    if len(embeddings) != len(content):
                        raise ValueError(
                            f"Mismatch in embedding count: got {len(embeddings)}, expected {len(content)}"
                        )

                    return embeddings

            except aiohttp.ClientError as e:
                if isinstance(e, aiohttp.ClientResponseError) and e.status == 429:
                    raise Exception("Rate limit exceeded. Waiting before retrying...")
                raise Exception(f"API request failed: {str(e)}")

            except Exception as e:
                msg.fail(f"Unexpected error: {type(e).__name__} - {str(e)}")
                raise

    @staticmethod
    def get_models(token: str, url: str) -> List[str]:
        """Fetch available embedding models from OpenAI API."""
        try:
            if token is None:
                return [
                    "text-embedding-ada-002",
                    "text-embedding-3-small",
                    "text-embedding-3-large",
                ]

            import requests  # Import here to avoid dependency if not needed

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{url}/models", headers=headers)
            response.raise_for_status()
            fetch_models = [model["id"] for model in response.json()["data"]]
            if not os.getenv("OPENAI_CUSTOM_EMBED", False):
                # this is not a custom OpenAI so we can filter out non-embedding OpenAI models
                fetch_models = [
                    model_id for model_id in fetch_models if "embedding" in model_id
                ]
            return fetch_models
        except Exception as e:
            msg.info(f"Failed to fetch OpenAI embedding models: {str(e)}")
            return [
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "text-embedding-3-large",
            ]
