"""Rejection mining: failed bridge attempts become repair records."""

from __future__ import annotations

import json

from urml_model.mining import resolve_manifest_ref
from urml_model.rejections import RejectionSession, mine_rejections

_ACCEPTED = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "kitchen"}}]},
}

# A ground robot cannot take off; the validator rejects this with capability codes.
_REJECTED = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"take_off": {"altitude": 30.0}}]},
}


def _manifest() -> dict:
    return resolve_manifest_ref("turtlebot4_home")


def test_mine_rejections_produces_repair_records() -> None:
    session = RejectionSession(
        nl="Go to the kitchen.",
        raw_completions=(json.dumps(_REJECTED), "{ not json at all"),
        accepted_program=_ACCEPTED,
    )
    records = mine_rejections([session], manifest=_manifest(), manifest_ref="turtlebot4_home", profile="home")
    assert len(records) == 1, "the unparseable attempt is skipped, the invalid program is kept"
    record = records[0]
    assert record.provenance == "rejection_repair"
    assert not record.validator_verdict.accepted
    assert record.validator_verdict.error_codes
    assert record.repair == _ACCEPTED
    assert record.program == _REJECTED


def test_sessions_without_accepted_program_are_skipped() -> None:
    session = RejectionSession(
        nl="Go to the kitchen.",
        raw_completions=(json.dumps(_REJECTED),),
        accepted_program=None,
    )
    assert mine_rejections([session], manifest=_manifest(), manifest_ref="turtlebot4_home", profile="home") == []


def test_attempts_that_now_validate_are_not_repairs() -> None:
    session = RejectionSession(
        nl="Go to the kitchen.",
        raw_completions=(json.dumps(_ACCEPTED),),
        accepted_program=_ACCEPTED,
    )
    assert mine_rejections([session], manifest=_manifest(), manifest_ref="turtlebot4_home", profile="home") == []
