"""whisper.cpp on-device speech provider (RFC-0670).

Talks to a running ``whisper-server`` (from the whisper.cpp project) over
its ``/inference`` endpoint: a multipart POST carrying the audio file, with
``response_format: json`` so the transcript comes back as ``{"text": ...}``.
Fully offline; the model is a local GGML/GGUF file loaded at server launch.

This is the speech twin of ``providers.llama_cpp.LlamaCppProvider`` and the
default speech backend for `urml translate --audio`: same project family,
same hermetic posture, same lazy-httpx adapter shape.

Install:

    pip install urml-llm-bridge[whisper_cpp]

Run a model locally first:

    whisper-server -m ./ggml-base.bin --port 8080

Usage:

    from urml_llm_bridge.speech.whisper_cpp import WhisperCppProvider

    provider = WhisperCppProvider()  # defaults to http://127.0.0.1:8080
    text = provider.transcribe(audio=wav_bytes, filename="request.wav")
"""

from __future__ import annotations

from typing import Any, Protocol

# whisper-server's default port. Note llama-server uses the same default;
# a deployment running both moves one of them with --speech-base-url.
DEFAULT_BASE_URL = "http://127.0.0.1:8080"

# whisper-server's transcription endpoint (multipart form upload).
INFERENCE_PATH = "/inference"


class _HTTPClient(Protocol):
    """Minimal httpx-shaped client surface this adapter uses."""

    def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        files: dict[str, Any],
        timeout: float,
    ) -> Any: ...


def _connect_error_types() -> tuple[type[BaseException], ...]:
    """Exception types that mean "could not reach the server".

    httpx is an optional extra, so the tuple is built at call time: with
    httpx installed it covers httpx's connect and timeout errors; without
    it (hermetic tests with an injected fake client) a plain
    ``ConnectionError`` still gets the friendly message.
    """
    types: tuple[type[BaseException], ...] = (ConnectionError,)
    try:
        import httpx
    except ImportError:
        return types
    return (*types, httpx.ConnectError, httpx.TimeoutException)


class WhisperCppProvider:
    """SpeechProvider adapter for whisper.cpp's ``whisper-server``.

    Provider-neutrality is preserved: the import of ``httpx`` is lazy, so
    ``urml_llm_bridge`` can be imported even when the extra is absent.
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        client: _HTTPClient | None = None,
        temperature: float = 0.0,
        timeout: float = 120.0,
    ) -> None:
        """Configure the adapter.

        Args:
            base_url:     URL of a running ``whisper-server``. Default is the
                          whisper.cpp standard ``http://127.0.0.1:8080``.
            client:       Pre-constructed httpx-shaped client for dependency
                          injection in tests.
            temperature:  Sampling temperature. Defaults to 0.0 for
                          deterministic transcripts.
            timeout:      HTTP timeout in seconds. The first call after a
                          server start can be slow while the model warms.
        """
        if client is None:
            try:
                import httpx
            except ImportError as exc:
                raise ImportError(
                    "WhisperCppProvider requires httpx. "
                    "Install with: pip install urml-llm-bridge[whisper_cpp]"
                ) from exc
            client = httpx.Client()
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._temperature = temperature
        self._timeout = timeout

    def transcribe(
        self,
        *,
        audio: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> str:
        """POST the audio to ``/inference`` and return the transcript."""
        data: dict[str, Any] = {
            "response_format": "json",
            "temperature": str(self._temperature),
        }
        if language is not None:
            data["language"] = language
        files = {"file": (filename, audio, "application/octet-stream")}
        try:
            response = self._client.post(
                self._base_url + INFERENCE_PATH,
                data=data,
                files=files,
                timeout=self._timeout,
            )
        except _connect_error_types() as exc:
            raise ConnectionError(
                f"could not reach whisper-server at {self._base_url}: {exc}. "
                "Is whisper-server running?"
            ) from exc
        return _extract_text(response)


def _extract_text(response: Any) -> str:
    """Pull the transcript out of a whisper-server JSON response.

    whisper-server's ``response_format: json`` shape::

        {"text": " Bring me the red mug from the kitchen.\\n"}
    """
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    payload = response.json() if callable(getattr(response, "json", None)) else response
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"whisper-server returned a non-object body of type {type(payload).__name__}"
        )
    text = payload.get("text")
    if not isinstance(text, str):
        raise RuntimeError(
            f"whisper-server response `text` was not a string (got {type(text).__name__})."
        )
    return text.strip()
