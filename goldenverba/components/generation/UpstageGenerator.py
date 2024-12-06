import os
from dotenv import load_dotenv
from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token
import httpx
import json

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

load_dotenv()

class UpstageGenerator(Generator):
    """
    Upstage Generator.
    """

    DEFAULT_BASE_URL = "https://api.upstage.ai/v1/solar"
    MODELS = ["solar-pro", "solar-mini"]
    DEFAULT_MODEL = "solar-pro"
    CONTEXT_WINDOW = 4096

    def __init__(self):
        super().__init__()
        self.name = "Upstage"
        self.description = "Using Upstage Solar LLM models for advanced text generation"
        self.context_window = self.CONTEXT_WINDOW

        models = self.MODELS

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=models[0],
            description="Select an Upstage Solar Model",
            values=models,
        )

        if get_token("UPSTAGE_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your Upstage API Key here or set it as environment variable `UPSTAGE_API_KEY`",
                values=[],
            )
        if os.getenv("UPSTAGE_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value=self.DEFAULT_BASE_URL,
                description="You can change the Base URL here if needed",
                values=[],
            )

    async def generate_stream(
        self,
        config: dict,
        query: str,
        context: str,
        conversation: list[dict] = [],
    ):
        system_message = config.get("System Message").value
        model = config.get("Model", {"value": self.DEFAULT_MODEL}).value
        api_key = get_environment(
            config, "API Key", "UPSTAGE_API_KEY", "Upstage API Key not found"
        )
        base_url = get_environment(
            config, "URL", "UPSTAGE_BASE_URL", self.DEFAULT_BASE_URL
        )

        messages = self.prepare_messages(query, context, conversation, system_message)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        data = {
            "messages": messages,
            "model": model,
            "stream": True,
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=None,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            break
                        json_line = json.loads(line[6:])
                        choice = json_line["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            yield {
                                "message": choice["delta"]["content"],
                                "finish_reason": choice.get("finish_reason"),
                            }
                        elif "finish_reason" in choice:
                            yield {
                                "message": "",
                                "finish_reason": choice["finish_reason"],
                            }

    def prepare_messages(
        self, query: str, context: str, conversation: list[dict], system_message: str
    ) -> list[dict]:
        """
        Prepare the message structure for the API request.

        Args:
            query: The user's query
            context: Context information
            conversation: Conversation history
            system_message: System instructions

        Returns:
            List of formatted messages for the API request
        """
        messages = [
            {
                "role": "system",
                "content": system_message,
            }
        ]

        for message in conversation:
            messages.append({"role": message.type, "content": message.content})

        messages.append(
            {
                "role": "user",
                "content": f"Answer this query: '{query}' with this provided context: {context}",
            }
        )

        return messages
