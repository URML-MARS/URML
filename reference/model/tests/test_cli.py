"""CLI: synthesize -> export round trip, and a hermetic echo-backed eval."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from urml_model.cli import main
from urml_model.dataset import Dataset

_VALID_HOME_PROGRAM = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "kitchen"}}]},
}


def test_synthesize_then_export(tmp_path: Path, capsys) -> None:
    data = tmp_path / "data.jsonl"
    assert main(["synthesize", "--out", str(data), "--profile", "home", "--no-fixtures"]) == 0
    dataset = Dataset.read_jsonl(data)
    assert len(dataset) > 0
    assert all(r.validator_verdict.accepted for r in dataset)

    sft = tmp_path / "sft.jsonl"
    assert main(["export", "--in", str(data), "--out", str(sft), "--fmt", "completions"]) == 0
    assert len(sft.read_text(encoding="utf-8").splitlines()) == len(dataset)
    out = capsys.readouterr().out
    assert "wrote" in out


def test_synthesize_fixture_path(tmp_path: Path) -> None:
    data = tmp_path / "drone.jsonl"
    assert main(["synthesize", "--out", str(data), "--profile", "drone", "--no-few-shots"]) == 0
    dataset = Dataset.read_jsonl(data)
    assert len(dataset) > 0
    assert {r.profile for r in dataset} == {"drone"}


def test_eval_with_echo_backend(tmp_path: Path, capsys) -> None:
    utterance = "Go to the kitchen."
    fixtures_root = tmp_path / "fixtures"
    (fixtures_root / "home").mkdir(parents=True)
    (fixtures_root / "home" / "utterances-en.yaml").write_text(
        yaml.safe_dump(
            {
                "profile": "home",
                "language": "en",
                "manifest": "turtlebot4_home",
                "utterances": [{"id": "kitchen-01", "text": utterance, "expected_kind": "positive"}],
            }
        ),
        encoding="utf-8",
    )
    responses = tmp_path / "responses.json"
    responses.write_text(json.dumps({utterance: json.dumps(_VALID_HOME_PROGRAM)}), encoding="utf-8")

    out = tmp_path / "row.yaml"
    code = main(
        [
            "eval",
            "--utterances-root",
            str(fixtures_root),
            "--profile",
            "home",
            "--backend",
            "echo",
            "--model",
            "echo-double",
            "--recorded-at",
            "2026-07-12T00:00:00+00:00",
            "--echo-responses",
            str(responses),
            "--out",
            str(out),
        ]
    )
    assert code == 0
    row = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert row["structural_pass_rate"] == 1.0
    assert row["semantic_pass_rate"] == 1.0
    assert row["revision_attempts_mean"] == 0.0
    assert "structural 1.0" in capsys.readouterr().out
