"""RFC-0286 — FleetRuntime concurrency + executed barrier semantics.

Proves the `parallel` runtime actually dispatches members at the same time (via a
rendezvous barrier that only clears if two members run concurrently), that
`sequential=True` does NOT interleave, that a `barrier` serializes members, and
that the unguarded cross-robot collision the validator rejects really does fire
both robots at once when validation is bypassed.
"""

from __future__ import annotations

import copy
import threading

from urml_validator import ErrorCode, validate_fleet
from urml_ros2_runtime import FleetRuntime, MockROSAdapter, NavigationResult


class RendezvousAdapter(MockROSAdapter):
    """A mock whose navigation goal blocks on a shared barrier — a move only
    completes if a sibling member's move is dispatched at the same time. If the
    members run one-at-a-time, the wait times out and the move fails."""

    def __init__(self, gate: threading.Barrier) -> None:
        super().__init__()
        self._gate = gate

    def send_navigation_goal(self, *args: object, **kwargs: object) -> NavigationResult:
        try:
            self._gate.wait(timeout=0.5)
        except threading.BrokenBarrierError:
            return NavigationResult(success=False, reason="rendezvous_timeout")
        return super().send_navigation_goal(*args, **kwargs)  # type: ignore[arg-type]


_MANIFEST = {
    "robot_id": "mover",
    "frames": [{"name": "map"}],
    "declared_locations": [
        {"name": "spot_a", "pose": {"x": 1.0, "y": 0.0}, "frame": "map"},
        {"name": "spot_b", "pose": {"x": 2.0, "y": 0.0}, "frame": "map"},
    ],
    "mobility": {"drive_type": "differential", "max_velocity": 1.0},
    "connectivity": {"links": [{"role": "peer_link"}]},
}

ROSTER = {
    "roster_version": "0.1",
    "members": [{"name": "a", "manifest": "m"}, {"name": "b", "manifest": "m"}],
    "shared_frames": ["map"],  # RFC-0287: a shared frame so the collision check compares
}
MEMBERS = {"a": copy.deepcopy(_MANIFEST), "b": copy.deepcopy(_MANIFEST)}

PARALLEL = {
    "profile": "home",
    "behavior": {
        "type": "parallel",
        "branches": [
            {"type": "on", "member": "a", "body": {"move_to": {"location": "spot_a"}}},
            {"type": "on", "member": "b", "body": {"move_to": {"location": "spot_b"}}},
        ],
    },
}


def test_parallel_dispatches_members_concurrently():
    # Both moves rendezvous at the barrier => they ran at the same time.
    gate = threading.Barrier(2)
    adapters = {"a": RendezvousAdapter(gate), "b": RendezvousAdapter(gate)}
    result = FleetRuntime(adapters).execute(ROSTER, MEMBERS, PARALLEL, policy=None)
    assert result.success


def test_sequential_mode_does_not_interleave():
    # One-at-a-time => the first move waits for a sibling that never comes => fail.
    gate = threading.Barrier(2)
    adapters = {"a": RendezvousAdapter(gate), "b": RendezvousAdapter(gate)}
    result = FleetRuntime(adapters, sequential=True).execute(ROSTER, MEMBERS, PARALLEL, policy=None)
    assert not result.success


def test_barrier_serializes_members():
    # A barrier between the two moves puts them in different sequence steps, so
    # they never overlap — the rendezvous times out, proving the barrier serialized.
    gate = threading.Barrier(2)
    adapters = {"a": RendezvousAdapter(gate), "b": RendezvousAdapter(gate)}
    program = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"type": "on", "member": "a", "body": {"move_to": {"location": "spot_a"}}},
                {"type": "barrier", "members": ["a", "b"]},
                {"type": "on", "member": "b", "body": {"move_to": {"location": "spot_b"}}},
            ],
        },
    }
    result = FleetRuntime(adapters).execute(ROSTER, MEMBERS, program, policy=None)
    assert not result.success


def test_unguarded_concurrent_collision_fires_both_robots():
    # The validator REJECTS two members at one location in a parallel
    # (fleet.concurrent_shared_workspace). Bypass validation to show what the
    # rejection prevents: both robots are actually dispatched to the same spot.
    collision = {
        "profile": "home",
        "behavior": {
            "type": "parallel",
            "branches": [
                {"type": "on", "member": "a", "body": {"move_to": {"location": "spot_a"}}},
                {"type": "on", "member": "b", "body": {"move_to": {"location": "spot_a"}}},
            ],
        },
    }
    # The validator would catch it.
    verdict = validate_fleet(ROSTER, MEMBERS, collision, policy=None)
    assert verdict.has(ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE)
    # Bypassed, both adapters fire — the hazard the check exists to prevent.
    adapters = {"a": MockROSAdapter(), "b": MockROSAdapter()}
    result = FleetRuntime(adapters, revalidate=False).execute(ROSTER, MEMBERS, collision, policy=None)
    assert result.success
    assert [c["method"] for c in result.per_member_audit["a"]] == ["send_navigation_goal"]
    assert [c["method"] for c in result.per_member_audit["b"]] == ["send_navigation_goal"]
