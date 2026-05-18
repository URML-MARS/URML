"""urml_industrial_arm_runtime — ROS-Industrial / MoveIt 2 reference runtime.

One first-class adapter per vendor, all implementing the substrate-neutral
``ROSAdapter`` Protocol:

  AbbAdapter, FanucAdapter, KukaAdapter, YaskawaAdapter
    Brand arm adapters. Each composes the ROS 2 runtime's RclpyAdapter
    (the MoveIt 2 / control_msgs shape an industrial arm needs is already
    implemented there) with a brand-default deployment config. rclpy is
    imported lazily inside RclpyAdapter, so this module loads on every
    host; constructing an adapter needs a sourced ROS 2 environment.

  IndustrialArmAdapter
    The shared core the brand classes subclass. Use a brand class
    directly; this is exposed for typing and custom-vendor extension.

  BRAND_ADAPTERS
    Name → class registry ({"abb": AbbAdapter, ...}) for config-driven
    selection (CI matrices, the conformance suite's adapter_factory).
"""

from __future__ import annotations

from urml_industrial_arm_runtime._version import __version__
from urml_industrial_arm_runtime.adapter import (
    AbbAdapter,
    FanucAdapter,
    FrankaAdapter,
    IndustrialArmAdapter,
    KukaAdapter,
    UrAdapter,
    YaskawaAdapter,
)

BRAND_ADAPTERS: dict[str, type[IndustrialArmAdapter]] = {
    "abb": AbbAdapter,
    "fanuc": FanucAdapter,
    "kuka": KukaAdapter,
    "yaskawa": YaskawaAdapter,
    "ur": UrAdapter,
    "franka": FrankaAdapter,
}

__all__ = [
    "BRAND_ADAPTERS",
    "AbbAdapter",
    "FanucAdapter",
    "FrankaAdapter",
    "IndustrialArmAdapter",
    "KukaAdapter",
    "UrAdapter",
    "YaskawaAdapter",
    "__version__",
]
