"""Validation records: build, append, read back, and re-verify.

The evidence log is how a refusal becomes evidence: what the gate was asked,
which declared limit the program broke, and which validator said no. These
tests hold the record format still, prove the digests are content digests
(formatting does not change them), and prove a recorded verdict can be
replayed against the inputs it judged and against nothing else.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_validator import __version__, validate
from urml_validator.evidence import (
    RECORD_FORMAT,
    append_record,
    build_record,
    canonical_json,
    content_digest,
    read_records,
    reverify,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
HOME = REPO_ROOT / "examples" / "home"


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


MANIFEST = _load(HOME / "red-mug.manifest.yaml")
ENVELOPE = _load(HOME / "red-mug.envelope.yaml")
SAFE = _load(HOME / "red-mug.urml.yaml")

# 4 N is inside the gripper's 5 N range and above the envelope's 3 N cap, so
# only the envelope refuses it.
GRASP_4N: dict[str, Any] = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"detect": {"object": "mug", "store_as": "target"}},
            {"grasp": {"target": "$target", "force": 4.0}},
        ],
    },
}


def _refused_record(recorded_at: str = "2026-09-27T08:00:00Z") -> Any:
    result = validate(GRASP_4N, MANIFEST, ENVELOPE, profiles=("home",), policy=None)
    assert not result.accepted
    return build_record(
        surface="validate",
        stage="validation",
        result=result,
        program=GRASP_4N,
        manifest=MANIFEST,
        envelope=ENVELOPE,
        policy=None,
        profiles=("home",),
        recorded_at=recorded_at,
    )


def test_content_digest_ignores_key_order_and_formatting() -> None:
    reordered = json.loads(json.dumps(MANIFEST))
    reordered = dict(reversed(list(reordered.items())))
    assert content_digest(MANIFEST) == content_digest(reordered)
    assert content_digest(MANIFEST).startswith("sha256:")
    assert content_digest(MANIFEST) != content_digest(ENVELOPE)


def test_canonical_json_is_sorted_and_compact() -> None:
    assert canonical_json({"b": 1, "a": [1, 2]}) == '{"a":[1,2],"b":1}'


def test_a_refusal_records_the_limit_it_broke() -> None:
    record = _refused_record()
    assert record.format == RECORD_FORMAT
    assert record.verdict == "refused"
    assert record.codes == ["envelope.force_exceeded"]
    assert record.robot_id == MANIFEST["robot_id"]
    assert record.program == GRASP_4N
    assert record.program_digest == content_digest(GRASP_4N)
    assert record.manifest_digest == content_digest(MANIFEST)
    assert record.envelope_digest == content_digest(ENVELOPE)
    assert record.policy == "none"
    assert record.tool.version == __version__
    assert record.result["accepted"] is False
    assert record.surface == "validate" and record.stage == "validation"


def test_an_acceptance_is_recorded_too() -> None:
    result = validate(SAFE, MANIFEST, ENVELOPE, profiles=("home",), policy=None)
    assert result.accepted
    record = build_record(
        surface="api",
        stage="validation",
        result=result,
        program=SAFE,
        manifest=MANIFEST,
        envelope=ENVELOPE,
        policy=None,
        profiles=("home",),
    )
    assert record.verdict == "accepted"
    assert record.codes == []
    assert record.recorded_at.endswith("Z")


def test_record_id_is_the_verdict_not_the_moment() -> None:
    first = _refused_record("2026-09-27T08:00:00Z")
    second = _refused_record("2026-09-28T09:30:00Z")
    assert first.recorded_at != second.recorded_at
    assert first.record_id == second.record_id


def test_policy_labels() -> None:
    result = validate(SAFE, MANIFEST, ENVELOPE, profiles=("home",))
    common: dict[str, Any] = {
        "surface": "api",
        "stage": "validation",
        "result": result,
        "program": SAFE,
        "manifest": MANIFEST,
    }
    assert build_record(**common, policy="DEFAULT").policy == "default"
    assert build_record(**common, policy=None).policy == "none"
    custom = {"policy_version": "0.1", "policy_id": "site", "rules": []}
    assert build_record(**common, policy=custom).policy == content_digest(custom)


def test_records_hold_no_identifiers() -> None:
    fields = set(_refused_record().model_dump())
    assert fields == {
        "format", "record_id", "recorded_at", "tool", "surface", "stage", "verdict",
        "robot_id", "program", "program_digest", "manifest_digest", "envelope_digest",
        "policy", "rulebooks", "default_rulebooks", "as_of", "profiles", "codes",
        "warning_codes", "result", "request", "attempts", "attempt_codes",
    }


def test_append_and_read_back(tmp_path: Path) -> None:
    log = tmp_path / "nested" / "evidence.jsonl"
    refused = _refused_record()
    append_record(log, refused)
    append_record(log, refused)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0] == canonical_json(refused.model_dump(mode="json"))
    assert read_records(log) == [refused, refused]


def test_read_names_the_bad_line(tmp_path: Path) -> None:
    log = tmp_path / "evidence.jsonl"
    append_record(log, _refused_record())
    with log.open("a", encoding="utf-8") as handle:
        handle.write('{"format": "something-else/9"}\n')
    with pytest.raises(ValueError, match=r"evidence\.jsonl:2:"):
        read_records(log)


def test_reverify_replays_the_verdict() -> None:
    check = reverify(_refused_record(), manifest=MANIFEST, envelope=ENVELOPE, policy=None)
    assert check.reproduced, check.problems


def test_reverify_refuses_other_inputs() -> None:
    looser = dict(ENVELOPE, max_grip_force_n=10.0)
    check = reverify(_refused_record(), manifest=MANIFEST, envelope=looser, policy=None)
    assert not check.reproduced
    assert any("envelope" in problem for problem in check.problems)


def test_reverify_catches_a_changed_verdict() -> None:
    record = _refused_record()
    tampered = record.model_copy(update={"codes": ["envelope.velocity_exceeded"]})
    check = reverify(tampered, manifest=MANIFEST, envelope=ENVELOPE, policy=None)
    assert not check.reproduced
    assert any(problem.startswith("codes:") for problem in check.problems)


def test_reverify_needs_a_program() -> None:
    record = _refused_record().model_copy(update={"program": None, "program_digest": None})
    check = reverify(record, manifest=MANIFEST, envelope=ENVELOPE, policy=None)
    assert not check.reproduced
    assert check.problems == ["the record has no program to replay"]
