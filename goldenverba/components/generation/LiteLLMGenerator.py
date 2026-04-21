import os

from dotenv import load_dotenv
from wasabi import msg

from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig

load_dotenv()


class LiteLLMGenerator(Generator):
    """LiteLLM Generator.

    Routes chat completions through ``litellm.acompletion()`` to 100+ providers
    (OpenAI, Anthropic, Bedrock, Vertex, Gemini, Ollama, OpenRouter, Groq, DeepSeek,
    etc.) using provider-native API keys. The user picks any LiteLLM-supported
    model by its prefixed name (``anthropic/claude-3-5-sonnet-20241022``,
    ``gemini/gemini-1.5-pro``, ``bedrock/anthropic.claude-3-sonnet-20240229-v1:0``,
    ``ollama/llama3``, ...).

    See https://docs.litellm.ai/docs/providers for the full list.
    """

    def __init__(self):
        super().__init__()
        self.name = "LiteLLM"
        self.description = (
            "Using LiteLLM to route to 100+ LLM providers via a unified interface"
        )
        self.context_window = 10000
        # LiteLLM is an optional dep; surface this in the UI via the standard
        # requires_library availability check.
        self.requires_library = ["litellm"]

        default_model = os.getenv("LITELLM_MODEL", "openai/gpt-4o-mini")
        self.config["Model"] = InputConfig(
            type="text",
            value=default_model,
            description=(
                "LiteLLM-style model name, e.g. 'anthropic/claude-3-5-sonnet-20241022', "
                "'gemini/gemini-1.5-pro', 'bedrock/anthropic.claude-3-sonnet-20240229-v1:0', "
                "'ollama/llama3'. See https://docs.litellm.ai/docs/providers."
            ),
            values=[],
        )
        if os.getenv("LITELLM_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description=(
                    "Optional provider API key. If left blank, LiteLLM falls back to "
                    "the provider-specific env var (OPENAI_API_KEY, ANTHROPIC_API_KEY, "
                    "GEMINI_API_KEY, AWS_*, GROQ_API_KEY, ...) based on the selected model."
                ),
                values=[],
            )
        if os.getenv("LITELLM_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value="",
                description=(
                    "Optional custom base URL, forwarded to LiteLLM as 'api_base'. "
                    "Leave blank to use the provider's default endpoint."
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
        try:
            import litellm  # lazy import; optional dep
        except ImportError as err:
            msg.warn(
                "LiteLLM is not installed. Install with: pip install 'goldenverba[litellm]'"
            )
            raise ImportError(
                "LiteLLM is not installed. Install with: pip install 'goldenverba[litellm]'"
            ) from err

        system_message = config.get("System Message").value
        model = config.get("Model").value

        # Optional credentials — read directly so a missing value doesn't raise.
        api_key = self._resolve_optional(config, "API Key", "LITELLM_API_KEY")
        api_base = self._resolve_optional(config, "URL", "LITELLM_BASE_URL")

        messages = self.prepare_messages(query, context, conversation, system_message)

        kwargs: dict = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if api_key:
            kwargs["api_key"] = api_key
        if api_base:
            kwargs["api_base"] = api_base

        response = await litellm.acompletion(**kwargs)
        async for chunk in response:
            if not getattr(chunk, "choices", None):
                continue
            choice = chunk.choices[0]
            delta = getattr(choice, "delta", None)
            content = getattr(delta, "content", None) if delta else None
            finish_reason = getattr(choice, "finish_reason", None)

            if content:
                yield {"message": content, "finish_reason": finish_reason}
            elif finish_reason:
                yield {"message": "", "finish_reason": finish_reason}

    @staticmethod
    def _resolve_optional(config: dict, config_key: str, env_key: str) -> str | None:
        """Read an optional value from the user config, falling back to an env var.

        Returns ``None`` when neither is set so the caller can skip forwarding the
        kwarg and let LiteLLM pick up provider-specific env vars on its own.
        """
        if config_key in config:
            value = config[config_key].value
            if value:
                return value
        env_value = os.getenv(env_key)
        return env_value or None

    def prepare_messages(
        self,
        query: str,
        context: str,
        conversation: list[dict],
        system_message: str,
    ) -> list[dict]:
        messages = [{"role": "system", "content": system_message}]

        for message in conversation:
            messages.append({"role": message.type, "content": message.content})

        messages.append(
            {
                "role": "user",
                "content": f"Answer this query: '{query}' with this provided context: {context}",
            }
        )
        return messages
