"""OpenAI provider adapter.

Uses OpenAI's **JSON mode** (``response_format={"type": "json_object"}``)
as the structured-output mechanism. The URML schema is conveyed via the
system prompt; JSON mode guarantees the response *is* JSON, and the
URML validator catches any schema violations downstream as part of the
bridge's revision loop.

We deliberately avoid OpenAI's stricter ``json_schema`` mode in this
first adapter because it imposes constraints (every field required, no
``oneOf``, no ``pattern``) that pydantic-generated schemas violate. A
follow-up may add a schema-preprocessing path that satisfies strict mode.

Install:

    pip install urml-llm-bridge[openai]

Usage:

    from urml_llm_bridge import Bridge
    from urml_llm_bridge.providers.openai import OpenAIProvider

    provider = OpenAIProvider(model="gpt-4o")  # uses OPENAI_API_KEY env var
    bridge = Bridge(provider=provider, manifest=manifest, ...)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from openai import OpenAI


# Default to a recent capable OpenAI workhorse model.
DEFAULT_MODEL = "gpt-4o"

# Per-request timeout (seconds). The dedicated `ollama` / `llama_cpp` providers
# already expose one; the OpenAI provider also serves any OpenAI-compatible
# server (Ollama, LM Studio, vLLM) via OPENAI_BASE_URL, where a cold start that
# loads a multi-GB local model on the first call can be slow. None means "use the
# OpenAI SDK default"; the URML_OPENAI_TIMEOUT env var raises it without a code or
# CLI change.
TIMEOUT_ENV = "URML_OPENAI_TIMEOUT"


def _resolve_timeout(explicit: float | None) -> float | None:
    """An explicit timeout wins; otherwise read URML_OPENAI_TIMEOUT, else None."""
    if explicit is not None:
        return explicit
    raw = os.environ.get(TIMEOUT_ENV)
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


class OpenAIProvider:
    """LLMProvider adapter for OpenAI chat-completion models.

    Provider-neutrality is preserved: the import of `openai` is lazy,
    so `urml_llm_bridge` can be imported even when the SDK is absent.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: OpenAI | None = None,
        max_tokens: int = 4096,
        timeout: float | None = None,
    ) -> None:
        """Configure the adapter.

        Args:
            model:      OpenAI model ID. Defaults to ``gpt-4o``.
            api_key:    Explicit API key. Falls back to ``$OPENAI_API_KEY``.
            client:     Pre-constructed ``OpenAI`` client for dependency
                        injection in tests. If given, ``api_key`` and ``timeout``
                        are ignored (configure them on the injected client).
            max_tokens: Default `max_tokens` for completions; overridable per call.
            timeout:    Per-request timeout in seconds. Falls back to
                        ``$URML_OPENAI_TIMEOUT``, then the OpenAI SDK default.
                        Raise it for a slow local model behind ``OPENAI_BASE_URL``
                        (a cold start that loads a multi-GB model can be slow).
        """
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise ImportError(
                    "OpenAIProvider requires the openai SDK. "
                    "Install with: pip install urml-llm-bridge[openai]"
                ) from exc
            kwargs: dict[str, Any] = {"api_key": api_key or os.environ.get("OPENAI_API_KEY")}
            resolved_timeout = _resolve_timeout(timeout)
            if resolved_timeout is not None:
                kwargs["timeout"] = resolved_timeout
            client = OpenAI(**kwargs)
        self._client = client
        self._model = model
        self._default_max_tokens = max_tokens

    def complete(
        self,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],  # schema is conveyed via `system`; kept for protocol parity
        max_tokens: int = 4096,
    ) -> str:
        """Call the model in JSON mode and return the raw JSON content string.

        The schema is conveyed in the system prompt (the bridge builds the
        prompt with the JSON Schema inlined); JSON mode here guarantees the
        response is *a* JSON object. Conformance to the schema is validated
        downstream by ``urml_validator.validate()``.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            max_tokens=max_tokens or self._default_max_tokens,
        )
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("OpenAI response.choices[0].message.content is None")
        return content
