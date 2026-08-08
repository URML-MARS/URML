"""The speech-provider contract (RFC-0670).

A speech provider turns recorded audio into the natural-language text that
the LLM bridge translates. It is deliberately the smallest possible surface,
mirroring ``providers.base.LLMProvider``: one method, structural typing, no
registration. Anything with a matching ``transcribe`` works, including
hand-rolled fakes in tests.

Speech sits strictly in front of the bridge: the transcript feeds the same
``Bridge.translate()`` path a typed request does, so the validator boundary
is untouched. A bad transcription produces a bad request, and the validator
gates it exactly as it gates a bad typed request.

Adapters shipped alongside this Protocol:

- ``whisper_cpp.py``: a local ``whisper-server`` (whisper.cpp), on-device.
- ``openai.py``: OpenAI's transcription API, or any OpenAI-compatible
  transcription endpoint via ``base_url``.
- ``echo.py``: a hermetic canned-transcript provider for tests and demos.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SpeechProvider(Protocol):
    """Anything that can turn audio bytes into a transcript string."""

    def transcribe(
        self,
        *,
        audio: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> str:
        """Transcribe ``audio`` and return the text.

        Args:
            audio:    The raw audio file content. WAV (16 kHz mono PCM) is
                      the safest interchange format across backends.
            filename: The original file name; some backends sniff the
                      container format from its extension.
            language: Optional ISO 639-1 language hint (``"he"``, ``"es"``,
                      ``"ja"``). None lets the backend auto-detect.
        """
        ...
