import os
from dotenv import load_dotenv
import json
import aiohttp
import requests
from wasabi import msg

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

load_dotenv()

ANYAPI_BASE_URL = "https://api.anyapi.ai/v1"
DEFAULT_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "anthropic/claude-sonnet-4-20250514",
    "google/gemini-2.5-pro",
    "meta/llama-4-maverick",
    "deepseek/deepseek-v3",
    "deepseek/deepseek-r1",
]


class AnyAPIGenerator(Generator):
    """
    AnyAPI Generator using AnyAPI's OpenAI-compatible chat API.

    AnyAPI is a unified AI platform that provides access to hundreds of
    AI models from leading providers (OpenAI, Anthropic, Google, Meta,
    DeepSeek, and more) through a single API endpoint.

    Reference: https://docs.anyapi.ai
    """

    def __init__(self):
        super().__init__()
        self.name = "AnyAPI"
        self.description = (
            "Use AnyAPI's unified API to access hundreds of AI models "
            "from OpenAI, Anthropic, Google, Meta, DeepSeek, and more "
            "through a single endpoint. See https://anyapi.ai/models."
        )
        self.context_window = 10000

        api_key = get_token("ANYAPI_API_KEY")
        base_url = os.getenv("ANYAPI_BASE_URL", ANYAPI_BASE_URL)
        models = self.get_models(api_key, base_url)
        default_model = os.getenv("ANYAPI_MODEL", models[0])

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=default_model,
            description="Select an AnyAPI model",
            values=models,
        )

        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description=(
                    "You can set your AnyAPI API Key here or set it as "
                    "environment variable `ANYAPI_API_KEY`. Get one at "
                    "https://anyapi.ai."
                ),
                values=[],
            )

        if os.getenv("ANYAPI_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value=ANYAPI_BASE_URL,
                description=(
                    "AnyAPI OpenAI-compatible base URL. The `/v1` suffix is "
                    "required."
                ),
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
        model = config.get("Model", {"value": DEFAULT_MODELS[0]}).value
        api_key = get_environment(
            config,
            "API Key",
            "ANYAPI_API_KEY",
            "No AnyAPI API Key found",
        )
        base_url = get_environment(
            config,
            "URL",
            "ANYAPI_BASE_URL",
            ANYAPI_BASE_URL,
        ).rstrip("/")

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

        async with aiohttp.ClientSession() as client:
            async with client.post(
                url=f"{base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=None,
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line.strip():
                            line = line.decode("utf-8").strip()
                            if line == "data: [DONE]":
                                yield {"message": "", "finish_reason": "stop"}
                            else:
                                if line.startswith("data:"):
                                    line = line[5:].strip()
                                json_line = json.loads(line)
                                choice = json_line.get("choices")[0]
                                yield {
                                    "message": choice.get("delta", {}).get(
                                        "content", ""
                                    ),
                                    "finish_reason": (
                                        "stop"
                                        if choice.get("finish_reason", "") == "stop"
                                        else ""
                                    ),
                                }
                else:
                    error_message = await response.text()
                    yield {
                        "message": f"HTTP Error {response.status}: {error_message}",
                        "finish_reason": "stop",
                    }

    def prepare_messages(
        self, query: str, context: str, conversation: list[dict], system_message: str
    ) -> list[dict]:
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

    def get_models(self, token: str | None, url: str) -> list[str]:
        try:
            if token is None:
                return DEFAULT_MODELS

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{url.rstrip('/')}/models", headers=headers, timeout=10
            )
            response.raise_for_status()
            models = sorted(
                {
                    model.get("id")
                    for model in response.json().get("data", [])
                    if model.get("id")
                }
            )
            return models if models else DEFAULT_MODELS
        except Exception as e:
            msg.info(f"Failed to fetch AnyAPI models: {str(e)}")
            return DEFAULT_MODELS