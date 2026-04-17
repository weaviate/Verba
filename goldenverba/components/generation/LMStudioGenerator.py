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


class LMStudioGenerator(Generator):
    """
    LM Studio Generator - Compatible with LM Studio's OpenAI-compatible API.
    """

    def __init__(self):
        super().__init__()
        self.name = "LM Studio"
        self.description = "Using LM Studio's locally hosted models via OpenAI-compatible API"
        self.context_window = 10000

        # Default LM Studio URL
        base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        api_key = get_token("LMSTUDIO_API_KEY") or "lm-studio"  # LM Studio often doesn't need real API key
        
        models = self.get_models(api_key, base_url)
        default_model = os.getenv("LMSTUDIO_MODEL", models[0] if models else "local-model")

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=default_model,
            description="Select a LM Studio Model",
            values=models,
        )

        # Always show URL config for LM Studio since it's local
        self.config["URL"] = InputConfig(
            type="text",
            value=base_url,
            description="LM Studio API Base URL (default: http://localhost:1234/v1)",
            values=[],
        )

        # API Key is optional for LM Studio
        if get_token("LMSTUDIO_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="lm-studio",
                description="LM Studio API Key (often not required, default: 'lm-studio')",
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
        model = config.get("Model", {"value": "local-model"}).value
        lmstudio_key = get_environment(
            config, "API Key", "LMSTUDIO_API_KEY", "lm-studio"
        )
        lmstudio_url = get_environment(
            config, "URL", "LMSTUDIO_BASE_URL", "http://localhost:1234/v1"
        )

        messages = self.prepare_messages(query, context, conversation, system_message)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {lmstudio_key}",
        }
        data = {
            "messages": messages,
            "model": model,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{lmstudio_url}/chat/completions",
                    json=data,
                    headers=headers,
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise Exception(f"LM Studio API error {response.status_code}: {error_text}")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line.strip() == "data: [DONE]":
                                yield {
                                    "message": "",
                                    "finish_reason": "stop",
                                }
                                break
                            try:
                                json_line = json.loads(line[6:])
                                choice = json_line.get("choices", [{}])[0]
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
                            except json.JSONDecodeError:
                                continue  # Skip malformed lines
        except Exception as e:
            msg.fail(f"LM Studio generation failed: {str(e)}")
            yield {
                "message": f"Error: {str(e)}",
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
        """Fetch available models from LM Studio API."""
        default_models = ["local-model"]
        try:
            import requests

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{url}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                if "data" in models_data:
                    available_models = [model["id"] for model in models_data["data"]]
                    return available_models if available_models else default_models
            
            msg.info("Could not fetch models from LM Studio, using default")
            return default_models
            
        except Exception as e:
            msg.info(f"Failed to fetch LM Studio models: {str(e)}")
            return default_models
