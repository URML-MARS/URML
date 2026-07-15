"""Dataset record schema + JSONL round-trip (RFC-0666 normative surface)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from urml_model.dataset import Dataset, DatasetRecord, ValidatorVerdict

_PROGRAM = {"profile": "home", "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "kitchen"}}]}}


def _accepted_record(nl: str = "Go to the kitchen.") -> DatasetRecord:
    return DatasetRecord(
        nl=nl,
        program=_PROGRAM,
        manifest_ref="turtlebot4_home",
        profile="home",
        provenance="fixture_backtranslation",
        validator_verdict=ValidatorVerdict(accepted=True),
    )


def test_jsonl_round_trip(tmp_path: Path) -> None:
    dataset = Dataset(records=[_accepted_record(), _accepted_record("Head to the kitchen.")])
    out = tmp_path / "data.jsonl"
    assert dataset.write_jsonl(out) == 2
    back = Dataset.read_jsonl(out)
    assert back.records == dataset.records


def test_rejected_record_requires_repair_provenance() -> None:
    with pytest.raises(ValidationError, match="rejection_repair"):
        DatasetRecord(
            nl="Go somewhere impossible.",
            program=_PROGRAM,
            manifest_ref="turtlebot4_home",
            profile="home",
            provenance="fixture_backtranslation",
            validator_verdict=ValidatorVerdict(accepted=False, error_codes=["capability.unknown_location"]),
        )


def test_rejected_repair_record_requires_repair_target() -> None:
    with pytest.raises(ValidationError, match="repair"):
        DatasetRecord(
            nl="Go somewhere impossible.",
            program=_PROGRAM,
            manifest_ref="turtlebot4_home",
            profile="home",
            provenance="rejection_repair",
            validator_verdict=ValidatorVerdict(accepted=False, error_codes=["capability.unknown_location"]),
        )


def test_repair_record_valid_with_target() -> None:
    record = DatasetRecord(
        nl="Go to the kitchen.",
        program={"profile": "home", "behavior": {"type": "sequence", "steps": []}},
        manifest_ref="turtlebot4_home",
        profile="home",
        provenance="rejection_repair",
        validator_verdict=ValidatorVerdict(accepted=False, error_codes=["argument.missing"]),
        repair=_PROGRAM,
    )
    assert record.repair == _PROGRAM


def test_dedup_key_is_canonical() -> None:
    a = _accepted_record()
    b = _accepted_record()
    assert a.dedup_key() == b.dedup_key()
    assert a.dedup_key() != _accepted_record("Head to the kitchen.").dedup_key()


def test_read_jsonl_rejects_bad_line(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"not": "a record"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        Dataset.read_jsonl(path)
