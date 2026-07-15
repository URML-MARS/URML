"""Export formats: chatml uses the bridge's real system prompt; dpo pairs repairs."""

from __future__ import annotations

import json
from pathlib import Path

from urml_model.dataset import Dataset, DatasetRecord, ValidatorVerdict
from urml_model.export import export_dpo, export_sft
from urml_model.mining import mine_few_shot_pairs
from urml_model.synthesize import synthesize

_ACCEPTED = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "kitchen"}}]},
}
_REJECTED = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"take_off": {"altitude": 30.0}}]},
}


def _home_dataset() -> Dataset:
    dataset, _report = synthesize(mine_few_shot_pairs(profiles=("home",)))
    return dataset


def test_chatml_export_uses_bridge_prompt(tmp_path: Path) -> None:
    dataset = _home_dataset()
    out = tmp_path / "sft.jsonl"
    count = export_sft(dataset, out, fmt="chatml")
    assert count == len(dataset)
    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    for line, record in zip(lines, dataset.records, strict=True):
        system, user, assistant = line["messages"]
        assert system["role"] == "system"
        # The bridge prompt embeds the program schema and the manifest summary.
        assert "URML" in system["content"]
        assert user == {"role": "user", "content": record.nl}
        assert json.loads(assistant["content"]) == record.program


def test_completions_export_is_bare_pairs(tmp_path: Path) -> None:
    dataset = _home_dataset()
    out = tmp_path / "completions.jsonl"
    count = export_sft(dataset, out, fmt="completions")
    assert count == len(dataset)
    first = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert set(first) == {"prompt", "completion"}
    assert json.loads(first["completion"])["profile"] == "home"


def test_dpo_export_pairs_rejected_with_repair(tmp_path: Path) -> None:
    repair_record = DatasetRecord(
        nl="Go to the kitchen.",
        program=_REJECTED,
        manifest_ref="turtlebot4_home",
        profile="home",
        provenance="rejection_repair",
        validator_verdict=ValidatorVerdict(accepted=False, error_codes=["capability.primitive_not_supported"]),
        repair=_ACCEPTED,
    )
    dataset = Dataset(records=[repair_record])
    out = tmp_path / "dpo.jsonl"
    assert export_dpo(dataset, out) == 1
    row = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert json.loads(row["chosen"]) == _ACCEPTED
    assert json.loads(row["rejected"]) == _REJECTED
    assert row["rejected_error_codes"] == ["capability.primitive_not_supported"]
    assert row["prompt"] == "Go to the kitchen."


def test_sft_export_excludes_repair_records(tmp_path: Path) -> None:
    dataset = _home_dataset()
    dataset.records.append(
        DatasetRecord(
            nl="Go to the kitchen.",
            program=_REJECTED,
            manifest_ref="turtlebot4_home",
            profile="home",
            provenance="rejection_repair",
            validator_verdict=ValidatorVerdict(accepted=False, error_codes=["capability.x"]),
            repair=_ACCEPTED,
        )
    )
    out = tmp_path / "sft.jsonl"
    assert export_sft(dataset, out, fmt="completions") == len(dataset) - 1
