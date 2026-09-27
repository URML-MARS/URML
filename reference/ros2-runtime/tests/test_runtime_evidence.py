"""The runtime records its own refusals in the evidence log.

`URMLRuntime.execute` re-validates before its first adapter call (defense in
depth). With ``evidence_log`` set, a refusal at that check is appended as one
validation record before ``ValidationRejectedError`` is raised, and the
adapter still receives nothing. Accepted programs are left to the entry point
that validated first. Hermetic: ``MockROSAdapter``, no ROS 2.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import pytest
import yaml
from urml_validator.evidence import content_digest, read_records, reverify

from urml_ros2_runtime import MockROSAdapter, URMLRuntime, ValidationRejectedError

REPO_ROOT = Path(__file__).resolve().parents[3]
HOME = REPO_ROOT / "examples" / "home"


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


MANIFEST = _load(HOME / "red-mug.manifest.yaml")
ENVELOPE = _load(HOME / "red-mug.envelope.yaml")
SAFE = _load(HOME / "red-mug.urml.yaml")
GRASP_4N = _load(HOME / "red-mug.grasp-4n.urml.yaml")
AS_OF = datetime.date(2026, 9, 27)


def test_a_revalidation_refusal_is_recorded_and_nothing_moves(tmp_path: Path) -> None:
    log = tmp_path / "evidence.jsonl"
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError):
        URMLRuntime(adapter, evidence_log=log).execute(
            GRASP_4N, MANIFEST, ENVELOPE, ("home",), policy=None, as_of=AS_OF
        )
    assert adapter.call_log == []
    (record,) = read_records(log)
    assert (record.surface, record.stage, record.verdict) == ("runtime", "revalidation", "refused")
    assert record.codes == ["envelope.force_exceeded"]
    assert record.program == GRASP_4N
    assert record.manifest_digest == content_digest(MANIFEST)
    assert record.envelope_digest == content_digest(ENVELOPE)
    assert (record.policy, record.profiles, record.as_of) == ("none", ["home"], "2026-09-27")
    check = reverify(record, manifest=MANIFEST, envelope=ENVELOPE, policy=None)
    assert check.reproduced, check.problems


def test_an_accepted_program_is_not_recorded_by_the_runtime(tmp_path: Path) -> None:
    log = tmp_path / "evidence.jsonl"
    result = URMLRuntime(MockROSAdapter(), evidence_log=str(log)).execute(
        SAFE, MANIFEST, ENVELOPE, ("home",), policy=None
    )
    assert result.success
    assert not log.exists()


def test_no_log_means_no_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValidationRejectedError):
        URMLRuntime(MockROSAdapter()).execute(GRASP_4N, MANIFEST, ENVELOPE, ("home",), policy=None)
    assert list(tmp_path.iterdir()) == []


def test_a_log_that_cannot_be_written_does_not_weaken_the_refusal(tmp_path: Path) -> None:
    """The refusal is raised as before; its note says the record was not written."""
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError) as excinfo:
        URMLRuntime(adapter, evidence_log=tmp_path).execute(
            GRASP_4N, MANIFEST, ENVELOPE, ("home",), policy=None
        )
    assert adapter.call_log == []
    assert any("was not written" in note for note in getattr(excinfo.value, "__notes__", []))
