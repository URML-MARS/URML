"""Bridge-specific exception types.

These are surfaced by `Bridge.translate()` for failures that are not
*validation* errors (those flow through ValidationResult). They cover:

- Provider failure (the LLM call itself errored).
- Bridge-level invariants (revision budget exhausted; provider returned
  non-JSON output).
"""

from __future__ import annotations


class BridgeError(Exception):
    """Base class for bridge-specific failures."""


class ProviderError(BridgeError):
    """The LLM provider raised, returned an unparseable response, or otherwise misbehaved."""


class BridgeRevisionExhausted(BridgeError):  # noqa: N818 - "Exhausted" reads better than "ExhaustedError" here.
    """The validator never accepted the program within the configured revision budget.

    The last attempted program and ValidationResult are attached so the caller
    can decide whether to surface them, log them, or try another model. Every
    raw model emission is attached too (``raw_completions``), so a caller can
    save the final rejected emission for debugging (e.g. a small local LLM that
    never produces a valid program).
    """

    def __init__(
        self,
        message: str,
        *,
        last_result: object,
        attempts: int,
        raw_completions: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.last_result = last_result
        self.attempts = attempts
        #: Every raw model emission, in order; the last entry is the final
        #: rejected emission.
        self.raw_completions: list[str] = raw_completions or []


class BridgeClarificationNeeded(BridgeError):  # noqa: N818 - names the state, not an error class.
    """The model asked a clarifying question and no answer channel exists.

    Raised by ``Bridge.translate()`` in clarify mode (RFC-0700) when the
    model emits a ``{"clarify": ...}`` object and the caller supplied no
    ``on_clarify`` callback. The caller should relay ``question`` (and
    ``options``, when present) to the operator and retry the translation
    with the answer available — never invent an answer itself.
    """

    def __init__(
        self,
        message: str,
        *,
        question: str,
        options: list[str] | None = None,
        raw_completions: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.question = question
        self.options: list[str] = options or []
        #: Every raw model emission so far; the last entry is the clarify object.
        self.raw_completions: list[str] = raw_completions or []


class BridgePolicyViolation(BridgeError):  # noqa: N818 - "Violation" reads better than "ViolationError".
    """The validator rejected the program for compliance-policy reasons.

    Raised by ``Bridge.translate()`` when *every* error in a validation result
    is in the ``policy.*`` namespace. Policy errors describe hardware
    provenance — they cannot be fixed by editing the URML program, so further
    revisions are pointless. The caller should surface the violation to the
    user (or pick a different robot, or update the policy).
    """

    def __init__(
        self,
        message: str,
        *,
        last_result: object,
        attempts: int,
        raw_completions: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.last_result = last_result
        self.attempts = attempts
        #: Every raw model emission, in order; the last entry is the final
        #: rejected emission.
        self.raw_completions: list[str] = raw_completions or []
