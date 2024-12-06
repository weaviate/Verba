import os
import json
from typing import List
import io

import aiohttp
from wasabi import msg

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token


class UpstageEmbedder(Embedding):
    """UpstageEmbedder for Verba."""

    def __init__(self):
        super().__init__()
        self.name = "Upstage"
        self.description = (
            "Vectorizes documents and queries using Upstage Solar Embeddings"
        )
        self.max_batch_size = 100

        # Fetch available models
        api_key = get_token("UPSTAGE_API_KEY")
        base_url = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1/solar")

        # Set up configuration
        self.config = {
            "Model": InputConfig(
                type="dropdown",
                value="embedding-query",
                description="Select an Upstage Embedding Model",
                values=["embedding-query", "embedding-passage"],
            )
        }

        # Add API Key and URL configs if not set in environment
        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Upstage API Key (or set UPSTAGE_API_KEY env var)",
                values=[],
            )
        if os.getenv("UPSTAGE_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value=base_url,
                description="Upstage API Base URL (if different from default)",
                values=[],
            )

    async def vectorize(self, config: dict, content: List[str]) -> List[List[float]]:
        """Vectorize the input content using Upstage's API."""
        model = config.get("Model", {"value": "embedding-query"}).value
        api_key = get_environment(
            config, "API Key", "UPSTAGE_API_KEY", "No Upstage API Key found"
        )
        base_url = get_environment(
            config, "URL", "UPSTAGE_BASE_URL", "No Upstage URL found"
        )

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
        """Return available embedding models for Upstage."""
        # Upstage currently has two fixed models
        return ["embedding-query", "embedding-passage"]
