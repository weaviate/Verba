import os
from dotenv import load_dotenv
from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token
from typing import List
import httpx
import json
from wasabi import msg

load_dotenv()

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL_LIST = ["deepseek-chat", "deepseek-reasoner"]


class DeepSeekGenerator(Generator):
    """
    DeepSeek Generator with reasoning model support.
    Supports both deepseek-chat and deepseek-reasoner (R1),
    including optional display of the model's thinking process.
    """

    def __init__(self):
        super().__init__()
        self.name = "DeepSeek"
        self.description = "Using DeepSeek models to generate answers, with support for reasoning models (R1)"
        self.context_window = 10000

        api_key = get_token("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", DEEPSEEK_BASE_URL)
        models = self.get_models(api_key, base_url)
        default_model = os.getenv("DEEPSEEK_MODEL", models[0])

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=default_model,
            description="Select a DeepSeek Model",
            values=models,
        )

        self.config["Show Reasoning"] = InputConfig(
            type="bool",
            value=False,
            description="Show the model's thinking process (for reasoning models like deepseek-reasoner)",
            values=[],
        )

        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your DeepSeek API Key here or set it as environment variable `DEEPSEEK_API_KEY`",
                values=[],
            )
        if os.getenv("DEEPSEEK_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value=DEEPSEEK_BASE_URL,
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
        model = config.get("Model", {"value": "deepseek-chat"}).value
        show_reasoning = config.get("Show Reasoning", {"value": False}).value
        api_key = get_environment(
            config, "API Key", "DEEPSEEK_API_KEY", "No DeepSeek API Key found"
        )
        api_url = get_environment(
            config, "URL", "DEEPSEEK_BASE_URL", DEEPSEEK_BASE_URL
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

        in_thinking = False

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{api_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=None,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            break
                        try:
                            json_line = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
                        choice = json_line["choices"][0]

                        # Handle reasoning_content from deepseek-reasoner
                        if "delta" in choice:
                            delta = choice["delta"]
                            reasoning = delta.get("reasoning_content")
                            content = delta.get("content")

                            if reasoning and show_reasoning:
                                if not in_thinking:
                                    in_thinking = True
                                    yield {
                                        "message": "\n<details><summary>💭 Reasoning</summary>\n\n",
                                        "finish_reason": None,
                                    }
                                yield {
                                    "message": reasoning,
                                    "finish_reason": None,
                                }

                            if content:
                                if in_thinking:
                                    in_thinking = False
                                    yield {
                                        "message": "\n</details>\n\n",
                                        "finish_reason": None,
                                    }
                                yield {
                                    "message": content,
                                    "finish_reason": choice.get("finish_reason"),
                                }

                        if choice.get("finish_reason") == "stop":
                            if in_thinking:
                                yield {
                                    "message": "\n</details>\n\n",
                                    "finish_reason": None,
                                }
                            yield {
                                "message": "",
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

    def get_models(self, token: str, url: str) -> List[str]:
        """Fetch available models from DeepSeek API."""
        try:
            if token is None:
                return DEFAULT_MODEL_LIST

            import requests

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{url}/models", headers=headers)
            response.raise_for_status()
            return [model["id"] for model in response.json()["data"]]
        except Exception as e:
            msg.info(f"Failed to fetch DeepSeek models: {str(e)}")
            return DEFAULT_MODEL_LIST
