"""RFC-0286 — fleet validation tests.

Covers the multi-robot entry point `validate_fleet` and its four cross-robot
checks, plus the invariant that a single-robot program is unaffected by the new
schema nodes.

The running example is the courier-to-arm handoff: a mobile base (`courier`)
brings itself to a dock; a stationary arm (`arm`) picks a widget from the dock
and places it on a conveyor; barriers bracket the exchange.
"""

from __future__ import annotations

import copy

from urml_validator import ErrorCode, validate, validate_fleet

# ---------------------------------------------------------------------------
# Member manifests (inline dicts; resolved by validate_fleet).
# ---------------------------------------------------------------------------

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

# The canonical courier-to-arm handoff program (tagged surface).
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


def _fleet(program, roster=ROSTER, members=MEMBERS, **kw):
    return validate_fleet(roster, members, program, policy=None, **kw)


# ---------------------------------------------------------------------------
# Positive: the canonical handoff validates.
# ---------------------------------------------------------------------------


def test_courier_to_arm_handoff_accepted():
    result = _fleet(HANDOFF_PROGRAM)
    assert result.accepted, result.codes()
    assert result.errors == []


def test_cross_member_binding_resolves():
    # $part is produced by the arm's pick_from and consumed by its place_at;
    # the single fleet tree resolves it in lexical order.
    result = _fleet(HANDOFF_PROGRAM)
    assert not result.has(ErrorCode.BINDING_UNRESOLVED_REFERENCE)


# ---------------------------------------------------------------------------
# fleet.undeclared_member
# ---------------------------------------------------------------------------


def test_on_undeclared_member_rejected():
    program = copy.deepcopy(HANDOFF_PROGRAM)
    program["behavior"]["steps"][0]["member"] = "gripper"  # not in roster
    result = _fleet(program)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_UNDECLARED_MEMBER)


def test_barrier_undeclared_member_rejected():
    program = copy.deepcopy(HANDOFF_PROGRAM)
    program["behavior"]["steps"][1]["members"] = ["courier", "forklift"]
    result = _fleet(program)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_UNDECLARED_MEMBER)


def test_unaddressed_step_in_multi_member_fleet_rejected():
    # A bare step at the top level (no `on:`) is unaddressed in a 2-member fleet.
    program = {
        "profile": "industrial",
        "behavior": {"move_to": {"location": "handoff_dock"}},
    }
    result = _fleet(program)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_UNDECLARED_MEMBER)


def test_single_member_fleet_allows_unaddressed_step():
    # A fleet of one: an unaddressed step resolves to the sole member.
    roster = {"roster_version": "0.1", "members": [{"name": "courier", "manifest": "husky_amr"}]}
    program = {
        "profile": "industrial",
        "behavior": {"move_to": {"location": "handoff_dock"}},
    }
    result = validate_fleet(roster, {"courier": COURIER_MANIFEST}, program, policy=None)
    assert result.accepted, result.codes()


# ---------------------------------------------------------------------------
# fleet.capability_unsupported_on_member
# ---------------------------------------------------------------------------


def test_capability_unsupported_on_member_rejected():
    # Scope pick_from to the courier, which has no manipulation or perception.
    program = {
        "profile": "industrial",
        "behavior": {
            "type": "on",
            "member": "courier",
            "body": {"pick_from": {"source": "handoff_dock", "object": "widget"}},
        },
    }
    result = _fleet(program)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CAPABILITY_UNSUPPORTED_ON_MEMBER)
    # The offending member is named in detail for the LLM bridge.
    fleet_errs = [e for e in result.errors if e.code == ErrorCode.FLEET_CAPABILITY_UNSUPPORTED_ON_MEMBER]
    assert all(e.detail and e.detail.get("member") == "courier" for e in fleet_errs)


# ---------------------------------------------------------------------------
# fleet.concurrent_shared_workspace
# ---------------------------------------------------------------------------


def test_concurrent_shared_workspace_rejected():
    program = {
        "profile": "industrial",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"type": "on", "member": "courier", "body": {"move_to": {"location": "handoff_dock"}}},
                {"type": "on", "member": "arm", "body": {"move_to": {"location": "handoff_dock"}}},
            ],
        },
    }
    result = _fleet(program)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


def test_same_member_same_location_not_flagged():
    # One member targeting a location twice across branches is not a cross-robot
    # collision (it is a self-overlap the fleet check does not own).
    program = {
        "profile": "industrial",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"type": "on", "member": "arm", "body": {"move_to": {"location": "handoff_dock"}}},
                {"type": "on", "member": "arm", "body": {"move_to": {"location": "conveyor_a"}}},
            ],
        },
    }
    result = _fleet(program)
    assert not result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


# ---------------------------------------------------------------------------
# fleet.barrier_missing_peer_link
# ---------------------------------------------------------------------------


def test_barrier_without_peer_link_rejected():
    arm_no_peer = copy.deepcopy(ARM_MANIFEST)
    del arm_no_peer["connectivity"]  # arm no longer declares peer_link
    result = validate_fleet(
        ROSTER, {"courier": COURIER_MANIFEST, "arm": arm_no_peer}, HANDOFF_PROGRAM, policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_BARRIER_MISSING_PEER_LINK)


# ---------------------------------------------------------------------------
# Single-robot invariant: the new schema nodes don't change `validate`.
# ---------------------------------------------------------------------------


def test_single_robot_program_unaffected():
    # A program with no on:/barrier nodes validates through the single-robot path
    # exactly as before RFC-0286.
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
    result = validate(program, ARM_MANIFEST, policy=None)
    assert result.accepted, result.codes()


def test_missing_member_manifest_rejected():
    # Roster declares two members but only one manifest is resolved.
    result = validate_fleet(ROSTER, {"courier": COURIER_MANIFEST}, HANDOFF_PROGRAM, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_UNDECLARED_MEMBER)


def test_bad_roster_short_circuits():
    bad_roster = {"roster_version": "0.1", "members": []}  # min_length 1
    result = validate_fleet(bad_roster, MEMBERS, HANDOFF_PROGRAM, policy=None)
    assert not result.accepted
