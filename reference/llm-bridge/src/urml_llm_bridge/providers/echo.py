"""EchoProvider — a hermetic LLMProvider for testing.

EchoProvider does NOT call any LLM. It returns pre-canned JSON responses
keyed by a simple match against the user request. Tests use this to
exercise the bridge end-to-end without network, API keys, or non-
determinism.

Two match modes are supported:

1. **Exact match** — request strings are looked up verbatim in `responses`.
2. **Substring match** — when `match_substrings=True`, the first key that
   appears as a substring of the user request is used. Useful for
   tolerating minor wording variation in fixtures.

A `scripted` mode lets a test return a *sequence* of responses on
successive calls — convenient for testing the revision loop, where the
first response is intentionally invalid and the second is correct.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


class EchoProvider:
    """Deterministic, network-free provider for tests.

    Implements the `LLMProvider` Protocol. Not registered as a subclass
    — Protocols are structurally checked.
    """

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        *,
        scripted: list[str] | None = None,
        match_substrings: bool = False,
    ) -> None:
        """Configure the provider.

        Args:
            responses:        Map of user-request string -> JSON response string.
            scripted:         If set, ignore `responses` and return each entry on
                              successive calls (the bridge calls `complete` once per
                              revision attempt).
            match_substrings: If True, find the first key in `responses` that is a
                              substring of the user request. Default: exact match.
        """
        if responses is None and scripted is None:
            raise ValueError("EchoProvider requires either `responses` or `scripted`")
        if responses is not None and scripted is not None:
            raise ValueError("EchoProvider: pass exactly one of `responses` or `scripted`")
        self._responses = responses or {}
        self._scripted = list(scripted) if scripted is not None else None
        self._iter: Iterator[str] | None = iter(self._scripted) if self._scripted is not None else None
        self._match_substrings = match_substrings
        self.call_log: list[dict[str, Any]] = []

    def complete(
        self,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],
        max_tokens: int = 4096,
    ) -> str:
        """Return the pre-canned response for `user` (or the next scripted entry)."""
        self.call_log.append({"system": system, "user": user, "schema": schema, "max_tokens": max_tokens})
        if self._iter is not None:
            try:
                return next(self._iter)
            except StopIteration as exc:
                raise KeyError("EchoProvider: scripted responses exhausted") from exc
        if self._match_substrings:
            for needle, response in self._responses.items():
                if needle in user:
                    return response
            raise KeyError(f"EchoProvider: no substring match for user request {user!r}")
        if user not in self._responses:
            raise KeyError(f"EchoProvider: no response registered for user request {user!r}")
        return self._responses[user]
