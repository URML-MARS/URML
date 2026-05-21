"""Ollama on-device provider adapter.

Talks to a running ``ollama serve`` over its native ``/api/chat`` endpoint,
passing the URML program schema in the ``format`` field. Ollama 0.5+
honors ``format`` as a JSON Schema constraint when the server is built
against a recent llama.cpp; older versions treat it as a soft "produce JSON"
hint. Either way the adapter forwards the schema and the bridge's
validator-feedback revision loop catches any residue.

This adapter exists for **developer convenience**: ``ollama pull`` and
``ollama run`` are the lowest-friction path to experiment with local
models. For production deployments that need token-level structural
guarantees, prefer ``LlamaCppProvider``: llama-server's ``grammar``
parameter is an unambiguous hard gate, while Ollama's enforcement strength
depends on the server build.

Install:

    pip install urml-llm-bridge[ollama]

Pull a model first:

    ollama pull llama3.2:1b
    ollama serve   # if not already running

Usage:

    from urml_llm_bridge import Bridge
    from urml_llm_bridge.providers.ollama import OllamaProvider

    provider = OllamaProvider(model="llama3.2:1b")
    bridge = Bridge(provider=provider, manifest=manifest, ...)
    result = bridge.translate("Bring me the red mug from the kitchen.")
"""

from __future__ import annotations

from typing import Any, Protocol

# Ollama's default port (`ollama serve`).
DEFAULT_BASE_URL = "http://127.0.0.1:11434"

# Native Ollama chat endpoint. Accepts ``model``, ``messages``, ``format``
# (string or JSON Schema), ``stream``, ``options``.
CHAT_PATH = "/api/chat"


class _HTTPClient(Protocol):
    """Minimal httpx-shaped client surface this adapter uses."""

    def post(self, url: str, *, json: dict[str, Any], timeout: float) -> Any: ...


class OllamaProvider:
    """LLMProvider adapter for Ollama's chat API.

    Provider-neutrality is preserved: the import of ``httpx`` is lazy, so
    ``urml_llm_bridge`` can be imported even when the extra is absent.
    """

    def __init__(
        self,
        *,
        model: str,
        base_url: str = DEFAULT_BASE_URL,
        client: _HTTPClient | None = None,
        temperature: float = 0.0,
        timeout: float = 120.0,
    ) -> None:
        """Configure the adapter.

        Args:
            model:        Ollama model tag (e.g. ``"llama3.2:1b"``,
                          ``"smollm:135m"``). Required: Ollama needs to know
                          which loaded model to dispatch to.
            base_url:     URL of a running ``ollama serve``. Default is the
                          Ollama standard ``http://127.0.0.1:11434``.
            client:       Pre-constructed httpx-shaped client for dependency
                          injection in tests.
            temperature:  Sampling temperature. Defaults to 0.0 for
                          deterministic emissions.
            timeout:      HTTP timeout in seconds.
        """
        if client is None:
            try:
                import httpx
            except ImportError as exc:
                raise ImportError(
                    "OllamaProvider requires httpx. "
                    "Install with: pip install urml-llm-bridge[ollama]"
                ) from exc
            client = httpx.Client()
        self._client = client
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._temperature = temperature
        self._timeout = timeout

    def complete(
        self,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat request with the URML schema as ``format``.

        On Ollama 0.5+ the schema is honored as a JSON-Schema constraint
        on the decoder. On older builds it degrades to "produce JSON";
        in both cases the validator catches residue.
        """
        body: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": self._temperature,
                "num_predict": max_tokens,
            },
        }
        response = self._client.post(
            self._base_url + CHAT_PATH,
            json=body,
            timeout=self._timeout,
        )
        return _extract_content(response)


def _extract_content(response: Any) -> str:
    """Pull the assistant message content out of an Ollama chat response.

    Ollama's non-streaming response shape::

        {"model": "...", "message": {"role": "assistant", "content": "..."}, ...}
    """
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    payload = response.json() if callable(getattr(response, "json", None)) else response
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"ollama returned a non-object body of type {type(payload).__name__}"
        )
    message = payload.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("ollama response had no object `message`.")
    content = message.get("content")
    if not isinstance(content, str):
        raise RuntimeError(
            f"ollama response message.content was not a string "
            f"(got {type(content).__name__})."
        )
    return content
