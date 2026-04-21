"""Unit tests for LiteLLMGenerator."""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from unittest import mock

import pytest

from goldenverba.components.generation.LiteLLMGenerator import LiteLLMGenerator


def _install_litellm_stub(acompletion_return):
    """Register a fake ``litellm`` module so ``import litellm`` resolves."""
    fake = types.ModuleType("litellm")

    async def _acompletion(**kwargs):
        # Record the call for assertions on the pytest side.
        _acompletion.call_args = kwargs  # type: ignore[attr-defined]
        return acompletion_return

    fake.acompletion = _acompletion
    sys.modules["litellm"] = fake
    return _acompletion


def _make_chunk(
    content: str | None, finish_reason: str | None = None
) -> SimpleNamespace:
    delta = SimpleNamespace(content=content)
    choice = SimpleNamespace(delta=delta, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice])


class _AsyncIter:
    def __init__(self, items):
        self._items = items

    def __aiter__(self):
        return self._iter()

    async def _iter(self):
        for item in self._items:
            yield item


def test_litellm_generator_metadata():
    gen = LiteLLMGenerator()
    assert gen.name == "LiteLLM"
    assert "LiteLLM" in gen.description
    assert "litellm" in gen.requires_library


def test_litellm_generator_config_surface():
    gen = LiteLLMGenerator()
    assert "Model" in gen.config
    # System Message is set by the parent Generator __init__
    assert "System Message" in gen.config
    # API Key / URL are conditionally added when the corresponding env var is unset.


def test_prepare_messages_builds_system_user_pair():
    gen = LiteLLMGenerator()
    messages = gen.prepare_messages(
        query="What is Verba?",
        context="Verba is a Weaviate-based RAG stack.",
        conversation=[],
        system_message="You are Verba.",
    )
    assert messages[0] == {"role": "system", "content": "You are Verba."}
    assert messages[-1]["role"] == "user"
    assert "What is Verba?" in messages[-1]["content"]
    assert "Verba is a Weaviate-based RAG stack." in messages[-1]["content"]


@pytest.mark.asyncio
async def test_generate_stream_yields_chunks_and_finish():
    """generate_stream must yield {'message', 'finish_reason'} dicts and forward
    the configured model + optional api_key/api_base to litellm.acompletion."""
    chunks = [
        _make_chunk("Hello "),
        _make_chunk("world", finish_reason=None),
        _make_chunk(None, finish_reason="stop"),
    ]
    acompletion = _install_litellm_stub(_AsyncIter(chunks))

    gen = LiteLLMGenerator()
    config = {
        "Model": SimpleNamespace(value="anthropic/claude-3-5-sonnet-20241022"),
        "System Message": SimpleNamespace(value="You are Verba."),
        "API Key": SimpleNamespace(value="sk-test"),
        "URL": SimpleNamespace(value="https://proxy.example.com/v1"),
    }

    outputs = []
    async for item in gen.generate_stream(
        config=config, query="hi", context="ctx", conversation=[]
    ):
        outputs.append(item)

    assert outputs[0] == {"message": "Hello ", "finish_reason": None}
    assert outputs[1] == {"message": "world", "finish_reason": None}
    assert outputs[2] == {"message": "", "finish_reason": "stop"}

    kwargs = acompletion.call_args  # type: ignore[attr-defined]
    assert kwargs["model"] == "anthropic/claude-3-5-sonnet-20241022"
    assert kwargs["stream"] is True
    assert kwargs["api_key"] == "sk-test"
    assert kwargs["api_base"] == "https://proxy.example.com/v1"


@pytest.mark.asyncio
async def test_generate_stream_omits_api_key_when_blank():
    """When neither config API Key nor LITELLM_API_KEY is set, the kwarg must be
    omitted so LiteLLM can fall back to provider-specific env vars."""
    acompletion = _install_litellm_stub(
        _AsyncIter([_make_chunk("ok", finish_reason="stop")])
    )

    gen = LiteLLMGenerator()
    config = {
        "Model": SimpleNamespace(value="openai/gpt-4o-mini"),
        "System Message": SimpleNamespace(value="You are Verba."),
        "API Key": SimpleNamespace(value=""),
        "URL": SimpleNamespace(value=""),
    }

    async for _ in gen.generate_stream(
        config=config, query="hi", context="ctx", conversation=[]
    ):
        pass

    kwargs = acompletion.call_args  # type: ignore[attr-defined]
    assert "api_key" not in kwargs
    assert "api_base" not in kwargs


@pytest.mark.asyncio
async def test_generate_stream_raises_import_error_without_litellm():
    """If ``litellm`` isn't installed, generate_stream should raise ImportError
    with an install hint matching our ``extras_require`` entry."""
    sys.modules.pop("litellm", None)
    # Also ensure it can't be found by the import machinery during the test.
    with mock.patch.dict(sys.modules, {"litellm": None}):
        gen = LiteLLMGenerator()
        config = {
            "Model": SimpleNamespace(value="openai/gpt-4o-mini"),
            "System Message": SimpleNamespace(value="You are Verba."),
        }
        with pytest.raises(ImportError, match="goldenverba\\[litellm\\]"):
            async for _ in gen.generate_stream(
                config=config, query="hi", context="ctx", conversation=[]
            ):
                pass
