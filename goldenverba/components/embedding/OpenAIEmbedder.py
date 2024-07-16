import os
import json
import requests

from goldenverba.components.interfaces import Embedding
from goldenverba.components.document import Document

class OpenAIEmbedder(Embedding):
    """
    OpenAIEmbedder for Verba.
    """

    def __init__(self):
        super().__init__()
        self.name = "OpenAIEmbedder"
        self.requires_env = ["OPENAI_API_KEY"]
        self.model = "text-embedding-ada-002"

    async def vectorize(self, config: dict, document: Document) -> Document:
        """Embed verba documents and its chunks to Weaviate
        @parameter: documents : list[Document] - List of Verba documents
        @parameter: client : Client - Weaviate Client
        @parameter: batch_size : int - Batch Size of Input
        @returns bool - Bool whether the embedding what successful.
        """
        url = "https://api.openai.com/v1/embeddings"
        OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)
        if OPENAI_KEY is not None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}"
            }
            data = {
                "input": [chunk.content for chunk in document.chunks],
                "model": self.model
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    if len(data["data"]) == len(document.chunks):
                        for vector, chunk in zip(data["data"],document.chunks):
                            chunk.vector = vector
                        return document
                    else:
                        raise Exception(f"Embedding length does not match number of chunks: {len(data['data'])}/{len(document.chunks)}")
                else:
                    raise Exception(f"Payload does not contain information: {data}")
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        else:
            raise Exception("No OpenAI API Key found")
