"""End-to-end: a URML conformance fixture driving a simulated robot.

This is the real thing — not a smoke test. It takes the
``home/nav_patrol_positive`` conformance fixture (three plain
``move_to`` goals), runs it through the *same* ``ConformanceRunner``
the hermetic suite uses, but with the ``adapter_factory`` wired to a
live ``RclpyAdapter``. The adapter sends Nav2 ``/navigate_to_pose``
goals to a running TurtleBot 4 Ignition simulation. If the simulated
robot drives to all three poses and Nav2 reports success, the fixture
passes — proving the full path closes:

    URML program -> validator -> ConformanceRunner -> RclpyAdapter
                 -> Nav2 -> simulated TurtleBot 4 actually moves.

## Gating

Two independent gates, both required:

  - ``URML_GAZEBO_E2E=1`` — opt in to the heavy sim test. Distinct from
    ``URML_ROS2_INTEGRATION`` (which only needs rclpy, no simulator).
  - The ``/navigate_to_pose`` action server must be reachable within a
    short bound. If it isn't, the test fails fast with an actionable
    message ("is the TB4 sim + Nav2 actually up?") rather than hanging.

The default ``pytest`` invocation skips this module entirely. The
``gazebo-e2e`` job in ``.github/workflows/ros2-integration.yml`` brings
up the sim, sets the env var, and runs it; it also uploads sim + Nav2
logs as artifacts so a failed first run is diagnosable, not opaque.

## Honest scope

A stock TurtleBot 4 sim exposes Nav2 navigation but its dock is iRobot
Create 3's ``/dock`` action (not Nav2 ``DockRobot``), and it has no
gripper or camera. So this covers the *navigation* slice end-to-end —
the load-bearing one for "does the adapter actually drive a real
robot". Perception / manipulation / docking e2e need a richer sim and
are tracked as follow-ups in INTEGRATION.md.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_GAZEBO_E2E") != "1",
    reason="Set URML_GAZEBO_E2E=1 (and have a TB4+Nav2 sim running) to run the Gazebo e2e test.",
)

_ADAPTER_CONFIG = Path(__file__).parent / "adapter_nav_patrol.yaml"
_FIXTURE_NAME = "home/nav_patrol_positive"

# How long to wait for Nav2's action server to come up before declaring
# the sim absent. Generous because a cold sim + Nav2 lifecycle bringup
# is slow, but bounded so a missing sim fails fast-ish with a clear
# message instead of an opaque hang.
_NAV_SERVER_TIMEOUT_S = 60.0


def _wait_for_nav2(timeout_s: float) -> bool:
    """Return True once Nav2's /navigate_to_pose action server answers."""
    import rclpy
    from rclpy.action import ActionClient
    from rclpy.node import Node

    probe: Node = rclpy.create_node("urml_e2e_nav2_probe")
    try:
        from nav2_msgs.action import NavigateToPose

        client = ActionClient(probe, NavigateToPose, "/navigate_to_pose")
        return bool(client.wait_for_server(timeout_sec=timeout_s))
    finally:
        probe.destroy_node()


def test_nav_patrol_fixture_runs_against_gazebo() -> None:
    """The nav-patrol fixture passes when executed against the live sim."""
    import rclpy

    from urml_conformance import ConformanceRunner, discover_fixtures
    from urml_ros2_runtime.substrate.adapter_config import load_adapter_config
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    rclpy.init()
    try:
        # Fail fast + actionable if the simulator/Nav2 isn't actually up.
        assert _wait_for_nav2(_NAV_SERVER_TIMEOUT_S), (
            "Nav2 /navigate_to_pose action server did not come up within "
            f"{_NAV_SERVER_TIMEOUT_S:.0f}s. Is the TurtleBot 4 Ignition sim "
            "running with Nav2 (headless)? See INTEGRATION.md for the local "
            "WSL2 repro."
        )

        config = load_adapter_config(_ADAPTER_CONFIG)

        # Run ONLY the nav-patrol fixture through the same runner the
        # hermetic suite uses — the only difference is the adapter.
        cases = [c for c in discover_fixtures() if c.name == _FIXTURE_NAME]
        assert cases, f"fixture {_FIXTURE_NAME!r} not found in the conformance suite"

        runner = ConformanceRunner(
            cases=cases,
            adapter_factory=lambda: RclpyAdapter(config),
        )
        report = runner.run()
        assert report.all_passed, (
            "nav-patrol fixture failed against the live sim:\n" + report.render()
        )
    finally:
        rclpy.shutdown()
