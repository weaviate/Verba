import os
import requests
from wasabi import msg
import aiohttp

from goldenverba.components.interfaces import Embedder
from goldenverba.components.types import InputConfig


class OllamaEmbedder(Embedder):

    def __init__(self):
        super().__init__()
        self.name = "Ollama"
        self.description = "Vectorizes documents and queries using Ollama"
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        models = self.get_models(self.url)

        self.config = {
            "Model": InputConfig(
                type="dropdown", value=models[0], description=f"Select a installed Ollama model from {self.url}. You can change the URL by setting the OLLAMA_URL environment variable. ", values=models
            ),
        }

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:
        model = config.get("Model").value
        data = {"model": model, "input": content}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + "/api/embed", json=data) as response:
                response.raise_for_status()
                data = await response.json()
                embeddings = data.get("embeddings", [])
                return embeddings


    def get_models(self, url: str):
        try:
            response = requests.get(url+"/api/tags")
            models = [model.get("name") for model in response.json().get("models")]
            if len(models) > 0:
                return models
            else:
                msg.info("No Ollama Model detected")
                return ["No Model Installed"]
        except Exception as e:
            msg.info("Couldn't connect to Ollama")
            return ["Couldn't connect to Ollama"]
        