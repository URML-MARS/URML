"""llama.cpp on-device provider adapter.

Talks to a running ``llama-server`` (from the llama.cpp project) over its
OpenAI-compatible ``/v1/chat/completions`` endpoint, passing the URML
program schema's derived GBNF grammar as an extra field. The grammar makes
structurally invalid URML unrepresentable at the decoder; whatever the
adapter returns is guaranteed to be parseable JSON, and the validator
catches the semantic residue downstream via the bridge's revision loop
(see [Layer 4 v0.1.0](../../../../../spec/layer-4-nl-grammar/v0.1.0.md)
§3, RFC-0021 §Detailed-design).

Install:

    pip install urml-llm-bridge[llama_cpp]

Run a model locally first:

    llama-server -m ./SmolLM-360M-Q4.gguf --port 8080

Usage:

    from urml_llm_bridge import Bridge
    from urml_llm_bridge.providers.llama_cpp import LlamaCppProvider

    provider = LlamaCppProvider()  # defaults to http://127.0.0.1:8080
    bridge = Bridge(provider=provider, manifest=manifest, ...)
    result = bridge.translate("Bring me the red mug from the kitchen.")
"""

from __future__ import annotations

from typing import Any, Protocol

from urml_llm_bridge.grammar import schema_to_gbnf

# llama-server's default port. Override in the constructor for non-default
# deployments.
DEFAULT_BASE_URL = "http://127.0.0.1:8080"

# The path on llama-server that accepts OpenAI-shaped chat requests with the
# llama.cpp ``grammar`` extra honored.
CHAT_COMPLETIONS_PATH = "/v1/chat/completions"

# Stable model placeholder. llama-server ignores the ``model`` field
# (the loaded GGUF is fixed at server launch), but the OpenAI schema
# requires the field; this string is what shows up in logs/traces.
DEFAULT_MODEL_LABEL = "llama-cpp-local"


class _HTTPClient(Protocol):
    """Minimal httpx-shaped client surface this adapter uses.

    Defined as a Protocol so tests can inject a hand-rolled fake without
    pulling httpx, and so mypy stays happy when the real httpx isn't
    installed at type-check time."""

    def post(self, url: str, *, json: dict[str, Any], timeout: float) -> Any: ...


class LlamaCppProvider:
    """LLMProvider adapter for llama.cpp's ``llama-server``.

    Provider-neutrality is preserved: the import of ``httpx`` is lazy, so
    ``urml_llm_bridge`` can be imported even when the extra is absent.
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        client: _HTTPClient | None = None,
        model_label: str = DEFAULT_MODEL_LABEL,
        temperature: float = 0.0,
        timeout: float = 120.0,
    ) -> None:
        """Configure the adapter.

        Args:
            base_url:     URL of a running ``llama-server``. Default is the
                          llama.cpp standard ``http://127.0.0.1:8080``.
            client:       Pre-constructed httpx-shaped client for dependency
                          injection in tests. If given, ``base_url`` is still
                          used to construct the final POST URL.
            model_label:  String forwarded as the OpenAI ``model`` field.
                          llama-server ignores it; it shows up in traces.
            temperature:  Sampling temperature. Defaults to 0.0 for
                          deterministic emissions (a URML program produced
                          by the bridge must be reproducible).
            timeout:      HTTP timeout in seconds. The first call after a
                          server start can be slow while the model warms.
        """
        if client is None:
            try:
                import httpx
            except ImportError as exc:
                raise ImportError(
                    "LlamaCppProvider requires httpx. "
                    "Install with: pip install urml-llm-bridge[llama_cpp]"
                ) from exc
            client = httpx.Client()
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._model_label = model_label
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
        """Send a chat completion with the schema-derived GBNF grammar.

        The grammar is computed via ``grammar.schema_to_gbnf(schema)`` and
        cached at the module level; repeated calls with the same schema do
        no extra work.
        """
        grammar = schema_to_gbnf(schema)
        body: dict[str, Any] = {
            "model": self._model_label,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": self._temperature,
            # llama-server's OpenAI-compat layer honors ``grammar`` as an
            # extra; non-llama-cpp servers will ignore it and fall back to
            # unconstrained decoding. The adapter is explicit about its
            # target server in the docstring.
            "grammar": grammar,
        }
        response = self._client.post(
            self._base_url + CHAT_COMPLETIONS_PATH,
            json=body,
            timeout=self._timeout,
        )
        return _extract_content(response)


def _extract_content(response: Any) -> str:
    """Pull the assistant content out of an OpenAI-compat chat response.

    Tolerates both the real httpx ``Response`` object (with ``.json()``)
    and a hand-rolled fake that returns a dict directly from ``.json()``.
    """
    if hasattr(response, "raise_for_status"):
        response.raise_for_status()
    payload = response.json() if callable(getattr(response, "json", None)) else response
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"llama-server returned a non-object body of type {type(payload).__name__}"
        )
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("llama-server response had no `choices`.")
    first = choices[0]
    if not isinstance(first, dict):
        raise RuntimeError("llama-server response `choices[0]` was not an object.")
    message = first.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("llama-server response `choices[0].message` was not an object.")
    content = message.get("content")
    if not isinstance(content, str):
        raise RuntimeError(
            f"llama-server response message.content was not a string "
            f"(got {type(content).__name__})."
        )
    return content
