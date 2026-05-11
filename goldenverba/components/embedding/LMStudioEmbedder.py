import os
from typing import List

import aiohttp
from wasabi import msg

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token


class LMStudioEmbedder(Embedding):
    """LM Studio Embedder for Verba - Compatible with LM Studio's OpenAI-compatible API."""

    def __init__(self):
        super().__init__()
        self.name = "LM Studio"
        self.description = "Vectorizes documents and queries using LM Studio's locally hosted embedding models"

        # Default LM Studio configuration
        api_key = get_token("LMSTUDIO_API_KEY") or "lm-studio"
        base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        
        # Fetch available models
        models = self.get_models(api_key, base_url)
        default_model = os.getenv("LMSTUDIO_EMBED_MODEL", models[0] if models else "local-embedding")

        # Set up configuration
        self.config = {
            "Model": InputConfig(
                type="dropdown",
                value=default_model,
                description="Select a LM Studio Embedding Model",
                values=models,
            ),
            "URL": InputConfig(
                type="text",
                value=base_url,
                description="LM Studio API Base URL (default: http://localhost:1234/v1)",
                values=[],
            )
        }

        # Add API Key config if not set in environment
        if get_token("LMSTUDIO_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="lm-studio",
                description="LM Studio API Key (often not required, default: 'lm-studio')",
                values=[],
            )

    async def vectorize(self, config: dict, content: List[str]) -> List[List[float]]:
        """Vectorize the input content using LM Studio's API."""
        model = config.get("Model", {"value": "local-embedding"}).value
        api_key = get_environment(
            config, "API Key", "LMSTUDIO_API_KEY", "lm-studio"
        )
        base_url = get_environment(
            config, "URL", "LMSTUDIO_BASE_URL", "http://localhost:1234/v1"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        payload = {"input": content, "model": model}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{base_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"LM Studio API error {response.status}: {error_text}")
                    
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
                raise Exception(f"LM Studio API request failed: {str(e)}")

            except Exception as e:
                msg.fail(f"LM Studio embedding error: {type(e).__name__} - {str(e)}")
                raise

    @staticmethod
    def get_models(token: str, url: str) -> List[str]:
        """Fetch available embedding models from LM Studio API."""
        default_models = ["local-embedding"]
        try:
            import requests

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{url}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                if "data" in models_data:
                    # Get all models - LM Studio may not differentiate embedding vs chat models in the API
                    available_models = [model["id"] for model in models_data["data"]]
                    # Filter for embedding models if possible (some models have 'embed' in the name)
                    embedding_models = [m for m in available_models if 'embed' in m.lower()]
                    
                    # Return embedding models if found, otherwise return all models
                    return embedding_models if embedding_models else available_models
            
            msg.info("Could not fetch embedding models from LM Studio, using default")
            return default_models
            
        except Exception as e:
            msg.info(f"Failed to fetch LM Studio embedding models: {str(e)}")
            return default_models
