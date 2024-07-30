import os
import json
import requests
import httpx

from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment

class OpenAIEmbedder(Embedding):
    """
    OpenAIEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "OpenAI"
        self.description = "Vectorizes documents and queries using OpenAI"

        models = self.get_models(os.getenv("OPENAI_API_KEY", None), os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))

        self.config = {
            "Model": InputConfig(
                type="dropdown", value="text-embedding-3-small", description="Select an OpenAI Embedding Model", values=models
            )
        }

        if os.getenv("OPENAI_API_KEY") is None:
            self.config["API Key"] = InputConfig(type="password",value="",description="You can set your OpenAI API Key here or set it as environment variable `OPENAI_API_KEY`", values=[])
        if os.getenv("OPENAI_BASE_URL") is None:
            self.config["URL"] = InputConfig(type="text",value="https://api.openai.com/v1",description="You can change the Base URL here if needed", values=[])

    

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:

        model = config.get("Model", {"value": "text-embedding-ada-002"}).value
        OPENAI_KEY = get_environment(config, "API Key", "OPENAI_API_KEY", "No OpenAI API Key found" )
        OPENAI_URL = get_environment(config, "URL", "OPENAI_BASE_URL", "No OpenAI URL found" )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_KEY}"
        }
        data = {
            "input": content,
            "model": model
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENAI_URL+"/embeddings", headers=headers, content=json.dumps(data))
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

        
    def get_models(self, token: str, url: str):
        if token is None:
            return ["text-embedding-ada-002","text-embedding-3-small","text-embedding-3-large"]
        headers = {
                "Authorization": f"Bearer {token}"
            }    
        response = requests.get(url+"/models", headers=headers)
        return [model["id"] for model in response.json()["data"] if "embedding" in model["id"]]
        

