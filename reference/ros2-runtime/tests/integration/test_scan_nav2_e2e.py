"""End-to-end: a URML ``scan`` driven by a live ``RclpyAdapter`` through real Nav2.

A validated program with one ``scan`` step runs through ``URMLRuntime`` and a
live ``RclpyAdapter``. The adapter plans the waypoints (``scan_plan``), sends
Nav2 one ``NavigateToPose`` goal per waypoint, and photographs each stop from
``/camera/image_raw``. A listen-only witness on its own node samples the
``map`` -> ``base_link`` transform during the scan, so the test checks where
the robot went, not only what the adapter reported: the robot came within
``_ARRIVAL_TOLERANCE_M`` of every waypoint the scan reported as a sample, and
ended the scan inside the area.

Written against Nav2's loopback simulator (``nav2_bringup``
``tb3_loopback_simulation.launch.py``: the real planner, controller and
behavior tree over a kinematic robot, no physics or rendering) with a
publisher of small images on ``/camera/image_raw`` and of ``std_msgs/Float64``
on ``/sensor/soil_probe``. See INTEGRATION.md.

## Gating

``URML_NAV2_SCAN_E2E=1`` opts in, and Nav2's ``/navigate_to_pose`` must
answer within ``_NAV_SERVER_TIMEOUT_S``. The default ``pytest`` run skips this
module.
"""

from __future__ import annotations

import math
import os
import threading
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.skipif(
    os.environ.get("URML_NAV2_SCAN_E2E") != "1",
    reason="Set URML_NAV2_SCAN_E2E=1 (with Nav2 and the test publishers running) to run the scan e2e test.",
)

REPO_ROOT = Path(__file__).resolve().parents[4]
_MANIFEST = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures" / "manifests" / "turtlebot4_home.yaml"
_ADAPTER_CONFIG = Path(__file__).parent / "adapter_scan_nav2.yaml"
# Open floor in nav2_bringup's depot map: a 2 m square centred on the robot's
# start pose (-3, 0), inside the 5.7 m square the map shows clear of obstacles
# by at least 0.8 m.
_AREA = {"min_x": -4.0, "max_x": -2.0, "min_y": -1.0, "max_y": 1.0}
_NAV_SERVER_TIMEOUT_S = 60.0
# Nav2's goal checker stops the robot within its xy_goal_tolerance (0.25 m
# in the TurtleBot 3 configuration); allow a little for sampling at 10 Hz.
_ARRIVAL_TOLERANCE_M = 0.35


class _PoseWitness:
    """Samples map -> base_link at 10 Hz on its own node and executor, never sending anything."""

    def __init__(self) -> None:
        import rclpy
        from rclpy.executors import SingleThreadedExecutor
        from tf2_ros import Buffer, TransformListener

        self._rclpy = rclpy
        self.node = rclpy.create_node("urml_scan_e2e_witness")
        self._buffer = Buffer()
        self._listener = TransformListener(self._buffer, self.node)
        self.poses: list[tuple[float, float]] = []
        self.node.create_timer(0.1, self._sample)
        self._executor = SingleThreadedExecutor()
        self._executor.add_node(self.node)
        self._thread = threading.Thread(target=self._executor.spin, daemon=True)

    def _sample(self) -> None:
        from rclpy.time import Time

        try:
            transform = self._buffer.lookup_transform("map", "base_link", Time())
        except Exception:  # the transform is not available yet
            return
        self.poses.append((transform.transform.translation.x, transform.transform.translation.y))

    def __enter__(self) -> _PoseWitness:
        self._thread.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self._executor.shutdown()
        self._thread.join(timeout=2.0)
        self.node.destroy_node()

    def closest(self, x: float, y: float) -> float:
        return min(math.hypot(px - x, py - y) for px, py in self.poses)


def _wait_for_nav2(timeout_s: float) -> bool:
    import rclpy
    from nav2_msgs.action import NavigateToPose
    from rclpy.action import ActionClient

    probe = rclpy.create_node("urml_scan_e2e_nav2_probe")
    try:
        return bool(ActionClient(probe, NavigateToPose, "/navigate_to_pose").wait_for_server(timeout_sec=timeout_s))
    finally:
        probe.destroy_node()


def _program(pattern: str) -> dict[str, Any]:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {
                    "scan": {
                        "area": {"bounding_box": _AREA},
                        "pattern": pattern,
                        "overlap": 0.3,
                        "media": "photo",
                        "sensor": "oakd_rgb",
                        "store_as": "survey",
                    }
                }
            ],
        },
    }


@pytest.fixture(scope="module")
def ros() -> Any:
    import rclpy

    rclpy.init()
    try:
        assert _wait_for_nav2(_NAV_SERVER_TIMEOUT_S), (
            f"Nav2 /navigate_to_pose did not answer within {_NAV_SERVER_TIMEOUT_S:.0f}s; "
            "is the loopback simulation up? See INTEGRATION.md."
        )
        yield rclpy
    finally:
        rclpy.shutdown()


def test_a_validated_serpentine_scan_drives_the_robot_over_the_area(ros: Any) -> None:
    from urml_ros2_runtime import URMLRuntime
    from urml_ros2_runtime.substrate.adapter_config import load_adapter_config
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    manifest = yaml.safe_load(_MANIFEST.read_text(encoding="utf-8"))
    config = load_adapter_config(_ADAPTER_CONFIG)
    with _PoseWitness() as witness, RclpyAdapter(config, node_name="urml_scan_e2e_serpentine") as adapter:
        result = URMLRuntime(adapter).execute(_program("serpentine"), manifest, None, ("home",), policy=None)

    assert result.success is True, result.model_dump()
    survey = result.bindings["survey"]
    print(
        f"scan: {survey['sample_count']}/{survey['waypoints']} samples, coverage {survey['coverage']}, "
        f"skipped {survey['skipped']}; witness samples {len(witness.poses)}"
    )
    assert survey["sample_count"] >= 1
    assert survey["coverage"] > 0
    assert all(sample["media"]["uri"].startswith("in_memory://") for sample in survey["samples"])
    # The robot really stood at each sampled waypoint.
    closest = {
        sample["index"]: round(witness.closest(sample["pose"]["x"], sample["pose"]["y"]), 3)
        for sample in survey["samples"]
    }
    print(f"witness: closest approach per waypoint (m) {closest}; end pose {witness.poses[-1]}")
    misses = {index: distance for index, distance in closest.items() if distance > _ARRIVAL_TOLERANCE_M}
    assert not misses, f"waypoints the robot never came within {_ARRIVAL_TOLERANCE_M} m of: {misses}"
    end_x, end_y = witness.poses[-1]
    margin = _ARRIVAL_TOLERANCE_M
    assert _AREA["min_x"] - margin <= end_x <= _AREA["max_x"] + margin
    assert _AREA["min_y"] - margin <= end_y <= _AREA["max_y"] + margin


def test_a_goal_nav2_aborts_is_a_failure(ros: Any) -> None:
    """Nav2 accepts a goal off the map, then aborts it. The adapter used to report that as success."""
    from urml_ros2_runtime.substrate.adapter_config import load_adapter_config
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    with RclpyAdapter(load_adapter_config(_ADAPTER_CONFIG), node_name="urml_scan_e2e_abort") as adapter:
        result = adapter.send_navigation_goal(pose={"x": 100.0, "y": 100.0}, frame="map")
    print(f"goal off the map: success={result.success} reason={result.reason!r}")
    assert result.success is False
    assert result.reason is not None and result.reason.startswith("goal_aborted")


def test_a_sensor_scan_reads_the_probe_at_each_stop(ros: Any) -> None:
    """Adapter level (the manifest declares no probe): one /sensor/soil_probe reading per stop."""
    from urml_ros2_runtime.substrate.adapter_config import load_adapter_config
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    config = load_adapter_config(_ADAPTER_CONFIG)
    with RclpyAdapter(config, node_name="urml_scan_e2e_sensor") as adapter:
        result = adapter.run_scan(
            area={"bounding_box": _AREA},
            pattern="spiral",
            overlap=0.0,
            altitude=None,
            media="sensor_only",
            sensor="soil_probe",
        )
    assert result.success is True, result.reason
    assert result.payload is not None
    values = [sample["reading"]["value"] for sample in result.payload["samples"]]
    print(f"spiral sensor scan: {len(values)} readings, skipped {result.payload['skipped']}")
    assert len(values) == result.payload["sample_count"] >= 1
