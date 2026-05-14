"""Substrate adapters — the surface between the URML runtime and ROS 2.

The runtime talks to ROS 2 *only* through the ``ROSAdapter`` Protocol in
``base.py``. Concrete adapters:

  - ``MockROSAdapter`` (in ``mock.py``) — fully hermetic. No ROS, no network.
    Records every call and returns canned responses. Used in tests and for
    development on hosts where ROS 2 isn't installed.
  - ``RclpyAdapter`` (planned, follow-up PR) — real ROS 2 backing via ``rclpy``.

The Protocol shape is intentionally higher-level than raw ROS topics/actions
so that a non-ROS adapter (PX4 / MAVLink, OPC UA Robotics, vendor SDK) can
implement the same surface without first translating to ROS-isms.
"""

from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ROSAdapter,
    ScanResult,
    SubstrateResult,
    WaitResult,
)
from urml_ros2_runtime.substrate.mock import MockROSAdapter

__all__ = [
    "CaptureResult",
    "DetectionResult",
    "ListenResult",
    "ManipulationResult",
    "MeasurementResult",
    "MockROSAdapter",
    "NavigationResult",
    "ROSAdapter",
    "ScanResult",
    "SubstrateResult",
    "WaitResult",
]
