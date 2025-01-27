import os
from dotenv import load_dotenv
import json
import aiohttp
import requests

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

load_dotenv()

base_url = "https://api.novita.ai/v3/openai"


class NovitaGenerator(Generator):
    """
    Novita Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "Novita AI"
        self.description = "Using Novita AI LLM models to generate answers to queries"
        self.context_window = 8192

        models = get_models()

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=models[0],
            description="Select a Novita Model",
            values=models,
        )

        if get_token("NOVITA_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your Novita API Key here or set it as environment variable `NOVITA_API_KEY`",
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
        model = config.get("Model", {"value": "deepseek/deepseek_v3"}).value
        novita_key = get_environment(
            config, "API Key", "NOVITA_API_KEY", "No Novita API Key found"
        )
        novita_url = base_url

        messages = self.prepare_messages(query, context, conversation, system_message)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {novita_key}",
        }
        data = {
            "messages": messages,
            "model": model,
            "stream": True,
        }

        async with aiohttp.ClientSession() as client:
            async with client.post(
                url=f"{novita_url}/chat/completions",
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


def get_models():
    try:
        response = requests.get(base_url + "/models")
        models = [model.get("id") for model in response.json().get("data")]
        if len(models) > 0:
            return models
        else:
            # msg.info("No Novita AI Model detected")
            return ["No Novita AI Model detected"]
    except Exception as e:
        # msg.fail(f"Couldn't connect to Novita AI: {e}")
        return [f"Couldn't connect to Novita AI"]
