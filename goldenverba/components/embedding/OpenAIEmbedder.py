import os
import json
import requests
import httpx

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig

class OpenAIEmbedder(Embedding):
    """
    OpenAIEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "OpenAI"
        self.description = "Vectorizes documents and queries using OpenAI"

        models = self.get_models(os.getenv("OPENAI_API_KEY", None))

        self.config = {
            "Model": InputConfig(
                type="dropdown", value="text-embedding-3-small", description="Select an OpenAI Embedding Model", values=models
            ),
            "URL": InputConfig(
                type="text",
                value="https://api.openai.com/v1/embeddings",
                description="You can change the Base URL here if needed", values=[]
            ),
            "API Key": InputConfig(
                type="password",
                value="",
                description="You can set your OpenAI API Key here or set it as environment variable `OPENAI_API_KEY`", values=[]
            ),
        }

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:
        url = config.get("URL", {"value": "https://api.openai.com/v1/embeddings"}).value
        model = config.get("Model", {"value": "text-embedding-ada-002"}).value
        API_KEY_CONFIG = config.get("API Key").value

        OPENAI_KEY = None
        if API_KEY_CONFIG == "":
            OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        else:
            OPENAI_KEY = API_KEY_CONFIG

        if OPENAI_KEY is not None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}"
            }
            data = {
                "input": content,
                "model": model
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, content=json.dumps(data))
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        if len(data["data"]) == len(content):
                            return [embedding["embedding"] for embedding in data["data"]]
                        else:
                            raise Exception(f"Embedding length does not match number of content: {len(data['data'])}/{len(content)}")
                    else:
                        raise Exception(f"Payload does not contain information: {data}")
                else:
                    raise Exception(f"Error: {response.status_code}, {response.text}")
        else:
            raise Exception("No OpenAI API Key found")
        
    def get_models(self, token: str):
        if token is None:
            return ["text-embedding-ada-002","text-embedding-3-small","text-embedding-3-large"]
        headers = {
                "Authorization": f"Bearer {token}"
            }    
        response = requests.get("https://api.openai.com/v1/models", headers=headers)
        return [model["id"] for model in response.json()["data"] if "embedding" in model["id"]]
        

