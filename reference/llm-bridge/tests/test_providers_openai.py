"""OpenAIProvider adapter tests.

No API calls. A fake client object stands in for `openai.OpenAI`,
recording the request and returning a canned chat-completion response.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from urml_llm_bridge.providers.openai import OpenAIProvider, _resolve_timeout


class _FakeCompletions:
    def __init__(self, content: str | None) -> None:
        self._content = content
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self._content))]
        )


class _FakeChat:
    def __init__(self, content: str | None) -> None:
        self.completions = _FakeCompletions(content)


class _FakeOpenAIClient:
    def __init__(self, content: str | None) -> None:
        self.chat = _FakeChat(content)


def test_adapter_returns_message_content_string() -> None:
    program_text = json.dumps({"profile": "home", "behavior": {"type": "sequence", "steps": []}})
    client = _FakeOpenAIClient(content=program_text)
    provider = OpenAIProvider(client=client)
    out = provider.complete(system="S", user="U", schema={"type": "object"})
    assert out == program_text


def test_adapter_uses_json_object_response_format() -> None:
    client = _FakeOpenAIClient(content='{"profile": "home", "behavior": {"type": "sequence", "steps": []}}')
    provider = OpenAIProvider(client=client, model="gpt-4o")
    provider.complete(system="S", user="U", schema={})
    call = client.chat.completions.calls[0]
    assert call["model"] == "gpt-4o"
    assert call["messages"] == [
        {"role": "system", "content": "S"},
        {"role": "user", "content": "U"},
    ]
    assert call["response_format"] == {"type": "json_object"}


def test_adapter_raises_when_content_is_none() -> None:
    """OpenAI can return content=None when the model refuses; we surface that explicitly."""
    client = _FakeOpenAIClient(content=None)
    provider = OpenAIProvider(client=client)
    with pytest.raises(RuntimeError, match="content is None"):
        provider.complete(system="S", user="U", schema={})


def test_max_tokens_default_and_override() -> None:
    client = _FakeOpenAIClient(content='{"profile": "home", "behavior": {"type": "sequence", "steps": []}}')
    provider = OpenAIProvider(client=client, max_tokens=8192)
    provider.complete(system="S", user="U", schema={})
    assert client.chat.completions.calls[0]["max_tokens"] == 4096  # protocol default

    client.chat.completions.calls.clear()
    provider.complete(system="S", user="U", schema={}, max_tokens=512)
    assert client.chat.completions.calls[0]["max_tokens"] == 512


def test_base_url_forwarded_to_client(monkeypatch) -> None:
    """--base-url path: the constructor hands base_url to the OpenAI client."""
    recorded: dict[str, Any] = {}

    def _fake_openai(**kwargs: Any) -> Any:
        recorded.update(kwargs)
        return _FakeOpenAIClient(content="{}")

    monkeypatch.setattr("openai.OpenAI", _fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    OpenAIProvider(base_url="http://127.0.0.1:1234/v1")
    assert recorded["base_url"] == "http://127.0.0.1:1234/v1"
    assert recorded["api_key"] == "sk-test"

    recorded.clear()
    OpenAIProvider()
    assert "base_url" not in recorded  # SDK's own OPENAI_BASE_URL handling applies


def test_resolve_timeout(monkeypatch) -> None:
    """Per-request timeout: explicit wins, else URML_OPENAI_TIMEOUT, else None (#523)."""
    monkeypatch.delenv("URML_OPENAI_TIMEOUT", raising=False)
    assert _resolve_timeout(None) is None
    assert _resolve_timeout(42.0) == 42.0  # explicit wins
    monkeypatch.setenv("URML_OPENAI_TIMEOUT", "600")
    assert _resolve_timeout(None) == 600.0  # env read when no explicit
    assert _resolve_timeout(30.0) == 30.0  # explicit still wins over env
    monkeypatch.setenv("URML_OPENAI_TIMEOUT", "not-a-number")
    assert _resolve_timeout(None) is None  # bad value ignored, never raises
