"""Dataset records and JSONL persistence (RFC-0666).

The record schema here is the normative surface of RFC-0666: a dataset is
a JSONL file, one `DatasetRecord` per line. Records with a rejected
`validator_verdict` are permitted only for `rejection_repair` provenance,
where the rejected program plus the validator's error codes are the
training signal and `repair` carries the accepted target.

Everything else in the pipeline (mining, back-translation, synthesis,
export) produces or consumes this shape.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Provenance = Literal[
    "few_shot",
    "fixture_backtranslation",
    "llm_backtranslation",
    "rejection_repair",
]


class ValidatorVerdict(BaseModel):
    """The validator's verdict for a record's program, measured at synthesis time."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    error_codes: list[str] = Field(default_factory=list)


class DatasetRecord(BaseModel):
    """One (natural language, program, manifest) training example."""

    model_config = ConfigDict(extra="forbid")

    nl: str
    program: dict[str, Any]
    manifest_ref: str
    profile: str
    language: str = "en"
    provenance: Provenance
    validator_verdict: ValidatorVerdict
    envelope_ref: str | None = None
    repair: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _rejected_only_for_repair(self) -> DatasetRecord:
        if not self.validator_verdict.accepted:
            if self.provenance != "rejection_repair":
                raise ValueError(
                    "a rejected program is only allowed with provenance "
                    "'rejection_repair'; every other record must be validator-accepted"
                )
            if self.repair is None:
                raise ValueError("a rejection_repair record must carry the accepted program in `repair`")
        return self

    def dedup_key(self) -> tuple[str, str]:
        """Stable identity for deduplication: the utterance plus the canonical program JSON."""
        return self.nl, json.dumps(self.program, sort_keys=True, separators=(",", ":"))


class Dataset(BaseModel):
    """An ordered collection of records with JSONL persistence."""

    model_config = ConfigDict(extra="forbid")

    records: list[DatasetRecord] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[DatasetRecord]:  # type: ignore[override]
        return iter(self.records)

    def extend(self, records: Iterable[DatasetRecord]) -> None:
        self.records.extend(records)

    def accepted(self) -> list[DatasetRecord]:
        """Records whose program the validator accepted."""
        return [r for r in self.records if r.validator_verdict.accepted]

    def repairs(self) -> list[DatasetRecord]:
        """The rejection_repair records (rejected program + accepted target)."""
        return [r for r in self.records if r.provenance == "rejection_repair"]

    def write_jsonl(self, path: Path) -> int:
        """Write one record per line; returns the record count."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            for record in self.records:
                fh.write(json.dumps(record.model_dump(exclude_none=True), sort_keys=True))
                fh.write("\n")
        return len(self.records)

    @classmethod
    def read_jsonl(cls, path: Path) -> Dataset:
        """Parse a JSONL file back into a Dataset, validating every line."""
        records: list[DatasetRecord] = []
        with path.open(encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_no}: not valid JSON: {exc}") from exc
                records.append(DatasetRecord.model_validate(payload))
        return cls(records=records)
