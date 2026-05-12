"""The LLMProvider Protocol — the contract every adapter implements.

The Bridge talks to LLMs *only* through this protocol. Anything that
implements `complete(system, user, schema, ...)` returning a JSON string
is a valid provider — including hermetic test doubles like
`EchoProvider`, real cloud SDKs (Anthropic, OpenAI), local-inference
backends (vLLM, llama.cpp, Ollama), or future on-device runtimes.

Provider-neutrality is structural: the bridge has no hard import of any
particular SDK. Adding a new provider is a small adapter file, not a
change to the bridge itself.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Translate a natural-language request into JSON matching `schema`.

    Implementations should use their native structured-output mechanism
    where one exists (Anthropic tool use, OpenAI JSON mode, constrained
    decoding for open-weights serving). Implementations that don't have
    structured output may post-validate by parsing JSON and re-prompting;
    that is an implementation choice, not a protocol concern.
    """

    def complete(
        self,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],
        max_tokens: int = 4096,
    ) -> str:
        """Return a JSON string. The Bridge will JSON-parse and validate it.

        Args:
            system:     System prompt assembled by the bridge.
            user:       User's natural-language request.
            schema:     The JSON Schema the emitted JSON must match.
            max_tokens: Soft cap on output tokens. Providers may interpret
                        loosely if their API expresses limits differently.

        Returns:
            A string containing a single JSON object. Need not be pretty-
            formatted; the bridge parses it. Must not be wrapped in
            Markdown fences — providers should return raw JSON.

        Raises:
            Implementation-specific exceptions may bubble through; the
            Bridge wraps them in `ProviderError` for callers.
        """
        ...
