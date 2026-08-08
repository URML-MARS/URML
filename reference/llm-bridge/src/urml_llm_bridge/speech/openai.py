"""OpenAI transcription speech provider (RFC-0670).

Uses the OpenAI audio transcription API (``/v1/audio/transcriptions``)
through the official SDK. With ``base_url`` set, the same adapter targets
any OpenAI-compatible transcription server, mirroring how
``providers.openai.OpenAIProvider`` serves OpenAI-compatible chat servers.

Install:

    pip install urml-llm-bridge[openai]

Usage:

    from urml_llm_bridge.speech.openai import OpenAISpeechProvider

    provider = OpenAISpeechProvider()  # reads OPENAI_API_KEY env var
    text = provider.transcribe(audio=wav_bytes, filename="request.wav")
"""

from __future__ import annotations

import io
import os
from typing import TYPE_CHECKING, Any

from urml_llm_bridge.providers.openai import _resolve_timeout

if TYPE_CHECKING:  # pragma: no cover
    from openai import OpenAI


# OpenAI's transcription workhorse. Newer transcribe-tuned chat models
# (gpt-4o-transcribe) are selectable via the `model` arg.
DEFAULT_MODEL = "whisper-1"


class OpenAISpeechProvider:
    """SpeechProvider adapter for OpenAI-shaped transcription endpoints.

    Provider-neutrality is preserved: the import of `openai` is lazy,
    so `urml_llm_bridge` can be imported even when the SDK is absent.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        base_url: str | None = None,
        client: OpenAI | None = None,
        timeout: float | None = None,
    ) -> None:
        """Configure the adapter.

        Args:
            model:    Transcription model ID. Defaults to ``whisper-1``.
            api_key:  Explicit API key. Falls back to ``$OPENAI_API_KEY``.
            base_url: Endpoint of an OpenAI-compatible transcription server.
                      Falls back to the SDK's own ``$OPENAI_BASE_URL``
                      handling when None.
            client:   Pre-constructed ``OpenAI`` client for dependency
                      injection in tests. If given, ``api_key``, ``base_url``
                      and ``timeout`` are ignored (configure them on the
                      injected client).
            timeout:  Per-request timeout in seconds. Falls back to
                      ``$URML_OPENAI_TIMEOUT``, then the OpenAI SDK default.
        """
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise ImportError(
                    "OpenAISpeechProvider requires the openai SDK. "
                    "Install with: pip install urml-llm-bridge[openai]"
                ) from exc
            kwargs: dict[str, Any] = {"api_key": api_key or os.environ.get("OPENAI_API_KEY")}
            if base_url is not None:
                kwargs["base_url"] = base_url
            resolved_timeout = _resolve_timeout(timeout)
            if resolved_timeout is not None:
                kwargs["timeout"] = resolved_timeout
            client = OpenAI(**kwargs)
        self._client = client
        self._model = model

    def transcribe(
        self,
        *,
        audio: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> str:
        """Send the audio to the transcription endpoint and return the text."""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "file": (filename, io.BytesIO(audio)),
        }
        if language is not None:
            kwargs["language"] = language
        result = self._client.audio.transcriptions.create(**kwargs)
        text = getattr(result, "text", None)
        if not isinstance(text, str):
            raise RuntimeError(
                f"transcription response `text` was not a string "
                f"(got {type(text).__name__})."
            )
        return text.strip()
