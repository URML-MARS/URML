"""OllamaProvider adapter tests.

No network, no Ollama. A hand-rolled fake httpx-shaped client stands in for
``httpx.Client``, recording POSTed bodies and returning a canned Ollama
chat response. The tests confirm:

- the adapter posts to ``/api/chat``,
- it forwards the URML schema as ``format`` (so Ollama 0.5+ uses it as a
  JSON-Schema constraint, older builds treat it as a JSON hint),
- it forwards system + user as chat messages,
- it pulls ``message.content`` out of the response,
- it sets ``stream: false`` and forwards ``num_predict`` + ``temperature``,
- it raises when the response shape is malformed.
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_llm_bridge.providers.ollama import CHAT_PATH, DEFAULT_BASE_URL, OllamaProvider


class _FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeHTTPClient:
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, *, json: dict[str, Any], timeout: float) -> _FakeResponse:
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        return self.response


def _chat_response(content: str) -> _FakeResponse:
    return _FakeResponse({"model": "test", "message": {"role": "assistant", "content": content}})


def test_adapter_posts_to_api_chat_with_schema_as_format() -> None:
    client = _FakeHTTPClient(_chat_response('{"profile": "home", "behavior": {"type": "sequence", "steps": []}}'))
    provider = OllamaProvider(model="llama3.2:1b", client=client)
    schema = {"type": "object", "additionalProperties": False, "properties": {"x": {"type": "string"}}}

    out = provider.complete(system="SYS", user="USR", schema=schema)

    assert out == '{"profile": "home", "behavior": {"type": "sequence", "steps": []}}'
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["url"] == DEFAULT_BASE_URL + CHAT_PATH
    body = call["json"]
    assert body["model"] == "llama3.2:1b"
    assert body["messages"] == [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "USR"},
    ]
    assert body["format"] is schema
    assert body["stream"] is False


def test_adapter_forwards_temperature_and_num_predict() -> None:
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = OllamaProvider(model="m", client=client, temperature=0.5)
    provider.complete(system="S", user="U", schema={"type": "object"}, max_tokens=256)
    opts = client.calls[0]["json"]["options"]
    assert opts["temperature"] == 0.5
    assert opts["num_predict"] == 256


def test_adapter_uses_zero_temperature_by_default() -> None:
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = OllamaProvider(model="m", client=client)
    provider.complete(system="S", user="U", schema={"type": "object"})
    assert client.calls[0]["json"]["options"]["temperature"] == 0.0


def test_adapter_honors_custom_base_url() -> None:
    client = _FakeHTTPClient(_chat_response("{}"))
    provider = OllamaProvider(model="m", client=client, base_url="http://gpu-box:99/")
    provider.complete(system="S", user="U", schema={"type": "object"})
    assert client.calls[0]["url"] == "http://gpu-box:99" + CHAT_PATH


def test_adapter_raises_on_missing_message() -> None:
    client = _FakeHTTPClient(_FakeResponse({"error": "boom"}))
    provider = OllamaProvider(model="m", client=client)
    with pytest.raises(RuntimeError, match="message"):
        provider.complete(system="S", user="U", schema={"type": "object"})


def test_adapter_raises_on_non_string_content() -> None:
    client = _FakeHTTPClient(_FakeResponse({"message": {"content": 42}}))
    provider = OllamaProvider(model="m", client=client)
    with pytest.raises(RuntimeError, match="content"):
        provider.complete(system="S", user="U", schema={"type": "object"})


def test_adapter_raises_on_http_error() -> None:
    client = _FakeHTTPClient(_FakeResponse({}, status_code=503))
    provider = OllamaProvider(model="m", client=client)
    with pytest.raises(RuntimeError, match="503"):
        provider.complete(system="S", user="U", schema={"type": "object"})


class _DeadHTTPClient:
    """Fake client standing in for a server that is not running."""

    def post(self, url: str, *, json: dict[str, Any], timeout: float) -> _FakeResponse:
        raise ConnectionError("connection refused")


def test_connect_error_is_friendly() -> None:
    """A dead server yields one actionable line naming the URL and the fix."""
    provider = OllamaProvider(model="m", client=_DeadHTTPClient(), base_url="http://gpu-box:99")
    with pytest.raises(ConnectionError) as excinfo:
        provider.complete(system="S", user="U", schema={"type": "object"})
    message = str(excinfo.value)
    assert "http://gpu-box:99" in message
    assert "ollama serve" in message
