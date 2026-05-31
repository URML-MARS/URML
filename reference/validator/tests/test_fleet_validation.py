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
    "frames": [{"name": "map"}, {"name": "site"}],
    "declared_locations": [
        # handoff_dock is the shared site frame both robots reference; staging is local.
        {"name": "handoff_dock", "pose": {"x": 1.0, "y": 1.0}, "frame": "site"},
        {"name": "staging", "pose": {"x": 0.0, "y": 0.0}, "frame": "map"},
    ],
    "mobility": {"drive_type": "differential", "max_velocity": 1.5},
    "connectivity": {"links": [{"role": "peer_link"}]},
}

ARM_MANIFEST = {
    "robot_id": "arm",
    "frames": [{"name": "cell"}, {"name": "site"}],
    "declared_locations": [
        {"name": "handoff_dock", "pose": {"x": 1.0, "y": 1.0}, "frame": "site"},
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
    "shared_frames": ["site"],
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


# ===========================================================================
# RFC-0291 — geometric (UTM) strategic deconfliction across the three media
# ===========================================================================


def _geo_manifest(robot_id, drive, frame, locs, radius, vertical, *, ceiling=None, autopilot=None):
    mob = {
        "drive_type": drive,
        "max_velocity": 1.0,
        "clearance": {"radius_m": radius, "vertical_m": vertical},
    }
    if ceiling is not None:
        mob["service_ceiling"] = ceiling
    manifest = {
        "robot_id": robot_id,
        "frames": [{"name": frame}],
        "declared_locations": locs,
        "mobility": mob,
        "connectivity": {"links": [{"role": "peer_link"}]},
    }
    if autopilot is not None:
        manifest["substrate"] = {"autopilot_class": autopilot}
    return manifest


def _loc(name, x, y, z, frame):
    return {"name": name, "pose": {"x": x, "y": y, "z": z}, "frame": frame}


def _roster2(shared):
    return {
        "roster_version": "0.1",
        "members": [{"name": "a", "manifest": "a"}, {"name": "b", "manifest": "b"}],
        "shared_frames": shared,
    }


def _parallel2(loc_a, loc_b):
    return {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"type": "on", "member": "a", "body": {"move_to": {"location": loc_a}}},
                {"type": "on", "member": "b", "body": {"move_to": {"location": loc_b}}},
            ],
        },
    }


def _geo_fleet(a, b, program, shared):
    return validate_fleet(_roster2(shared), {"a": a, "b": b}, program, policy=None)


# ---- 07 ground: footprints overlap (distinct names) -> REJECT --------------


def test_geometric_ground_footprint_overlap_rejected():
    a = _geo_manifest("a", "differential", "site", [_loc("spot_a", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    b = _geo_manifest("b", "differential", "site", [_loc("spot_b", 0.4, 0.0, 0.0, "site")], 0.5, 1.0)
    result = _geo_fleet(a, b, _parallel2("spot_a", "spot_b"), ["site"])
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


# ---- 08/09 air: altitude separation -> ACCEPT; same altitude -> REJECT -----


def test_geometric_air_vertical_separation_accepted():
    a = _geo_manifest("a", "multirotor", "agl", [_loc("low", 0.0, 0.0, 0.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    b = _geo_manifest("b", "multirotor", "agl", [_loc("high", 0.0, 0.0, 30.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    result = _geo_fleet(a, b, _parallel2("low", "high"), ["agl"])
    assert result.accepted, result.codes()


def test_geometric_air_same_altitude_rejected():
    a = _geo_manifest("a", "multirotor", "agl", [_loc("p_a", 0.0, 0.0, 30.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    b = _geo_manifest("b", "multirotor", "agl", [_loc("p_b", 0.0, 0.0, 30.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    result = _geo_fleet(a, b, _parallel2("p_a", "p_b"), ["agl"])
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


# ---- 10/11 water: depth separation -> ACCEPT; same depth -> REJECT ---------


def test_geometric_water_depth_separation_accepted():
    a = _geo_manifest("a", "underwater_thrusters", "water", [_loc("shallow", 0.0, 0.0, -2.0, "water")], 0.5, 2.0)
    b = _geo_manifest("b", "underwater_thrusters", "water", [_loc("deep", 0.0, 0.0, -8.0, "water")], 0.5, 2.0)
    result = _geo_fleet(a, b, _parallel2("shallow", "deep"), ["water"])
    assert result.accepted, result.codes()


def test_geometric_water_same_depth_rejected():
    a = _geo_manifest("a", "underwater_thrusters", "water", [_loc("d_a", 0.0, 0.0, -5.0, "water")], 0.5, 2.0)
    b = _geo_manifest("b", "underwater_thrusters", "water", [_loc("d_b", 0.0, 0.0, -5.0, "water")], 0.5, 2.0)
    result = _geo_fleet(a, b, _parallel2("d_a", "d_b"), ["water"])
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


# ---- 12 cross-medium: air vs water never collide -> ACCEPT -----------------


def test_geometric_cross_medium_accepted():
    drone = _geo_manifest("a", "multirotor", "site", [_loc("p_a", 0.0, 0.0, 0.0, "site")], 0.5, 5.0, ceiling=120, autopilot="px4")
    rov = _geo_manifest("b", "underwater_thrusters", "site", [_loc("p_b", 0.0, 0.0, 0.0, "site")], 0.5, 5.0)
    result = _geo_fleet(drone, rov, _parallel2("p_a", "p_b"), ["site"])
    assert result.accepted, result.codes()  # overlapping poses, but medium gate stops it


# ---- 13 temporal: a barrier deconflicts the same volume -> ACCEPT ----------


def test_temporal_barrier_deconflicts():
    a = _geo_manifest("a", "differential", "site", [_loc("spot", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    b = _geo_manifest("b", "differential", "site", [_loc("spot", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    program = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"type": "on", "member": "a", "body": {"move_to": {"location": "spot"}}},
                {"type": "barrier", "members": ["a", "b"]},
                {"type": "on", "member": "b", "body": {"move_to": {"location": "spot"}}},
            ],
        },
    }
    result = _geo_fleet(a, b, program, ["site"])
    assert result.accepted, result.codes()  # not concurrent: the barrier separates them in time


# ---- 14 local frames: not a shared frame -> no false positive -> ACCEPT ----


def test_local_frame_not_compared_accepted():
    # The engaged-partners case: three robots each with a private `floor` frame and
    # a same-named `waypoint_a`. With no shared frame, they are never compared.
    def mover(rid):
        return _geo_manifest(rid, "differential", "floor", [_loc("waypoint_a", 0.3, 0.0, 0.0, "floor")], 0.5, 1.0)

    roster = {
        "roster_version": "0.1",
        "members": [{"name": n, "manifest": n} for n in ("m1", "m2", "m3")],
        "shared_frames": [],
    }
    program = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"type": "on", "member": n, "body": {"move_to": {"location": "waypoint_a"}}}
                for n in ("m1", "m2", "m3")
            ],
        },
    }
    result = validate_fleet(roster, {n: mover(n) for n in ("m1", "m2", "m3")}, program, policy=None)
    assert result.accepted, result.codes()


# ---- 15 name fallback still works when no clearance declared ---------------


def test_name_fallback_within_shared_frame_rejected():
    # No clearance declared -> fall back to name-equality, but now frame-gated.
    a = {
        "robot_id": "a",
        "frames": [{"name": "site"}],
        "declared_locations": [_loc("dock", 0.0, 0.0, 0.0, "site")],
        "mobility": {"drive_type": "differential", "max_velocity": 1.0},
        "connectivity": {"links": [{"role": "peer_link"}]},
    }
    b = copy.deepcopy(a)
    b["robot_id"] = "b"
    result = _geo_fleet(a, b, _parallel2("dock", "dock"), ["site"])
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


def test_shared_frame_undeclared_warns():
    a = _geo_manifest("a", "differential", "site", [_loc("spot_a", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    b = _geo_manifest("b", "differential", "site", [_loc("spot_b", 5.0, 0.0, 0.0, "site")], 0.5, 1.0)
    # Declare a shared frame no member has -> warning, still accepted (well separated).
    result = _geo_fleet(a, b, _parallel2("spot_a", "spot_b"), ["nonexistent"])
    assert result.accepted, result.codes()
    assert result.has(ErrorCode.FLEET_SHARED_FRAME_UNDECLARED)


# ===========================================================================
# RFC-0290 — cross-frame deconfliction via world-anchors (a drone's agl vs a
# rover's site, resolved into one world)
# ===========================================================================


def _anchored_roster(*anchors):
    # anchors: (name, manifest_key, anchor_frame, transform_dict)
    members = [
        {"name": n, "manifest": mk, "anchor": {"frame": af, "transform": tf}}
        for (n, mk, af, tf) in anchors
    ]
    return {"roster_version": "0.1", "world_frame": "world", "members": members}


def test_cross_frame_drone_over_rover_rejected():
    # Drone target in `agl` and rover target in `site` resolve to the SAME world
    # point (both anchored at world x=10); the drone is 1 m above the rover.
    drone = _geo_manifest("a", "multirotor", "agl", [_loc("p", 0.0, 0.0, 1.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    rover = _geo_manifest("b", "differential", "site", [_loc("q", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    roster = _anchored_roster(
        ("a", "a", "agl", {"translation": {"x": 10.0}}),
        ("b", "b", "site", {"translation": {"x": 10.0}}),
    )
    result = validate_fleet(roster, {"a": drone, "b": rover}, _parallel2("p", "q"), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)


def test_cross_frame_drone_high_above_rover_accepted():
    drone = _geo_manifest("a", "multirotor", "agl", [_loc("p", 0.0, 0.0, 30.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    rover = _geo_manifest("b", "differential", "site", [_loc("q", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    roster = _anchored_roster(
        ("a", "a", "agl", {"translation": {"x": 10.0}}),
        ("b", "b", "site", {"translation": {"x": 10.0}}),
    )
    result = validate_fleet(roster, {"a": drone, "b": rover}, _parallel2("p", "q"), policy=None)
    assert result.accepted, result.codes()  # 30 m of altitude separation in world


def test_cross_frame_air_water_still_exempt():
    drone = _geo_manifest("a", "multirotor", "agl", [_loc("p", 0.0, 0.0, 0.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    rov = _geo_manifest("b", "underwater_thrusters", "water", [_loc("q", 0.0, 0.0, 0.0, "water")], 0.5, 5.0)
    roster = _anchored_roster(
        ("a", "a", "agl", {"translation": {"x": 10.0}}),
        ("b", "b", "water", {"translation": {"x": 10.0}}),
    )
    # Same world point, but air vs water never collide.
    result = validate_fleet(roster, {"a": drone, "b": rov}, _parallel2("p", "q"), policy=None)
    assert result.accepted, result.codes()


def test_cross_frame_without_anchors_abstains():
    # No anchors and no shared_frames: agl and site never resolve to a common
    # world -> not compared -> accepted (backward-compatible abstention).
    drone = _geo_manifest("a", "multirotor", "agl", [_loc("p", 0.0, 0.0, 0.0, "agl")], 0.5, 5.0, ceiling=120, autopilot="px4")
    rover = _geo_manifest("b", "differential", "site", [_loc("q", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    roster = {"roster_version": "0.1", "members": [{"name": "a", "manifest": "a"}, {"name": "b", "manifest": "b"}]}
    result = validate_fleet(roster, {"a": drone, "b": rover}, _parallel2("p", "q"), policy=None)
    assert result.accepted, result.codes()


def test_anchor_frame_undeclared_warns():
    a = _geo_manifest("a", "differential", "site", [_loc("p", 0.0, 0.0, 0.0, "site")], 0.5, 1.0)
    b = _geo_manifest("b", "differential", "site", [_loc("q", 5.0, 0.0, 0.0, "site")], 0.5, 1.0)
    roster = _anchored_roster(
        ("a", "a", "ghost_frame", {"translation": {}}),  # not a frame member a declares
        ("b", "b", "site", {"translation": {}}),
    )
    result = validate_fleet(roster, {"a": a, "b": b}, _parallel2("p", "q"), policy=None)
    assert result.has(ErrorCode.FLEET_ANCHOR_FRAME_UNDECLARED)
