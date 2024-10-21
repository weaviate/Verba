import os
import json
import aiohttp
from typing import List, Dict, AsyncGenerator

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.embedding.CohereEmbedder import get_models
from goldenverba.components.util import get_environment, get_token


class CohereGenerator(Generator):
    """
    CohereGenerator Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "Cohere"
        self.description = "Generator using Cohere's command-r-plus model"
        self.url = os.getenv("COHERE_BASE_URL", "https://api.cohere.com/v1")
        self.context_window = 10000

        models = get_models(self.url, get_token("COHERE_API_KEY", None), "chat")

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

    async def generate_stream(
        self,
        config: Dict,
        query: str,
        context: str,
        conversation: List[Dict] = [],
    ) -> AsyncGenerator[Dict, None]:
        model = config.get("Model").value
        api_key = get_environment(
            config, "API Key", "COHERE_API_KEY", "No Cohere API Key found"
        )

        if api_key is None:
            yield self._error_response("Missing Cohere API Key")
            return

        system_message = config.get("System Message").value

        message, chat_history = self._prepare_messages(
            query, context, conversation, system_message
        )

        data = {
            "model": model,
            "chat_history": chat_history,
            "message": message,
            "stream": True,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url + "/chat", json=data, headers=headers
                ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line.strip():
                                yield self._process_response(line)
                    else:
                        error_message = await response.text()
                        yield self._error_response(
                            f"HTTP Error {response.status}: {error_message}"
                        )

        except Exception as e:
            yield self._error_response(str(e))

    def _prepare_messages(
        self,
        query: str,
        context: str,
        conversation: List[Dict],
        system_message: str,
    ) -> tuple[str, List[Dict]]:
        """Prepare the message and chat history for the Cohere API request."""
        chat_history = [
            {
                "role": "CHATBOT",
                "message": system_message,
            }
        ]

        for message in conversation:
            _type = "CHATBOT" if message.type == "system" else "USER"
            chat_history.append({"role": _type, "message": message.content})

        message = (
            f"With this provided context: {context} Please answer this query: {query}"
        )

        return message, chat_history

    @staticmethod
    def _process_response(line: bytes) -> Dict:
        """Process a single line of response from the Cohere API."""
        json_data = json.loads(line.decode("utf-8"))
        return {
            "message": json_data.get("text", ""),
            "finish_reason": (
                "stop" if json_data.get("finish_reason", "") == "COMPLETE" else ""
            ),
        }

    @staticmethod
    def _error_response(message: str) -> Dict:
        """Return an error response."""
        return {"message": message, "finish_reason": "stop"}
