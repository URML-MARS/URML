"""urml_legged_runtime — legged/quadruped reference runtime for URML.

One first-class adapter per vendor, both implementing the
substrate-neutral ``ROSAdapter`` Protocol:

  SpotAdapter (+ SpotConfig, load_spot_config)
    Boston Dynamics Spot via the ``bosdyn`` gRPC SDK. No ROS 2
    dependency (the [spot] extra installs the bosdyn wheels). Like
    PX4Adapter, a second proof the spec carries no ROS assumptions.

  AnymalAdapter
    ANYbotics ANYmal — a ROS 2 quadruped, so it composes the ROS 2
    runtime's RclpyAdapter (the industrial-arm single-sourced-substrate
    pattern). No duplicated ROS 2 plumbing.

  LEGGED_ADAPTERS
    Name → class registry ({"spot": SpotAdapter, "anymal":
    AnymalAdapter}) for config-driven selection (CI matrices, the
    conformance adapter_factory).

Both bosdyn and rclpy are imported lazily, so this module loads on
every host; constructing an adapter needs that vendor's runtime
(the [spot] extra, or a sourced ROS 2 environment).
"""

from __future__ import annotations

from urml_legged_runtime._version import __version__
from urml_legged_runtime.anymal import AnymalAdapter
from urml_legged_runtime.spot import SpotAdapter, SpotConfig, load_spot_config

LEGGED_ADAPTERS: dict[str, type] = {
    "spot": SpotAdapter,
    "anymal": AnymalAdapter,
}

__all__ = [
    "LEGGED_ADAPTERS",
    "AnymalAdapter",
    "SpotAdapter",
    "SpotConfig",
    "__version__",
    "load_spot_config",
]
