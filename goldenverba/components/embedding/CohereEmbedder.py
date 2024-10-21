import os
import requests
import aiohttp
import json

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

from wasabi import msg


class CohereEmbedder(Embedding):
    """
    CohereEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "Cohere"
        self.description = "Vectorizes documents and queries using Cohere"
        self.url = os.getenv("COHERE_BASE_URL", "https://api.cohere.com/v1")
        models = get_models(self.url, get_token("COHERE_API_KEY", None), "embed")

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=models[0] if models else "",
            description="Select a Cohere Embedding Model",
            values=models if models else [],
        )

        if get_token("COHERE_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your Cohere API Key here or set it as environment variable `COHERE_API_KEY`",
                values=[],
            )

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:
        model = config.get("Model", "embed-english-v3.0").value
        api_key = get_environment(
            config, "API Key", "COHERE_API_KEY", "No Cohere API Key found"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"bearer {api_key}",
        }

        # Function to split the content into chunks of up to 96 texts
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i : i + n]

        all_embeddings = []

        async with aiohttp.ClientSession() as session:
            for chunk in chunks(content, 96):
                data = {"texts": chunk, "model": model, "input_type": "search_document"}
                async with session.post(
                    self.url + "/embed", data=json.dumps(data), headers=headers
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    embeddings = response_data.get("embeddings", [])
                    all_embeddings.extend(embeddings)

        return all_embeddings


def get_models(url: str, token: str, model_type: str):
    try:
        if token is None or token == "":
            return [
                "embed-english-v3.0",
                "embed-multilingual-v3.0",
                "embed-english-light-v3.0",
                "embed-multilingual-light-v3.0",
            ]
        headers = {"Authorization": f"bearer {token}"}
        response = requests.get(url + "/models", headers=headers)
        data = response.json()
        if "models" in data:
            return [
                model["name"]
                for model in data["models"]
                if model_type in model["endpoints"]
            ]
    except Exception as e:
        msg.warn(f"Couldn't fetch models from Cohere endpoint: {e}")
        return [
            "embed-english-v3.0",
            "embed-multilingual-v3.0",
            "embed-english-light-v3.0",
            "embed-multilingual-light-v3.0",
        ]
