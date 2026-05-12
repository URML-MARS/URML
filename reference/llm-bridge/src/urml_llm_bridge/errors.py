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
    can decide whether to surface them, log them, or try another model.
    """

    def __init__(self, message: str, *, last_result: object, attempts: int) -> None:
        super().__init__(message)
        self.last_result = last_result
        self.attempts = attempts
