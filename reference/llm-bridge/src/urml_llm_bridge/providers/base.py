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

#: RFC-0700: the inner payload of a clarifying question.
CLARIFY_INNER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "question": {"type": "string", "minLength": 1},
        "options": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["question"],
    "additionalProperties": False,
}

#: RFC-0700: the wire shape of a clarify emission — a single-key object.
CLARIFY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"clarify": CLARIFY_INNER_SCHEMA},
    "required": ["clarify"],
    "additionalProperties": False,
}


def build_clarify_union_schema(
    program_schema: dict[str, Any],
    clarify_schema: dict[str, Any],
) -> dict[str, Any]:
    """The program-or-clarify union for schema/grammar-constrained decoding.

    The program schema's ``$defs`` are hoisted to the union root: the GBNF
    derivation (and JSON-Schema resolvers generally) resolve ``$ref`` against
    the root schema, so a naive ``{"anyOf": [program, clarify]}`` would lose
    them.
    """
    program_branch = {k: v for k, v in program_schema.items() if k not in ("$defs", "definitions")}
    defs = dict(program_schema.get("$defs") or program_schema.get("definitions") or {})
    union: dict[str, Any] = {"anyOf": [program_branch, clarify_schema]}
    if defs:
        union["$defs"] = defs
    return union


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
        clarify_schema: dict[str, Any] | None = None,
    ) -> str:
        """Return a JSON string. The Bridge will JSON-parse and validate it.

        Args:
            system:     System prompt assembled by the bridge.
            user:       User's natural-language request.
            schema:     The JSON Schema the emitted JSON must match.
            max_tokens: Soft cap on output tokens. Providers may interpret
                        loosely if their API expresses limits differently.
            clarify_schema: RFC-0700 clarify mode only (default None = off).
                        When set, the emission may ALSO be an object matching
                        this schema (`{"clarify": {...}}`), and a provider
                        that constrains decoding MUST widen its constraint to
                        the union of the two (see
                        ``build_clarify_union_schema``). Providers without
                        constrained decoding may ignore it; the prompt
                        carries the contract.

        Returns:
            A string containing a single JSON object. Need not be pretty-
            formatted; the bridge parses it. Must not be wrapped in
            Markdown fences — providers should return raw JSON.

        Raises:
            Implementation-specific exceptions may bubble through; the
            Bridge wraps them in `ProviderError` for callers.
        """
        ...
