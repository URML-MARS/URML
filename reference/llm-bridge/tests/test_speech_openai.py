"""OpenAISpeechProvider adapter tests (RFC-0670).

No API calls. A fake client object stands in for `openai.OpenAI`, recording
the transcription request and returning a canned response.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from urml_llm_bridge.speech.echo import EchoSpeechProvider
from urml_llm_bridge.speech.openai import OpenAISpeechProvider


class _FakeTranscriptions:
    def __init__(self, text: Any) -> None:
        self._text = text
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(text=self._text)


class _FakeAudio:
    def __init__(self, text: Any) -> None:
        self.transcriptions = _FakeTranscriptions(text)


class _FakeOpenAIClient:
    def __init__(self, text: Any) -> None:
        self.audio = _FakeAudio(text)


def test_adapter_returns_stripped_text() -> None:
    client = _FakeOpenAIClient(text=" Bring me the red mug. \n")
    provider = OpenAISpeechProvider(client=client)
    out = provider.transcribe(audio=b"RIFFwav-bytes", filename="request.wav")
    assert out == "Bring me the red mug."
    call = client.audio.transcriptions.calls[0]
    assert call["model"] == "whisper-1"
    filename, fileobj = call["file"]
    assert filename == "request.wav"
    assert fileobj.read() == b"RIFFwav-bytes"


def test_adapter_forwards_model_and_language() -> None:
    client = _FakeOpenAIClient(text="ok")
    provider = OpenAISpeechProvider(client=client, model="gpt-4o-transcribe")
    provider.transcribe(audio=b"x", language="ja")
    call = client.audio.transcriptions.calls[0]
    assert call["model"] == "gpt-4o-transcribe"
    assert call["language"] == "ja"


def test_adapter_omits_language_by_default() -> None:
    client = _FakeOpenAIClient(text="ok")
    provider = OpenAISpeechProvider(client=client)
    provider.transcribe(audio=b"x")
    assert "language" not in client.audio.transcriptions.calls[0]


def test_adapter_raises_on_non_string_text() -> None:
    client = _FakeOpenAIClient(text=None)
    provider = OpenAISpeechProvider(client=client)
    with pytest.raises(RuntimeError, match="text"):
        provider.transcribe(audio=b"x")


def test_base_url_forwarded_to_client(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: dict[str, Any] = {}

    def _fake_openai(**kwargs: Any) -> Any:
        recorded.update(kwargs)
        return _FakeOpenAIClient(text="ok")

    monkeypatch.setattr("openai.OpenAI", _fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    OpenAISpeechProvider(base_url="http://127.0.0.1:1234/v1")
    assert recorded["base_url"] == "http://127.0.0.1:1234/v1"
    assert recorded["api_key"] == "sk-test"


def test_echo_speech_provider_returns_canned_text() -> None:
    provider = EchoSpeechProvider(text="Bring me the red mug.")
    assert provider.transcribe(audio=b"ignored") == "Bring me the red mug."
