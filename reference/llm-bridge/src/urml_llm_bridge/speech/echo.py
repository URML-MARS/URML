"""Hermetic speech provider: returns a canned transcript.

The speech twin of ``providers.echo.EchoProvider``. No audio processing, no
network. Used by tests and by hermetic CLI demos (`--speech-provider echo
--echo-transcript "..."`) so the audio path can be exercised end to end
without a speech model on the host.
"""

from __future__ import annotations


class EchoSpeechProvider:
    """SpeechProvider that ignores the audio and returns a fixed string."""

    def __init__(self, *, text: str) -> None:
        self._text = text

    def transcribe(
        self,
        *,
        audio: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> str:
        return self._text
