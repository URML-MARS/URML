"""RFC-0286 — FleetRuntime hermetic execution tests.

Runs the courier-to-arm handoff across two MockROSAdapters (one per member) and
asserts the per-member audit, defense-in-depth re-validation, and a fleet of one.
"""

from __future__ import annotations

import copy

import pytest
from urml_ros2_runtime import FleetRuntime, MockROSAdapter, ValidationRejectedError

COURIER_MANIFEST = {
    "robot_id": "courier",
    "frames": [{"name": "map"}],
    "declared_locations": [
        {"name": "handoff_dock", "pose": {"x": 1.0, "y": 1.0}, "frame": "map"},
        {"name": "staging", "pose": {"x": 0.0, "y": 0.0}, "frame": "map"},
    ],
    "mobility": {"drive_type": "differential", "max_velocity": 1.5},
    "connectivity": {"links": [{"role": "peer_link"}]},
}

ARM_MANIFEST = {
    "robot_id": "arm",
    "frames": [{"name": "cell"}],
    "declared_locations": [
        {"name": "handoff_dock", "pose": {"x": 1.0, "y": 1.0}, "frame": "cell"},
        {"name": "conveyor_a", "pose": {"x": 2.0, "y": 0.0}, "frame": "cell"},
    ],
    "mobility": {"drive_type": "manipulator_base", "max_velocity": 0.0},
    "manipulation": {
        "arm_count": 1,
        "grippers": [
            {"name": "g0", "kind": "servo_electric", "force_min_n": 1.0, "force_max_n": 50.0}
        ],
    },
    "perception": {"cameras": [{"name": "wrist_cam"}], "object_vocabulary": ["widget"]},
    "connectivity": {"links": [{"role": "peer_link"}]},
}

ROSTER = {
    "roster_version": "0.1",
    "members": [
        {"name": "courier", "manifest": "husky_amr"},
        {"name": "arm", "manifest": "kawasaki_rs"},
    ],
}

MEMBERS = {"courier": COURIER_MANIFEST, "arm": ARM_MANIFEST}

HANDOFF_PROGRAM = {
    "profile": "industrial",
    "behavior": {
        "type": "sequence",
        "steps": [
            {"type": "on", "member": "courier", "body": {"move_to": {"location": "handoff_dock"}}},
            {"type": "barrier", "members": ["courier", "arm"]},
            {
                "type": "parallel",
                "branches": [
                    {
                        "type": "on",
                        "member": "arm",
                        "body": {
                            "type": "sequence",
                            "steps": [
                                {
                                    "pick_from": {
                                        "source": "handoff_dock",
                                        "object": "widget",
                                        "store_as": "part",
                                    }
                                },
                                {"place_at": {"target": "conveyor_a", "held": "$part"}},
                            ],
                        },
                    },
                    {"type": "on", "member": "courier", "body": {"wait": {"duration": "2s"}}},
                ],
            },
            {"type": "barrier", "members": ["courier", "arm"]},
            {"type": "on", "member": "courier", "body": {"move_to": {"location": "staging"}}},
        ],
    },
}


def _fleet() -> FleetRuntime:
    return FleetRuntime({"courier": MockROSAdapter(), "arm": MockROSAdapter()})


def test_handoff_executes_hermetically():
    result = _fleet().execute(ROSTER, MEMBERS, HANDOFF_PROGRAM)
    assert result.success
    # Both members appear in the per-member audit.
    assert set(result.per_member_audit) == {"courier", "arm"}


def test_per_member_audit_is_dispatched_correctly():
    result = _fleet().execute(ROSTER, MEMBERS, HANDOFF_PROGRAM)
    courier_methods = [c.get("method") for c in result.per_member_audit["courier"]]
    arm_methods = [c.get("method") for c in result.per_member_audit["arm"]]
    # The courier navigates twice (to the dock, then to staging) and holds in
    # between; it never manipulates anything.
    assert courier_methods == ["send_navigation_goal", "wait_passively", "send_navigation_goal"]
    assert "send_manipulation_goal" not in courier_methods
    # The arm picks and places (manipulation), and never holds.
    assert arm_methods.count("send_manipulation_goal") == 2
    assert "wait_passively" not in arm_methods


def test_cross_member_binding_flows():
    result = _fleet().execute(ROSTER, MEMBERS, HANDOFF_PROGRAM)
    # $part is produced by the arm's pick_from and consumed by its place_at;
    # execution completes, proving the binding resolved at runtime.
    assert result.success
    assert "part" in result.bindings


def test_revalidation_rejects_bad_fleet_program():
    program = copy.deepcopy(HANDOFF_PROGRAM)
    program["behavior"]["steps"][0]["member"] = "ghost"  # undeclared member
    with pytest.raises(ValidationRejectedError):
        _fleet().execute(ROSTER, MEMBERS, program)


def test_fleet_of_one_executes():
    roster = {"roster_version": "0.1", "members": [{"name": "arm", "manifest": "kawasaki_rs"}]}
    program = {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"pick_from": {"source": "handoff_dock", "object": "widget", "store_as": "part"}},
                {"place_at": {"target": "conveyor_a", "held": "$part"}},
            ],
        },
    }
    result = FleetRuntime({"arm": MockROSAdapter()}).execute(roster, {"arm": ARM_MANIFEST}, program)
    assert result.success


def test_steps_executed_counts_primitives_not_barriers():
    result = _fleet().execute(ROSTER, MEMBERS, HANDOFF_PROGRAM)
    # 5 primitives run: courier move_to, arm pick_from, arm place_at, courier wait,
    # courier move_to. The two barriers are rendezvous markers, not steps.
    assert result.steps_executed == 5
