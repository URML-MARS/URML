"""RFC-0286 — NL -> fleet bridge tests.

Covers the fleet few-shot library (every example validates against a reference
roster) and the FleetBridge round-trip + revision loop via EchoProvider.
"""

from __future__ import annotations

import copy
import json

import pytest
from urml_validator import validate_fleet

from urml_llm_bridge import EchoProvider, FleetBridge, fleet_few_shots

# Reference two-member roster the fleet few-shots target. Distinct location names
# per member (gate/lead_home vs start/follow_home) keep the name-based cross-robot
# collision check happy.
LEAD = {
    "robot_id": "lead",
    "frames": [{"name": "map"}],
    "declared_locations": [
        {"name": "gate", "pose": {"x": 1.0, "y": 0.0}, "frame": "map"},
        {"name": "lead_home", "pose": {"x": 0.0, "y": 0.0}, "frame": "map"},
    ],
    "mobility": {"drive_type": "differential", "max_velocity": 1.0},
    "connectivity": {"links": [{"role": "peer_link"}]},
}
FOLLOW = {
    "robot_id": "follow",
    "frames": [{"name": "map"}],
    "declared_locations": [
        {"name": "start", "pose": {"x": 2.0, "y": 0.0}, "frame": "map"},
        {"name": "follow_home", "pose": {"x": 3.0, "y": 0.0}, "frame": "map"},
    ],
    "mobility": {"drive_type": "differential", "max_velocity": 1.0},
    "connectivity": {"links": [{"role": "peer_link"}]},
}
ROSTER = {
    "roster_version": "0.1",
    "members": [{"name": "lead", "manifest": "lead"}, {"name": "follow", "manifest": "follow"}],
}
MEMBERS = {"lead": LEAD, "follow": FOLLOW}


@pytest.mark.parametrize("example", fleet_few_shots(), ids=lambda e: e.user[:32])
def test_fleet_few_shots_validate(example):
    """Every shipped fleet few-shot validates against the reference roster."""
    result = validate_fleet(ROSTER, MEMBERS, example.program, policy=None)
    assert result.accepted, result.codes()


def test_fleet_bridge_round_trip():
    program = fleet_few_shots()[0].program
    provider = EchoProvider(scripted=[json.dumps(program)])
    bridge = FleetBridge(
        provider=provider,
        roster=ROSTER,
        member_manifests=MEMBERS,
        profiles=("fleet",),
        policy=None,
    )
    result = bridge.translate("Move both robots to their starts at the same time, then sync.")
    assert result.accepted
    assert result.revision_count == 0
    assert result.program == program


def test_fleet_bridge_revises_after_bad_emission():
    good = fleet_few_shots()[0].program
    # First emission addresses an undeclared member -> fleet.undeclared_member
    # (a non-policy error) -> the loop revises.
    bad = {
        "profile": "home",
        "behavior": {"type": "on", "member": "ghost", "body": {"move_to": {"location": "gate"}}},
    }
    provider = EchoProvider(scripted=[json.dumps(bad), json.dumps(good)])
    bridge = FleetBridge(
        provider=provider, roster=ROSTER, member_manifests=MEMBERS, policy=None
    )
    result = bridge.translate("Move both robots to their starts, then sync.")
    assert result.accepted
    assert result.revision_count == 1


def test_fleet_prompt_summarizes_every_member():
    from urml_llm_bridge import build_fleet_system_prompt
    from urml_validator import export_schema

    prompt = build_fleet_system_prompt(
        schema=export_schema("program"),
        roster=ROSTER,
        member_manifests=MEMBERS,
        profiles=("fleet",),
        few_shots=fleet_few_shots(),
    )
    # The roster and both member handles are in the prompt, plus the fleet rules.
    assert "Fleet roster" in prompt
    assert "`lead`" in prompt and "`follow`" in prompt
    assert "barrier" in prompt and '"type": "on"' in prompt


def test_fleet_bridge_does_not_mutate_inputs():
    program = copy.deepcopy(fleet_few_shots()[1].program)
    provider = EchoProvider(scripted=[json.dumps(program)])
    members_before = copy.deepcopy(MEMBERS)
    bridge = FleetBridge(provider=provider, roster=ROSTER, member_manifests=MEMBERS, policy=None)
    bridge.translate("Send the lead to the gate, then send both home.")
    assert MEMBERS == members_before
