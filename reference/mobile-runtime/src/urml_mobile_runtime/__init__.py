"""urml_mobile_runtime — wheeled-AMR reference runtime for URML.

  HuskyAdapter, JackalAdapter
    Clearpath Husky / Jackal, the canonical ROS 2 differential-drive
    research/field AMRs. Each composes the ROS 2 runtime's RclpyAdapter
    (the single-sourced-substrate pattern). rclpy is lazy inside
    RclpyAdapter, so this module loads on every host; constructing an
    adapter needs a sourced ROS 2 environment.

  ClearpathAdapter
    The shared core the brand classes subclass. Exposed for typing and
    custom-base extension.

  MOBILE_ADAPTERS
    Name → class registry ({"husky": HuskyAdapter, "jackal":
    JackalAdapter}) for config-driven selection (CI matrices, the
    conformance adapter_factory).
"""

from __future__ import annotations

from urml_mobile_runtime._version import __version__
from urml_mobile_runtime.adapter import (
    MOBILE_ADAPTERS,
    ClearpathAdapter,
    HuskyAdapter,
    JackalAdapter,
)

__all__ = [
    "MOBILE_ADAPTERS",
    "ClearpathAdapter",
    "HuskyAdapter",
    "JackalAdapter",
    "__version__",
]
