"""WhisperCppProvider adapter tests (RFC-0670).

No network, no whisper-server. A hand-rolled fake httpx-shaped client stands
in for ``httpx.Client``, recording POSTed multipart requests and returning a
canned whisper-server JSON response. The tests confirm:

- the adapter posts to ``/inference`` with the audio as a multipart file,
- it requests ``response_format: json`` and forwards temperature + language,
- it strips the transcript (whisper-server pads with whitespace/newlines),
- it raises when the response shape is malformed,
- a dead server yields one actionable ConnectionError line.
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_llm_bridge.speech.whisper_cpp import (
    DEFAULT_BASE_URL,
    INFERENCE_PATH,
    WhisperCppProvider,
)


class _FakeResponse:
    def __init__(self, payload: Any, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> Any:
        return self._payload


class _FakeHTTPClient:
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        files: dict[str, Any],
        timeout: float,
    ) -> _FakeResponse:
        self.calls.append({"url": url, "data": data, "files": files, "timeout": timeout})
        return self.response


def test_adapter_posts_multipart_to_inference() -> None:
    client = _FakeHTTPClient(_FakeResponse({"text": " Bring me the red mug.\n"}))
    provider = WhisperCppProvider(client=client)

    out = provider.transcribe(audio=b"RIFFwav-bytes", filename="request.wav")

    assert out == "Bring me the red mug."  # stripped
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["url"] == DEFAULT_BASE_URL + INFERENCE_PATH
    assert call["data"]["response_format"] == "json"
    assert call["data"]["temperature"] == "0.0"
    assert call["files"]["file"] == ("request.wav", b"RIFFwav-bytes", "application/octet-stream")


def test_adapter_forwards_language_hint() -> None:
    client = _FakeHTTPClient(_FakeResponse({"text": "תביא לי את הספל האדום"}))
    provider = WhisperCppProvider(client=client)
    provider.transcribe(audio=b"x", language="he")
    assert client.calls[0]["data"]["language"] == "he"


def test_adapter_omits_language_by_default() -> None:
    client = _FakeHTTPClient(_FakeResponse({"text": "ok"}))
    provider = WhisperCppProvider(client=client)
    provider.transcribe(audio=b"x")
    assert "language" not in client.calls[0]["data"]


def test_adapter_honors_custom_base_url() -> None:
    client = _FakeHTTPClient(_FakeResponse({"text": "ok"}))
    provider = WhisperCppProvider(client=client, base_url="http://gpu-box:9000/")
    provider.transcribe(audio=b"x")
    assert client.calls[0]["url"] == "http://gpu-box:9000" + INFERENCE_PATH


def test_adapter_raises_on_missing_text() -> None:
    client = _FakeHTTPClient(_FakeResponse({"error": "boom"}))
    provider = WhisperCppProvider(client=client)
    with pytest.raises(RuntimeError, match="text"):
        provider.transcribe(audio=b"x")


def test_adapter_raises_on_non_object_body() -> None:
    client = _FakeHTTPClient(_FakeResponse(["not", "a", "dict"]))
    provider = WhisperCppProvider(client=client)
    with pytest.raises(RuntimeError, match="non-object"):
        provider.transcribe(audio=b"x")


def test_adapter_raises_on_http_error() -> None:
    client = _FakeHTTPClient(_FakeResponse({}, status_code=503))
    provider = WhisperCppProvider(client=client)
    with pytest.raises(RuntimeError, match="503"):
        provider.transcribe(audio=b"x")


class _DeadHTTPClient:
    """Fake client standing in for a server that is not running."""

    def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        files: dict[str, Any],
        timeout: float,
    ) -> _FakeResponse:
        raise ConnectionError("connection refused")


def test_connect_error_is_friendly() -> None:
    """A dead server yields one actionable line naming the URL and the fix."""
    provider = WhisperCppProvider(client=_DeadHTTPClient(), base_url="http://gpu-box:9000")
    with pytest.raises(ConnectionError) as excinfo:
        provider.transcribe(audio=b"x")
    message = str(excinfo.value)
    assert "http://gpu-box:9000" in message
    assert "whisper-server" in message
