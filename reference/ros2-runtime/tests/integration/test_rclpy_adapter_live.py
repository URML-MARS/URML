"""Live integration tests for RclpyAdapter — gated to the ROS 2 CI runner.

These tests require a working ROS 2 environment:

  - rclpy must import (`source /opt/ros/<distro>/setup.bash`).
  - `rclpy.init()` must have been called before each test starts.
  - For full coverage, a Gazebo TurtleBot 4 simulation should be running
    so Nav2 / MoveIt 2 action servers respond.

The default `pytest` invocation skips this file entirely. The dedicated
workflow `.github/workflows/ros2-integration.yml` sets
`URML_ROS2_INTEGRATION=1` before running pytest with
`--integration`, which flips the skip condition.

What's covered today vs. follow-up:

  - **Today (v0.1):** A smoke test that constructs ``RclpyAdapter``
    against a real rclpy, exercises lifecycle (node create + destroy),
    and confirms the lazy imports resolve. This proves the adapter
    code loads correctly under a real ROS 2 install and that the
    optional `[ros2]` extra's deps are sufficient.
  - **Follow-up (Phase 5 per INTEGRATION.md):** Full Gazebo integration
    tests that run the conformance fixture suite against the simulator.
    The runner already accepts an `adapter_factory` hook for this; the
    blocker is a pinned-Gazebo CI image, not adapter code.
"""

from __future__ import annotations

import os

import pytest

# Skip the whole module unless the integration flag is set. This keeps
# the default `pytest` invocation hermetic on every host.
pytestmark = pytest.mark.skipif(
    os.environ.get("URML_ROS2_INTEGRATION") != "1",
    reason="Set URML_ROS2_INTEGRATION=1 to run live ROS 2 integration tests.",
)


def test_real_rclpy_is_importable() -> None:
    """The real rclpy module is available under the integration env."""
    import rclpy  # noqa: F401


def test_adapter_constructs_and_closes_against_real_rclpy() -> None:
    """RclpyAdapter lifecycle works against a real ROS 2 install."""
    import rclpy

    rclpy.init()
    try:
        from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

        with RclpyAdapter(node_name="urml_integration_smoke") as adapter:
            # Sanity: the adapter owns a real rclpy node.
            assert adapter._node is not None
    finally:
        rclpy.shutdown()


def test_conformance_runner_accepts_real_adapter_factory() -> None:
    """The ConformanceRunner can be wired to construct a real adapter per case.

    This test does NOT run the fixture suite end-to-end because most
    fixtures expect Nav2/MoveIt/perception servers that aren't running
    in a bare ROS 2 install. The hook itself is what we're testing — it
    must accept a real-adapter factory without raising.
    """
    import rclpy

    rclpy.init()
    try:
        from urml_conformance import ConformanceRunner
        from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

        runner = ConformanceRunner(adapter_factory=lambda: RclpyAdapter())
        assert runner is not None
    finally:
        rclpy.shutdown()
