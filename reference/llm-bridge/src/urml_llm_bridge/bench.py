"""Benchmark harness: how well does a given model speak URML?

This module is a BENCHMARK, not a conformance test (see `conformance/README.md`
for the distinction). It runs a corpus of natural-language utterances through
`Bridge.translate()` against one manifest and reports where each landed:

  accepted          the validator accepted a program that does real work
  honest_refusal    the validator accepted a program whose root behavior is
                    only `report(status: failure)`: the model declined
  invalid_emission  the revision budget ran out without an accepted program
  provider_error    the provider raised, or emitted non-JSON
  policy_block      only `policy.*` errors remained (RFC-0004 short-circuit)

Classification is derived from the bridge's own control flow, so a benchmark
run measures exactly what a `urml translate` user would experience, repair
step included.

Two deliberate divergences from the RFC-0021 conformance scorer
(`urml_conformance.llm_bridge.scorer`), which stays untouched:

  1. `honest_refusal` requires the ROOT behavior to be report-only. A program
     that moves the robot and then reports failure did real work and counts
     as `accepted`; the scorer's anywhere-in-tree match would misfile it.
  2. A per-utterance `ProviderError` costs that row, never the run.

`expected` from the corpus maps to a separate `expected_match` boolean, so a
model that honestly refuses a doable request is recorded as an honest refusal
that missed expectations, never binned with invalid output.

`revision_attempts_mean` averages `revision_count` over rows where the bridge
returned a result (accepted or honest_refusal); failed rows have no
comparable number and are excluded.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml

from urml_llm_bridge.bridge import Bridge
from urml_llm_bridge.errors import (
    BridgePolicyViolation,
    BridgeRevisionExhausted,
    ProviderError,
)

Outcome = Literal[
    "accepted",
    "honest_refusal",
    "invalid_emission",
    "provider_error",
    "policy_block",
]

OUTCOMES: tuple[Outcome, ...] = (
    "accepted",
    "honest_refusal",
    "invalid_emission",
    "provider_error",
    "policy_block",
)

Expected = Literal["accept", "refuse"]

_EXPECTED_ALIASES: dict[str, Expected] = {
    # Native bench spelling.
    "accept": "accept",
    "refuse": "refuse",
    # RFC-0021 conformance-fixture spelling, so the existing utterance sets
    # under conformance/llm-bridge/fixtures/ load unchanged.
    "positive": "accept",
    "report_failure": "refuse",
}


class BenchCorpusError(ValueError):
    """The corpus file is missing or malformed."""


@dataclass(frozen=True)
class BenchUtterance:
    """One benchmark row: a request and what a good model should do with it."""

    id: str
    text: str
    expected: Expected


@dataclass(frozen=True)
class BenchCorpus:
    """A parsed utterance corpus."""

    corpus_id: str
    profile: str
    language: str
    utterances: tuple[BenchUtterance, ...]


@dataclass(frozen=True)
class UtteranceResult:
    """Where one utterance landed."""

    utterance_id: str
    outcome: Outcome
    expected: Expected
    expected_match: bool
    revision_count: int | None
    detail: str = ""


@dataclass
class BenchRow:
    """One benchmark run: one (backend, model) against one corpus."""

    row_id: str
    recorded_at: str
    backend: str
    model_id: str
    corpus_id: str
    profile: str
    n: int
    counts: dict[str, int]
    expected_match_rate: float
    revision_attempts_mean: float | None
    notes: str = ""
    results: list[UtteranceResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------


def load_corpus(path: Path) -> BenchCorpus:
    """Load an utterance corpus from YAML.

    Accepts both the bench shape (`expected: accept|refuse`) and the RFC-0021
    conformance-fixture shape (`expected_kind: positive|report_failure`).

    Raises:
        BenchCorpusError: The file is missing, unparseable, or malformed.
    """
    if not path.is_file():
        raise BenchCorpusError(f"corpus file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BenchCorpusError(f"corpus is not valid YAML: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BenchCorpusError(f"corpus must be a YAML mapping: {path}")
    rows = data.get("utterances")
    if not isinstance(rows, list) or not rows:
        raise BenchCorpusError(f"corpus has no `utterances` list: {path}")

    utterances: list[BenchUtterance] = []
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise BenchCorpusError(f"utterance #{i} is not a mapping: {path}")
        uid = row.get("id")
        text = row.get("text")
        raw_expected = row.get("expected", row.get("expected_kind"))
        if not isinstance(uid, str) or not uid:
            raise BenchCorpusError(f"utterance #{i} is missing `id`: {path}")
        if uid in seen:
            raise BenchCorpusError(f"duplicate utterance id {uid!r}: {path}")
        seen.add(uid)
        if not isinstance(text, str) or not text.strip():
            raise BenchCorpusError(f"utterance {uid!r} is missing `text`: {path}")
        if not isinstance(raw_expected, str) or raw_expected not in _EXPECTED_ALIASES:
            raise BenchCorpusError(
                f"utterance {uid!r} needs `expected: accept|refuse` "
                f"(or legacy `expected_kind: positive|report_failure`): {path}"
            )
        utterances.append(
            BenchUtterance(id=uid, text=text, expected=_EXPECTED_ALIASES[raw_expected])
        )

    return BenchCorpus(
        corpus_id=str(data.get("corpus_id") or path.stem),
        profile=str(data.get("profile") or ""),
        language=str(data.get("language") or "en"),
        utterances=tuple(utterances),
    )


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _is_report_only(program: dict[str, Any]) -> bool:
    """True iff the ROOT behavior consists solely of `report` steps and at
    least one of them carries `status: failure`.

    This is the bench's honest-refusal shape: the prompt contract tells a
    model whose request exceeds the manifest to emit exactly that. A program
    that does real work before reporting failure is not a refusal.
    """
    behavior = program.get("behavior")
    if not isinstance(behavior, dict):
        return False
    steps = behavior.get("steps")
    if not isinstance(steps, list) or not steps:
        return False
    saw_failure = False
    for step in steps:
        if not isinstance(step, dict) or set(step.keys()) != {"report"}:
            return False
        report = step["report"]
        if isinstance(report, dict) and report.get("status") == "failure":
            saw_failure = True
    return saw_failure


def classify(bridge: Bridge, utterance: BenchUtterance) -> UtteranceResult:
    """Translate one utterance and classify where it landed.

    Never raises for a per-utterance failure: provider errors, exhausted
    revisions and policy blocks all become outcomes, so one bad row cannot
    abort a benchmark run.
    """
    try:
        result = bridge.translate(utterance.text)
    except BridgePolicyViolation as exc:
        outcome: Outcome = "policy_block"
        return _mk_result(utterance, outcome, None, f"after {exc.attempts} attempt(s)")
    except BridgeRevisionExhausted as exc:
        return _mk_result(
            utterance, "invalid_emission", None, f"all {exc.attempts} attempt(s) rejected"
        )
    except ProviderError as exc:
        return _mk_result(utterance, "provider_error", None, str(exc))

    program = result.program or {}
    if _is_report_only(program):
        return _mk_result(utterance, "honest_refusal", result.revision_count, "")
    return _mk_result(utterance, "accepted", result.revision_count, "")


def _mk_result(
    utterance: BenchUtterance,
    outcome: Outcome,
    revision_count: int | None,
    detail: str,
) -> UtteranceResult:
    matched = (utterance.expected == "accept" and outcome == "accepted") or (
        utterance.expected == "refuse" and outcome == "honest_refusal"
    )
    return UtteranceResult(
        utterance_id=utterance.id,
        outcome=outcome,
        expected=utterance.expected,
        expected_match=matched,
        revision_count=revision_count,
        detail=detail,
    )


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------


def run_bench(
    *,
    bridge: Bridge,
    corpus: BenchCorpus,
    backend: str,
    model_id: str,
    recorded_at: str | None = None,
    tag: str = "",
    notes: str = "",
) -> BenchRow:
    """Run every corpus utterance through the bridge and aggregate a row."""
    results = [classify(bridge, u) for u in corpus.utterances]

    counts: dict[str, int] = {name: 0 for name in OUTCOMES}
    for r in results:
        counts[r.outcome] += 1

    matched = sum(1 for r in results if r.expected_match)
    revisions = [r.revision_count for r in results if r.revision_count is not None]

    recorded = recorded_at or date.today().isoformat()
    row_id = _slug(f"{recorded}-{backend}-{model_id}-{corpus.corpus_id}")
    if tag:
        row_id = f"{row_id}-{_slug(tag)}"

    return BenchRow(
        row_id=row_id,
        recorded_at=recorded,
        backend=backend,
        model_id=model_id,
        corpus_id=corpus.corpus_id,
        profile=corpus.profile,
        n=len(results),
        counts=counts,
        expected_match_rate=matched / len(results) if results else 0.0,
        revision_attempts_mean=(sum(revisions) / len(revisions)) if revisions else None,
        notes=notes,
        results=results,
    )


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", text).strip("-").lower()


# ---------------------------------------------------------------------------
# Row persistence
# ---------------------------------------------------------------------------


def row_to_dict(row: BenchRow) -> dict[str, Any]:
    """The machine YAML shape of one row."""
    return {
        "row_id": row.row_id,
        "recorded_at": row.recorded_at,
        "backend": row.backend,
        "model_id": row.model_id,
        "corpus_id": row.corpus_id,
        "profile": row.profile,
        "n": row.n,
        "counts": dict(row.counts),
        "expected_match_rate": round(row.expected_match_rate, 4),
        "revision_attempts_mean": (
            round(row.revision_attempts_mean, 4)
            if row.revision_attempts_mean is not None
            else None
        ),
        "notes": row.notes,
        "results": [
            {
                "utterance_id": r.utterance_id,
                "outcome": r.outcome,
                "expected": r.expected,
                "expected_match": r.expected_match,
                "revision_count": r.revision_count,
                "detail": r.detail,
            }
            for r in row.results
        ],
    }


def write_row(row: BenchRow, path: Path) -> None:
    """Write a row's YAML to `path`, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(row_to_dict(row), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )


def load_rows(directory: Path) -> list[BenchRow]:
    """Load every `*.yaml` row in a results directory (sorted by file name).

    Raises:
        BenchCorpusError: The directory is missing or a row file is malformed.
    """
    if not directory.is_dir():
        raise BenchCorpusError(f"results directory not found: {directory}")
    rows: list[BenchRow] = []
    for path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "counts" not in data:
            raise BenchCorpusError(f"not a bench row file: {path}")
        counts: dict[str, int] = {name: int(data["counts"].get(name, 0)) for name in OUTCOMES}
        rows.append(
            BenchRow(
                row_id=str(data.get("row_id") or path.stem),
                recorded_at=str(data.get("recorded_at") or ""),
                backend=str(data.get("backend") or ""),
                model_id=str(data.get("model_id") or ""),
                corpus_id=str(data.get("corpus_id") or ""),
                profile=str(data.get("profile") or ""),
                n=int(data.get("n") or sum(counts.values())),
                counts=counts,
                expected_match_rate=float(data.get("expected_match_rate") or 0.0),
                revision_attempts_mean=(
                    float(data["revision_attempts_mean"])
                    if data.get("revision_attempts_mean") is not None
                    else None
                ),
                notes=str(data.get("notes") or ""),
            )
        )
    if not rows:
        raise BenchCorpusError(f"no bench row files (*.yaml) in {directory}")
    return rows


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

_TABLE_HEADER = (
    "| Model | Backend | Corpus | n | Accepted | Honest refusal | Invalid | "
    "Provider error | Policy block | Expected match | Mean revisions |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def render_table(rows: Iterable[BenchRow]) -> str:
    """A public markdown comparison table, one line per row."""
    out = _TABLE_HEADER
    for row in rows:
        n = row.n or 1
        cells = " | ".join(
            f"{row.counts[name]} ({row.counts[name] / n:.0%})" for name in OUTCOMES
        )
        mean = (
            f"{row.revision_attempts_mean:.2f}"
            if row.revision_attempts_mean is not None
            else "n/a"
        )
        out += (
            f"| {row.model_id} | {row.backend} | {row.corpus_id} | {row.n} "
            f"| {cells} | {row.expected_match_rate:.0%} | {mean} |\n"
        )
    return out


def render_row(row: BenchRow) -> str:
    """The single-run report printed after a bench run."""
    lines = [
        f"bench: {row.model_id} via {row.backend} on corpus {row.corpus_id} "
        f"(n={row.n}, recorded {row.recorded_at})",
        "",
    ]
    for r in row.results:
        flag = "match" if r.expected_match else f"expected {r.expected}"
        detail = f"  [{r.detail}]" if r.detail else ""
        lines.append(f"  {r.utterance_id:24s} {r.outcome:16s} ({flag}){detail}")
    lines.append("")
    lines.append(render_table([row]).rstrip())
    return "\n".join(lines) + "\n"
