import os
import requests
from wasabi import msg
import aiohttp

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment


class WeaviateEmbedder(Embedding):

    def __init__(self):
        super().__init__()
        self.name = "Weaviate"
        self.description = f"Vectorizes documents and queries using Weaviate's In-House Embedding Service."
        models = ["Embedding Service"]

        api_key = os.getenv("EMBEDDING_SERVICE_KEY")
        base_url = os.getenv(
            "EMBEDDING_SERVICE_URL", ""
        )  # Provide empty string as default

        self.config = {
            "Model": InputConfig(
                type="dropdown",
                value=models[0],
                description=f"Select a Weaviate Embedding Service Model",
                values=models,
            ),
        }

        if api_key == None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Weaviate Embedding Service Key (or set EMBEDDING_SERVICE_KEY env var)",
                values=[],
            )
        if base_url == "":
            self.config["URL"] = InputConfig(
                type="text",
                value="",  # Use empty string as default value
                description="Weaviate Embedding Service URL (if different from default)",
                values=[],
            )

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:

        api_key = get_environment(
            config,
            "API Key",
            "EMBEDDING_SERVICE_KEY",
            "No Weaviate Embedding Service Key found",
        )
        base_url = get_environment(
            config,
            "URL",
            "EMBEDDING_SERVICE_URL",
            "No Weaviate Embedding Service URL found",
        )

        path = "/v1/embeddings/embed"

        data = {"is_search_query": False, "texts": content}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                base_url + path, json=data, headers={"Authorization": f"{api_key}"}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                embeddings = data.get("embeddings", [])
                return embeddings
