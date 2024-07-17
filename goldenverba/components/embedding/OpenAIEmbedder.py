import os
import json
import requests

from goldenverba.components.interfaces import Embedding
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig

class OpenAIEmbedder(Embedding):
    """
    OpenAIEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "OpenAI"
        self.requires_env = ["OPENAI_API_KEY"]
        self.description = "Vectorizes documents and queries using OpenAI"
        self.config = {
            "Model": InputConfig(
                type="dropdown", value="text-embedding-ada-002", description="Select an OpenAI Embedding Model", values=["text-embedding-ada-002","text-embedding-3-small","text-embedding-3-large"]
            ),
            "URL": InputConfig(
                type="text",
                value="https://api.openai.com/v1/embeddings",
                description="You can change the Base URL here if needed", values=[]
            ),
        }

    async def vectorize(self, config: dict, content: list[str]) -> list[float]:
        url = config.get("URL", {"value": "https://api.openai.com/v1/embeddings"}).value
        model = config.get("Model", {"value": "text-embedding-ada-002"}).value
        OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)
        if OPENAI_KEY is not None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}"
            }
            data = {
                "input": content,
                "model": model
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    if len(data["data"]) == len(content):
                        return data["data"]
                    else:
                        raise Exception(f"Embedding length does not match number of content: {len(data['data'])}/{len(content)}")
                else:
                    raise Exception(f"Payload does not contain information: {data}")
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        else:
            raise Exception("No OpenAI API Key found")
