import os
from dotenv import load_dotenv
from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment
import aiohttp
import json

load_dotenv()


class AnthropicGenerator(Generator):
    """
    Anthropic Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "Anthropic"
        self.description = "Using Anthropic LLM models to generate answers to queries"
        self.context_window = 10000
        self.url = "https://api.anthropic.com/v1/messages"

        models = ["claude-3-5-sonnet-20240620"]

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=models[0],
            description="Select an Anthropic Model",
            values=models,
        )

        if os.getenv("ANTHROPIC_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your Anthropic API Key here or set it as environment variable `ANTHROPIC_API_KEY`",
                values=[],
            )

    async def generate_stream(
        self,
        config: dict,
        query: str,
        context: str,
        conversation: list[dict] = [],
    ):
        model = config.get("Model").value
        system_message = config.get("System Message").value
        antr_key = get_environment(
            config, "API Key", "ANTHROPIC_API_KEY", "No Anthropic API Key found"
        )

        messages = self.prepare_messages(query, context, conversation)

        headers = {
            "Content-Type": "application/json",
            "x-api-key": antr_key,
            "anthropic-version": "2023-06-01",
        }

        data = {
            "messages": messages,
            "model": model,
            "stream": True,
            "system": system_message,
            "max_tokens": 4096,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                json=data,
                headers=headers,
            ) as response:
                if response.status != 200:
                    error_json = await response.json()
                    error_message = error_json.get("error", {}).get(
                        "message", "Unknown error occurred"
                    )
                    yield {
                        "message": f"Error: {error_message}",
                        "finish_reason": "stop",
                    }
                    return

                async for line in response.content:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        json_line = json.loads(line[6:])
                        if json_line["type"] == "content_block_delta":
                            delta = json_line.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text = delta.get("text", "")
                                yield {
                                    "message": text,
                                    "finish_reason": None,
                                }
                        elif json_line.get("type") == "message_stop":
                            yield {
                                "message": "",
                                "finish_reason": json_line.get("stop_reason", "stop"),
                            }

    def prepare_messages(
        self, query: str, context: str, conversation: list[dict]
    ) -> list[dict]:
        messages = []

        for message in conversation:
            messages.append(
                {
                    "role": "assistant" if message.type == "system" else message.type,
                    "content": message.content,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": f"Answer this query: '{query}' with this provided context: {context}",
            }
        )

        return messages
