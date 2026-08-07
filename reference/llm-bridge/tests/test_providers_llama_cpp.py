"""LlamaCppProvider adapter tests.

No network, no llama-server. A hand-rolled fake httpx-shaped client stands
in for ``httpx.Client``, recording POSTed bodies and returning a canned
OpenAI-compat chat response. The tests confirm:

- the adapter posts to ``/v1/chat/completions``,
- it derives a GBNF grammar from the schema and includes it in the body,
- it forwards system + user as chat messages,
- it pulls ``choices[0].message.content`` out of the response,
- it raises when the response shape is malformed.
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_llm_bridge.providers.llama_cpp import (
    CHAT_COMPLETIONS_PATH,
    DEFAULT_BASE_URL,
    LlamaCppProvider,
)


class _FakeResponse:
    """Quacks like an httpx.Response."""

    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeHTTPClient:
    """Records each .post() call and returns a configured response."""

    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, *, json: dict[str, Any], timeout: float) -> _FakeResponse:
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        return self.response


def _chat_response(content: str) -> _FakeResponse:
    return _FakeResponse({"choices": [{"message": {"role": "assistant", "content": content}}]})


def test_adapter_posts_to_chat_completions_with_grammar() -> None:
    client = _FakeHTTPClient(_chat_response('{"profile": "home", "behavior": {"type": "sequence", "steps": []}}'))
    provider = LlamaCppProvider(client=client)
    schema = {"type": "object", "additionalProperties": False, "properties": {"x": {"type": "string"}}}

    out = provider.complete(system="SYS", user="USR", schema=schema)

    assert out == '{"profile": "home", "behavior": {"type": "sequence", "steps": []}}'
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["url"] == DEFAULT_BASE_URL + CHAT_COMPLETIONS_PATH
    body = call["json"]
    assert body["messages"] == [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "USR"},
    ]
    # Grammar is present and non-empty (the actual GBNF text).
    assert isinstance(body["grammar"], str)
    assert "::=" in body["grammar"]


def test_adapter_uses_zero_temperature_by_default() -> None:
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = LlamaCppProvider(client=client)
    provider.complete(system="S", user="U", schema={"type": "object"})
    assert client.calls[0]["json"]["temperature"] == 0.0


def test_adapter_honors_custom_base_url_and_temperature() -> None:
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = LlamaCppProvider(client=client, base_url="http://gpu-box:9090/", temperature=0.7)
    provider.complete(system="S", user="U", schema={"type": "object"})
    call = client.calls[0]
    # Trailing slash stripped, path joined cleanly.
    assert call["url"] == "http://gpu-box:9090" + CHAT_COMPLETIONS_PATH
    assert call["json"]["temperature"] == 0.7


def test_adapter_forwards_max_tokens() -> None:
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = LlamaCppProvider(client=client)
    provider.complete(system="S", user="U", schema={"type": "object"}, max_tokens=512)
    assert client.calls[0]["json"]["max_tokens"] == 512


def test_adapter_raises_on_missing_choices() -> None:
    client = _FakeHTTPClient(_FakeResponse({"error": "boom"}))
    provider = LlamaCppProvider(client=client)
    with pytest.raises(RuntimeError, match="choices"):
        provider.complete(system="S", user="U", schema={"type": "object"})


def test_adapter_raises_on_non_string_content() -> None:
    client = _FakeHTTPClient(_FakeResponse({"choices": [{"message": {"content": 42}}]}))
    provider = LlamaCppProvider(client=client)
    with pytest.raises(RuntimeError, match="content"):
        provider.complete(system="S", user="U", schema={"type": "object"})


def test_adapter_raises_on_http_error() -> None:
    client = _FakeHTTPClient(_FakeResponse({}, status_code=500))
    provider = LlamaCppProvider(client=client)
    with pytest.raises(RuntimeError, match="500"):
        provider.complete(system="S", user="U", schema={"type": "object"})


def test_grammar_is_cached_across_calls_with_same_schema() -> None:
    """Two complete() calls with the same schema produce identical grammar text."""
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = LlamaCppProvider(client=client)
    schema = {"type": "object", "additionalProperties": False, "properties": {"x": {"type": "string"}}}

    provider.complete(system="S", user="U", schema=schema)
    provider.complete(system="S2", user="U2", schema=schema)

    g1 = client.calls[0]["json"]["grammar"]
    g2 = client.calls[1]["json"]["grammar"]
    assert g1 == g2


class _DeadHTTPClient:
    """Fake client standing in for a server that is not running."""

    def post(self, url: str, *, json: dict[str, Any], timeout: float) -> _FakeResponse:
        raise ConnectionError("connection refused")


def test_connect_error_is_friendly() -> None:
    """A dead server yields one actionable line naming the URL and the fix."""
    provider = LlamaCppProvider(client=_DeadHTTPClient(), base_url="http://gpu-box:99")
    with pytest.raises(ConnectionError) as excinfo:
        provider.complete(system="S", user="U", schema={"type": "object"})
    message = str(excinfo.value)
    assert "http://gpu-box:99" in message
    assert "llama-server" in message
