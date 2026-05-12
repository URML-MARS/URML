"""AnthropicProvider adapter tests.

No API calls. A fake client object stands in for `anthropic.Anthropic`,
recording the request and returning a canned tool_use response. The
tests confirm:

- the adapter sends the URML schema in the `tools` payload,
- it forces `tool_choice={"type": "tool", "name": "emit_urml"}`,
- it pulls the tool input out of the response and serializes to JSON,
- it raises when the response lacks the expected tool_use block,
- the lazy SDK import works (the adapter doesn't blow up at import time
  when the real anthropic SDK is available, which it is in the dev env).
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from urml_llm_bridge.providers.anthropic import EMIT_TOOL_NAME, AnthropicProvider


class _FakeMessages:
    """Records the .create() call and returns a configured response."""

    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self.response


class _FakeAnthropicClient:
    def __init__(self, response: Any) -> None:
        self.messages = _FakeMessages(response)


def _tool_use_response(payload: dict[str, Any]) -> SimpleNamespace:
    """Build the smallest object that quacks like an Anthropic Message with a tool_use block."""
    return SimpleNamespace(
        content=[
            SimpleNamespace(type="tool_use", name=EMIT_TOOL_NAME, input=payload),
        ]
    )


def test_adapter_returns_tool_input_as_json() -> None:
    target = {
        "profile": "home",
        "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "kitchen"}}]},
    }
    client = _FakeAnthropicClient(_tool_use_response(target))
    provider = AnthropicProvider(client=client)
    out = provider.complete(
        system="SYSTEM",
        user="Bring me the red mug from the kitchen.",
        schema={"type": "object"},
    )
    assert json.loads(out) == target


def test_adapter_passes_schema_and_forces_tool_choice() -> None:
    payload = {"profile": "home", "behavior": {"type": "sequence", "steps": []}}
    client = _FakeAnthropicClient(_tool_use_response(payload))
    schema = {"type": "object", "properties": {"profile": {"type": "string"}}}
    provider = AnthropicProvider(client=client, model="claude-sonnet-4-6")
    provider.complete(system="S", user="U", schema=schema)

    call = client.messages.calls[0]
    assert call["model"] == "claude-sonnet-4-6"
    assert call["system"] == "S"
    assert call["messages"] == [{"role": "user", "content": "U"}]
    assert call["tools"][0]["name"] == EMIT_TOOL_NAME
    assert call["tools"][0]["input_schema"] is schema
    assert call["tool_choice"] == {"type": "tool", "name": EMIT_TOOL_NAME}


def test_adapter_raises_when_response_lacks_tool_use_block() -> None:
    response = SimpleNamespace(content=[SimpleNamespace(type="text", text="hello")])
    client = _FakeAnthropicClient(response)
    provider = AnthropicProvider(client=client)
    with pytest.raises(RuntimeError, match=f"{EMIT_TOOL_NAME!r}"):
        provider.complete(system="S", user="U", schema={})


def test_adapter_ignores_wrong_named_tool_use_blocks() -> None:
    """Defensive: ignore tool_use blocks whose name isn't ours."""
    response = SimpleNamespace(
        content=[
            SimpleNamespace(type="tool_use", name="some_other_tool", input={"unused": True}),
        ]
    )
    client = _FakeAnthropicClient(response)
    provider = AnthropicProvider(client=client)
    with pytest.raises(RuntimeError):
        provider.complete(system="S", user="U", schema={})


def test_max_tokens_default_and_override() -> None:
    payload = {"profile": "home", "behavior": {"type": "sequence", "steps": []}}
    client = _FakeAnthropicClient(_tool_use_response(payload))
    provider = AnthropicProvider(client=client, max_tokens=8192)
    provider.complete(system="S", user="U", schema={})
    # No explicit per-call max_tokens -> defaults to the protocol's 4096 (kwarg default).
    assert client.messages.calls[0]["max_tokens"] == 4096

    client.messages.calls.clear()
    provider.complete(system="S", user="U", schema={}, max_tokens=1024)
    assert client.messages.calls[0]["max_tokens"] == 1024
