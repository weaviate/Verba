import json
import os
import aiohttp
from typing import Any, AsyncGenerator, List, Dict
from wasabi import msg
import requests

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment

GROQ_BASE_URL = "https://api.groq.com/openai/v1/"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MODEL_LIST = [
    "gemma-7b-it",
    "gemma2-9b-it",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
]  # offline Groq models list to show to user if they don't provide a GROQ_API_KEY as environment variable
# this list may need to be updated in the future


class GroqGenerator(Generator):
    """
    Groq LPU Inference Engine Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "Groq"
        self.description = "Generator using Groq's LPU inference engine"
        self.url = GROQ_BASE_URL
        self.context_window = 10000

        env_api_key = os.getenv("GROQ_API_KEY")

        # Fetch available models
        models = get_models(self.url, env_api_key)

        # Configure the model selection dropdown
        self.config["Model"] = InputConfig(
            type="dropdown",
            value=models[0] if models else "",
            description="Select a Groq model",
            values=models,
        )

        if env_api_key is None:
            # if api key not set in environment variable, then provide input for Groq API key on the interface
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your Groq API Key here or set it as environment variable `GROQ_API_KEY`",
                values=[],
            )

    async def generate_stream(
        self,
        config: Dict,
        query: str,
        context: str,
        conversation: List[Dict[str, Any]] = [],
    ) -> AsyncGenerator[Dict, None]:
        model = config.get("Model").value
        api_key = get_environment(
            config, "API Key", "GROQ_API_KEY", "No Groq API Key found"
        )

        if api_key is None:
            yield self._error_response("Missing Groq API Key")
            return

        system_message = config.get("System Message").value
        messages = self._prepare_messages(query, context, conversation, system_message)

        data = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": DEFAULT_TEMPERATURE,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url + "/chat/completions", json=data, headers=headers
                ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line.strip():
                                yield GroqGenerator._process_response(line)
                    else:
                        error_message = await response.text()
                        yield GroqGenerator._error_response(
                            f"HTTP Error {response.status}: {error_message}"
                        )

        except Exception as e:
            yield self._error_response(str(e))

    def _prepare_messages(
        self,
        query: str,
        context: str,
        conversation: List[Dict[str, Any]],
        system_message: str,
    ) -> List[Dict[str, str]]:
        """
        Prepare the message list for the Groq API request.
        """
        messages = [
            {"role": "system", "content": system_message},
            *[
                {"role": message.type, "content": message.content}
                for message in conversation
            ],
            {
                "role": "user",
                "content": f"With this provided context: {context} Please answer this query: {query}",
            },
        ]
        return messages

    @staticmethod
    def _process_response(line: bytes) -> Dict[str, str]:
        """
        Process a single line of response from the Groq API.
        """
        decoded_line = line.decode("utf-8").strip()

        if decoded_line == "data: [DONE]":
            return {"message": "", "finish_reason": "stop"}

        if decoded_line.startswith("data:"):
            decoded_line = decoded_line[5:].strip()  # remove prefix 'data:'

        try:
            json_data = json.loads(decoded_line)
            generation_data = json_data.get("choices")[
                0
            ]  # take first generation choice
            return {
                "message": generation_data.get("delta", {}).get("content", ""),
                "finish_reason": (
                    "stop" if json_data.get("finish_reason", "") == "stop" else ""
                ),
            }
        except json.JSONDecodeError as e:
            msg.fail(
                f"Error \"{e}\" while processing Groq JSON response : \"\"\"{line.decode('utf-8')}\"\"\""
            )
            raise e

    @staticmethod
    def _error_response(message: str) -> Dict[str, str]:
        """Return an error response."""
        return {"message": message, "finish_reason": "stop"}


def get_models(url: str, api_key: str) -> List[str]:
    """
    Fetch online and return available Groq models if api_key is not empty and valid.
    Else, return offline default model list.
    """
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url + "models", headers=headers)
        models = [
            model.get("id")
            for model in response.json().get("data")
            if model.get("active") is True
        ]
        models.sort()
        models = filter_models(models)
        return models

    except Exception as e:
        msg.info(f"Couldn't connect to Groq ({url})")
        return DEFAULT_MODEL_LIST


def filter_models(models: List[str]) -> List[str]:
    """
    Filters out models that are not LLMs
    (As Groq API doesn't provide a way to identify them, this function will probably evolve with custom filtering rules)
    """

    def is_valid_model(model):
        return ("whisper" not in model) and ("llava" not in model)

    filtered_models = list(filter(is_valid_model, models))
    return filtered_models
