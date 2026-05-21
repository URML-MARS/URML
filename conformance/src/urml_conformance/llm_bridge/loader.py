"""LLM-bridge conformance fixture loader.

Reads utterance sets and measurement rows from the on-disk layout
described in
[`conformance/llm-bridge/README.md`](../../../../llm-bridge/README.md).
No dependency on the bridge, the validator, or any LLM backend; this
module parses YAML and returns dataclasses, so lightweight tools (docs
site renderers, badge generation) can pull the published table without
pulling pydantic or httpx.

The actual scoring runner (which calls a real ``LLMProvider``, runs the
bridge, and aggregates pass rates) is a separate component scheduled for a
follow-up commit. The loader and the row schema land first so external
tooling can rely on a stable on-disk contract from day one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

__all__ = [
    "ConformanceLoaderError",
    "ExpectedKind",
    "ResultRow",
    "Utterance",
    "UtteranceSet",
    "load_results_for_date",
    "load_utterances",
]

#: One of the two expected outcomes per utterance.
ExpectedKind = Literal["positive", "report_failure"]


class ConformanceLoaderError(ValueError):
    """Raised when a fixture or result file doesn't conform to the schema."""


@dataclass(frozen=True)
class Utterance:
    """A single utterance the LLM bridge is asked to translate."""

    id: str
    text: str
    expected_kind: ExpectedKind


@dataclass(frozen=True)
class UtteranceSet:
    """A profile's utterance fixture for one language."""

    profile: str
    language: str
    manifest: str
    utterances: tuple[Utterance, ...]


@dataclass(frozen=True)
class ResultRow:
    """One ``(model, backend, profile)`` measurement."""

    row_id: str
    recorded_at: str
    model_id: str
    model_size_b: float
    backend: str
    profile: str
    n_utterances: int
    structural_pass_rate: float
    semantic_pass_rate: float
    revision_attempts_mean: float
    hardware_class: str
    notes: str = ""


def load_utterances(
    fixtures_root: Path, *, profile: str, language: str = "en"
) -> UtteranceSet:
    """Load ``fixtures_root/<profile>/utterances-<language>.yaml``."""
    path = fixtures_root / profile / f"utterances-{language}.yaml"
    if not path.is_file():
        raise ConformanceLoaderError(f"no utterance fixture at {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConformanceLoaderError(f"{path}: top-level is not a mapping")
    try:
        utterances = tuple(
            Utterance(
                id=str(u["id"]),
                text=str(u["text"]),
                expected_kind=_validate_expected_kind(u["expected_kind"], path),
            )
            for u in raw["utterances"]
        )
        return UtteranceSet(
            profile=str(raw["profile"]),
            language=str(raw["language"]),
            manifest=str(raw["manifest"]),
            utterances=utterances,
        )
    except (KeyError, TypeError) as exc:
        raise ConformanceLoaderError(f"{path}: missing or malformed field: {exc}") from exc


def load_results_for_date(results_root: Path, *, date: str) -> list[ResultRow]:
    """Load every row YAML under ``results_root/<date>/`` (alphabetical)."""
    day = results_root / date
    if not day.is_dir():
        return []
    rows: list[ResultRow] = []
    for row_path in sorted(day.glob("*.yaml")):
        rows.append(_load_row(row_path))
    return rows


def _load_row(path: Path) -> ResultRow:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConformanceLoaderError(f"{path}: top-level is not a mapping")
    try:
        return ResultRow(
            row_id=str(raw["row_id"]),
            recorded_at=str(raw["recorded_at"]),
            model_id=str(raw["model_id"]),
            model_size_b=float(raw["model_size_b"]),
            backend=str(raw["backend"]),
            profile=str(raw["profile"]),
            n_utterances=int(raw["n_utterances"]),
            structural_pass_rate=float(raw["structural_pass_rate"]),
            semantic_pass_rate=float(raw["semantic_pass_rate"]),
            revision_attempts_mean=float(raw["revision_attempts_mean"]),
            hardware_class=str(raw["hardware_class"]),
            notes=str(raw.get("notes", "")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConformanceLoaderError(f"{path}: missing or malformed field: {exc}") from exc


def _validate_expected_kind(value: object, source: Path) -> ExpectedKind:
    if value == "positive":
        return "positive"
    if value == "report_failure":
        return "report_failure"
    raise ConformanceLoaderError(
        f"{source}: expected_kind must be 'positive' or 'report_failure', got {value!r}"
    )
