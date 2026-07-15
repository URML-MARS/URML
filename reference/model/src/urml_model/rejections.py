"""Mine rejected bridge emissions into repair training records (RFC-0666).

A bridge translation session that needed revisions is a free preference
signal: the failed attempts (with the validator's error codes for each)
versus the finally accepted program, all for the same utterance. This
module turns those sessions into `rejection_repair` records, exportable as
SFT-with-error-context or DPO preference pairs.

`TranslateResult.raw_completions` carries every attempt, not just the last
(the CLI's `--save-rejected` persists only the final one; consume the
result object programmatically to get the full trace).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from urml_llm_bridge.bridge import TranslateResult
from urml_validator import validate

from urml_model.dataset import DatasetRecord, ValidatorVerdict
from urml_model.mining import PolicyArg


@dataclass(frozen=True)
class RejectionSession:
    """One bridge translation session: the utterance, every raw attempt, the outcome."""

    nl: str
    raw_completions: tuple[str, ...]
    accepted_program: dict[str, Any] | None


def session_from_result(nl: str, result: TranslateResult) -> RejectionSession:
    """Build a session from a successful `Bridge.translate()` result.

    When the result was accepted after revisions, everything before the
    last completion is a failed attempt. An exhausted or policy-violating
    session (the bridge raised) has no accepted program; build the session
    from the exception's `raw_completions` directly with
    `RejectionSession(nl, tuple(exc.raw_completions), None)`.
    """
    raw = tuple(result.raw_completions)
    if result.accepted and result.program is not None:
        return RejectionSession(nl=nl, raw_completions=raw[:-1], accepted_program=result.program)
    return RejectionSession(nl=nl, raw_completions=raw, accepted_program=None)


def mine_rejections(
    sessions: list[RejectionSession],
    *,
    manifest: dict[str, Any],
    manifest_ref: str,
    profile: str,
    envelope: dict[str, Any] | None = None,
    envelope_ref: str | None = None,
    policy: PolicyArg = "DEFAULT",
    language: str = "en",
) -> list[DatasetRecord]:
    """Turn revision sessions into rejection_repair records.

    Sessions without an accepted program are skipped: a repair record needs
    a repair target. Attempts that do not parse as JSON are skipped too
    (the record schema requires a program object); the parse failure itself
    is a decoding concern the GBNF grammar path already solves.
    """
    records: list[DatasetRecord] = []
    for session in sessions:
        if session.accepted_program is None:
            continue
        for raw in session.raw_completions:
            try:
                program = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(program, dict):
                continue
            verdict = validate(program, manifest, envelope, profiles=(profile,), policy=policy)
            if verdict.accepted:
                continue
            records.append(
                DatasetRecord(
                    nl=session.nl,
                    program=program,
                    manifest_ref=manifest_ref,
                    profile=profile,
                    language=language,
                    provenance="rejection_repair",
                    validator_verdict=ValidatorVerdict(accepted=False, error_codes=verdict.codes()),
                    envelope_ref=envelope_ref,
                    repair=session.accepted_program,
                )
            )
    return records
