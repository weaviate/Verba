import json
import os
import httpx

from dotenv import load_dotenv

from collections.abc import AsyncIterator
from goldenverba.server.types import ConversationItem, GeneratedMessage

load_dotenv()


class OllamaGenerator:
    """
    Ollama Generator.
    """

    def __init__(self):
        super().__init__()
        self.requires_env = ["OLLAMA_API_URL", "OLLAMA_MODEL"]
        self.model_name = os.getenv("OLLAMA_MODEL")
        self.name = f"OllamaGenerator - {self.model_name}"
        self.description = (
            f"Generator using the Ollama API with {self.model_name} model"
        )
        self.requires_library = ["httpx"]
        self.streamable = True
        self.context_window = 10000

    async def generate(
        self,
        query: str,
        context: list[str],
        history: list[ConversationItem] = None,
    ) -> str:
        messages = self.prepare_messages(query, context, history)
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
        }

        try:
            async with httpx.Client() as client:
                response = await client.post(
                    f"{os.getenv('OLLAMA_API_URL')}/chat", json=payload, timeout=None
                )
                response.raise_for_status()
                completion = response.json()
                return completion.get("message").get("content")
        except Exception:
            raise

    async def generate_stream(
        self,
        query: str,
        context: list[str],
        history: list[ConversationItem] = None,
    ) -> AsyncIterator[GeneratedMessage]:
        messages = self.prepare_messages(query, context, history)
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    'POST', f"{os.getenv('OLLAMA_API_URL')}/chat", json=payload, timeout=None
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            payload = json.loads(line)
                            message = payload.get("message").get("content")
                            yield {
                                "message": message,
                                "finish_reason": payload.get("done") and "stop" or None,
                            }
        except Exception:
            raise

    def prepare_messages(
        self, query: str, context: list[str], history: list[ConversationItem]
    ) -> [dict[str, str]]:
        preprompt = [
            "You are a Retrieval Augmented Generation chatbot.",
            "Please answer user query only their provided context.",
            "If the provided documentation does not provide enough information, say so.",
            "If the answer requires code examples encapsulate them with ```programming-language-name ```.",
            "Don't do pseudo-code.",
            "Reply in english.",
            "Be precise and concise.",
        ]

        messages = [
            {"role": "system", "content": " ".join(preprompt)},
            {
                "role": "user",
                "content": f"Please answer this query: '{query}' with this provided context: {' --- '.join(context)}",
            },
        ]

        return messages
