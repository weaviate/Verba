import json
import os

import httpx
from dotenv import load_dotenv
import requests
from wasabi import msg

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

load_dotenv()

ATLASCLOUD_BASE_URL = "https://api.atlascloud.ai/v1"
DEFAULT_MODELS = [
    "deepseek-ai/DeepSeek-V3-0324",
    "qwen/qwen3-32b",
]


class AtlasCloudGenerator(Generator):
    """
    Atlas Cloud Generator using Atlas Cloud's OpenAI-compatible chat API.
    """

    def __init__(self):
        super().__init__()
        self.name = "Atlas Cloud"
        self.description = (
            "Use Atlas Cloud's OpenAI-compatible LLM API to generate answers"
        )
        self.context_window = 10000

        api_key = get_token("ATLASCLOUD_API_KEY")
        base_url = os.getenv("ATLASCLOUD_BASE_URL", ATLASCLOUD_BASE_URL)
        models = self.get_models(api_key, base_url)
        default_model = os.getenv("ATLASCLOUD_MODEL", models[0])

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=default_model,
            description="Select an Atlas Cloud model",
            values=models,
        )

        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description=(
                    "You can set your Atlas Cloud API Key here or set it as "
                    "environment variable `ATLASCLOUD_API_KEY`"
                ),
                values=[],
            )

        if os.getenv("ATLASCLOUD_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value=ATLASCLOUD_BASE_URL,
                description=(
                    "Atlas Cloud OpenAI-compatible base URL. The `/v1` suffix is "
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
            "ATLASCLOUD_API_KEY",
            "No Atlas Cloud API Key found",
        )
        base_url = get_environment(
            config,
            "URL",
            "ATLASCLOUD_BASE_URL",
            ATLASCLOUD_BASE_URL,
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
                    if not line.startswith("data: "):
                        continue
                    if line.strip() == "data: [DONE]":
                        break

                    try:
                        json_line = json.loads(line[6:])
                        choice = json_line["choices"][0]
                    except Exception:
                        continue

                    delta = choice.get("delta", {})
                    message = delta.get("content") or ""
                    finish_reason = choice.get("finish_reason")
                    if message or finish_reason:
                        yield {
                            "message": message,
                            "finish_reason": finish_reason,
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
            response = requests.get(f"{url.rstrip('/')}/models", headers=headers)
            response.raise_for_status()
            models = sorted(
                {
                    model.get("id")
                    for model in response.json().get("data", [])
                    if model.get("id") and "embedding" not in model.get("id")
                }
            )
            return models if models else DEFAULT_MODELS
        except Exception as e:
            msg.info(f"Failed to fetch Atlas Cloud models: {str(e)}")
            return DEFAULT_MODELS
