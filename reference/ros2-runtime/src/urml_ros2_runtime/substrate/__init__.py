"""Substrate adapters — the surface between the URML runtime and ROS 2.

The runtime talks to ROS 2 *only* through the ``ROSAdapter`` Protocol in
``base.py``. Concrete adapters shipped in v0.1:

  - ``MockROSAdapter`` (in ``mock.py``) — fully hermetic. No ROS, no network.
    Records every call and returns canned responses. Used in tests and for
    development on hosts where ROS 2 isn't installed.
  - ``RclpyAdapter`` (in ``rclpy_adapter.py``) — real ROS 2 backing via
    ``rclpy``. rclpy is imported lazily so this module is safe to load on
    every host; constructing the adapter without rclpy raises a clear,
    actionable error.

The Protocol shape is intentionally higher-level than raw ROS topics/actions
so that a non-ROS adapter (PX4 / MAVLink, OPC UA Robotics, vendor SDK) can
implement the same surface without first translating to ROS-isms.
"""

from urml_ros2_runtime.substrate.adapter_config import (
    ActionServerConfig,
    AdapterConfig,
    PerceptionTopics,
    PoseLiteral,
    SpeechTopics,
    load_adapter_config,
)
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
from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

__all__ = [
    "ActionServerConfig",
    "AdapterConfig",
    "CaptureResult",
    "DetectionResult",
    "ListenResult",
    "ManipulationResult",
    "MeasurementResult",
    "MockROSAdapter",
    "NavigationResult",
    "PerceptionTopics",
    "PoseLiteral",
    "ROSAdapter",
    "RclpyAdapter",
    "ScanResult",
    "SpeechTopics",
    "SubstrateResult",
    "WaitResult",
    "load_adapter_config",
]
