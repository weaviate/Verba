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

ORCAROUTER_BASE_URL = "https://api.orcarouter.ai/v1"
DEFAULT_MODELS = [
    "orcarouter/auto",
    "openai/gpt-5.5",
    "google/gemini-3-flash-preview",
    "anthropic/claude-opus-4.7",
    "grok/grok-4.3",
    "deepseek/deepseek-v4-pro",
    "minimax/minimax-m2.7",
    "qwen/qwen3.6-flash",
]


class OrcaRouterGenerator(Generator):
    """
    OrcaRouter Generator using OrcaRouter's OpenAI-compatible chat API.

    OrcaRouter is a meta-router that exposes 150+ upstream models from OpenAI,
    Anthropic, Google, DeepSeek, xAI, Qwen, MiniMax and others through a single
    OpenAI-compatible endpoint. The virtual `orcarouter/auto` model picks an
    upstream per-request based on a configurable routing policy.

    Reference: https://docs.orcarouter.ai
    """

    def __init__(self):
        super().__init__()
        self.name = "OrcaRouter"
        self.description = (
            "Use OrcaRouter's OpenAI-compatible meta-router to call 150+ upstream "
            "LLMs (OpenAI / Anthropic / Google / DeepSeek / xAI / Qwen / ...) "
            "through a single API key. See https://www.orcarouter.ai/models."
        )
        self.context_window = 10000

        api_key = get_token("ORCAROUTER_API_KEY")
        base_url = os.getenv("ORCAROUTER_API_BASE_URL", ORCAROUTER_BASE_URL)
        models = self.get_models(api_key, base_url)
        default_model = os.getenv("ORCAROUTER_MODEL", models[0])

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=default_model,
            description=(
                "Select an OrcaRouter model. `orcarouter/auto` picks an upstream "
                "automatically per request."
            ),
            values=models,
        )

        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description=(
                    "You can set your OrcaRouter API Key here or set it as "
                    "environment variable `ORCAROUTER_API_KEY`. Get one at "
                    "https://www.orcarouter.ai."
                ),
                values=[],
            )

        if os.getenv("ORCAROUTER_API_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value=ORCAROUTER_BASE_URL,
                description=(
                    "OrcaRouter OpenAI-compatible base URL. The `/v1` suffix is "
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
            "ORCAROUTER_API_KEY",
            "No OrcaRouter API Key found",
        )
        base_url = get_environment(
            config,
            "URL",
            "ORCAROUTER_API_BASE_URL",
            ORCAROUTER_BASE_URL,
        ).rstrip("/")

        messages = self.prepare_messages(query, context, conversation, system_message)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://verba.weaviate.io/",
            "X-Title": "Verba",
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
            response = requests.get(
                f"{url.rstrip('/')}/models", headers=headers, timeout=10
            )
            response.raise_for_status()
            models = sorted(
                {
                    model.get("id")
                    for model in response.json().get("data", [])
                    if model.get("id") and "embedding" not in model.get("id").lower()
                }
            )
            return models if models else DEFAULT_MODELS
        except Exception as e:
            msg.info(f"Failed to fetch OrcaRouter models: {str(e)}")
            return DEFAULT_MODELS
