"""Anthropic provider adapter.

Uses Anthropic's **tool use** as the structured-output mechanism: the
URML program JSON Schema is registered as a single tool named
`emit_urml`, and the model is forced to call it via `tool_choice`. The
tool call's input is the URML program, already JSON-parseable.

Install:

    pip install urml-llm-bridge[anthropic]

Usage:

    from urml_llm_bridge import Bridge
    from urml_llm_bridge.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(model="claude-sonnet-4-6")  # uses ANTHROPIC_API_KEY env var
    bridge = Bridge(provider=provider, manifest=manifest, ...)
    result = bridge.translate("Bring me the red mug from the kitchen.")
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from anthropic import Anthropic


# Default to a recent capable Anthropic workhorse model. Override in the
# constructor for higher-capability calls (e.g., claude-opus-4-7 for
# difficult disambiguation) or cheaper calls (claude-haiku-4-5).
DEFAULT_MODEL = "claude-sonnet-4-6"

# The name registered with the Anthropic API for the URML emission tool.
# Stable; downstream tracing/observability code may filter on it.
EMIT_TOOL_NAME = "emit_urml"


class AnthropicProvider:
    """LLMProvider adapter for the Anthropic Claude family.

    Provider-neutrality is preserved: the import of `anthropic` is lazy,
    so `urml_llm_bridge` can be imported even when the SDK is absent.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: Anthropic | None = None,
        max_tokens: int = 4096,
    ) -> None:
        """Configure the adapter.

        Args:
            model:      Anthropic model ID. Defaults to the Sonnet workhorse.
            api_key:    Explicit API key. Falls back to ``$ANTHROPIC_API_KEY``.
            client:     Pre-constructed ``Anthropic`` client for dependency
                        injection in tests. If given, ``api_key`` is ignored.
            max_tokens: Default `max_tokens` for completions; overridable per call.
        """
        if client is None:
            try:
                from anthropic import Anthropic
            except ImportError as exc:
                raise ImportError(
                    "AnthropicProvider requires the anthropic SDK. "
                    "Install with: pip install urml-llm-bridge[anthropic]"
                ) from exc
            client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self._client = client
        self._model = model
        self._default_max_tokens = max_tokens

    def complete(
        self,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],
        max_tokens: int = 4096,
    ) -> str:
        """Call the model with the URML schema registered as a tool.

        Returns the JSON-serialized tool input — i.e., the URML program
        the model emitted. Raises if the response contains no
        ``emit_urml`` tool_use block.
        """
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens or self._default_max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            tools=[
                {
                    "name": EMIT_TOOL_NAME,
                    "description": "Emit the URML program corresponding to the user's request.",
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": EMIT_TOOL_NAME},
        )
        for block in response.content:
            # ToolUseBlock has .type == "tool_use", .name == EMIT_TOOL_NAME, and .input.
            # `getattr` keeps the read duck-typed so test doubles work and mypy doesn't
            # try to narrow the SDK's wide union of block types.
            if (
                getattr(block, "type", None) == "tool_use"
                and getattr(block, "name", None) == EMIT_TOOL_NAME
            ):
                payload = getattr(block, "input", None)
                if payload is None:
                    raise RuntimeError(
                        f"Anthropic {EMIT_TOOL_NAME!r} tool_use block had no `input`."
                    )
                return json.dumps(payload)
        raise RuntimeError(
            f"Anthropic response did not contain an {EMIT_TOOL_NAME!r} tool_use block "
            "despite tool_choice forcing it."
        )
