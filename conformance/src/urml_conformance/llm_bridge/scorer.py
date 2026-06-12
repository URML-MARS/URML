"""LLM-bridge scoring harness (RFC-0021).

`score()` drives `urml_llm_bridge.Bridge` over a profile's utterance set with
one `(model, backend)` and tallies the two published numbers — structural and
semantic pass rates — plus the mean revision count, returning a `ResultRow`.

The harness is **backend-neutral**: it names no LLM, takes any object
implementing the `LLMProvider` Protocol, and works identically for a
grammar-constrained `llama_cpp` backend, a soft-JSON `ollama`/`openai` backend,
a cloud `anthropic` backend, or the hermetic `EchoProvider`. The v0.1 PR
exercises the echo path (see `tests/test_llm_bridge_scorer.py`); real-model rows
that require a GGUF artifact and a running server are a follow-up project.

`urml_llm_bridge` is imported lazily inside `score()` so this package's loader
(pure pydantic-free dataclasses + PyYAML) keeps zero bridge dependency; install
the optional `urml-conformance[llm-bridge]` extra to run the scorer.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal

from urml_conformance.llm_bridge.loader import ResultRow, UtteranceSet

if TYPE_CHECKING:  # pragma: no cover - typing only
    from urml_llm_bridge.providers.base import LLMProvider

Backend = Literal["llama_cpp", "ollama", "anthropic", "openai", "echo"]


def _emits_report_failure(program: dict[str, Any] | None) -> bool:
    """True if the program's behavior contains a `report(status: failure)` step.

    The `report_failure` expected-kind asks the bridge to decline honestly —
    emit a report naming what the manifest does not cover — rather than invent
    capability. Walks nested behaviors (sequence / parallel / branch) defensively.
    """
    if not isinstance(program, dict):
        return False

    def _walk(node: Any) -> bool:
        if isinstance(node, dict):
            report = node.get("report")
            if isinstance(report, dict) and report.get("status") == "failure":
                return True
            return any(_walk(v) for v in node.values())
        if isinstance(node, list):
            return any(_walk(item) for item in node)
        return False

    return _walk(program.get("behavior", {}))


def _is_structural(raw_completion: str) -> bool:
    """True if a raw emission parses as JSON and matches the program's structural shape.

    Structural validity is the JSON-shape gate (the place a GBNF grammar enforces
    at decode time); semantic validity — capabilities, envelope, policy — is the
    validator's job and is counted separately.
    """
    from urml_validator.schemas.program import URMLProgram

    try:
        parsed = json.loads(raw_completion)
    except (json.JSONDecodeError, TypeError):
        return False
    try:
        URMLProgram.model_validate(parsed)
    except Exception:  # pydantic ValidationError or anything malformed
        return False
    return True


def score(
    *,
    provider: "LLMProvider",
    utterances: UtteranceSet,
    manifest: dict[str, Any],
    backend: Backend,
    model_id: str,
    recorded_at: str,
    row_id: str | None = None,
    model_size_b: float = 0.0,
    hardware_class: str = "unspecified",
    max_revisions: int = 3,
    envelope: dict[str, Any] | None = None,
    policy: dict[str, Any] | None | Literal["DEFAULT"] = None,
    notes: str = "",
) -> ResultRow:
    """Score one ``(model, backend, profile)`` triple against an utterance set.

    Drives the bridge once per utterance and tallies:

    - ``structural_pass_rate`` — fraction whose first raw emission parses as JSON
      and matches the program schema's structural shape.
    - ``semantic_pass_rate`` — fraction whose outcome matches the utterance's
      ``expected_kind``: a ``positive`` utterance yields a validator-accepted
      program; a ``report_failure`` utterance yields a ``report(status: failure)``.
    - ``revision_attempts_mean`` — mean validator-feedback revisions; an
      exhausted budget counts as ``max_revisions + 1``.

    The caller supplies the wall-clock ``recorded_at`` (this package never reads
    the clock, keeping runs reproducible).
    """
    from urml_llm_bridge import Bridge
    from urml_llm_bridge.errors import BridgePolicyViolation, BridgeRevisionExhausted

    n = len(utterances.utterances)
    if n == 0:
        raise ValueError("cannot score an empty utterance set")

    structural = 0
    semantic = 0
    rev_total = 0.0
    for utt in utterances.utterances:
        bridge = Bridge(
            provider=provider,
            manifest=manifest,
            envelope=envelope,
            profiles=(utterances.profile,),
            max_revisions=max_revisions,
            policy=policy,
        )
        try:
            result = bridge.translate(utt.text)
        except (BridgeRevisionExhausted, BridgePolicyViolation) as exc:
            rev_total += float(max_revisions + 1)
            raw = getattr(exc, "raw_completions", None)
            if raw and _is_structural(raw[0]):
                structural += 1
            continue
        rev_total += float(result.revision_count)
        if result.raw_completions and _is_structural(result.raw_completions[0]):
            structural += 1
        if utt.expected_kind == "positive":
            if result.accepted:
                semantic += 1
        elif _emits_report_failure(result.program):
            semantic += 1

    return ResultRow(
        row_id=row_id or f"{model_id}-{backend}-{utterances.profile}-{recorded_at[:10].replace('-', '')}",
        recorded_at=recorded_at,
        model_id=model_id,
        model_size_b=model_size_b,
        backend=backend,
        profile=utterances.profile,
        n_utterances=n,
        structural_pass_rate=round(structural / n, 4),
        semantic_pass_rate=round(semantic / n, 4),
        revision_attempts_mean=round(rev_total / n, 4),
        hardware_class=hardware_class,
        notes=notes,
    )
