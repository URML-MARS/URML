"""urml_cobot_runtime — collaborative-arm reference runtime for URML.

  UrRtdeAdapter   — Universal Robots via RTDE (rtde_control/receive)
  FrankaFciAdapter — Franka via FCI (panda-py)
  (+ CobotConfig, load_cobot_config)

The two most-deployed cobots driven by their native SDKs with **zero
ROS** — the proof that the popular real arms need no ROS. The
ROS-free siblings of industrial-arm-runtime's RclpyAdapter-composed
Ur/Franka adapters, parallel to how marine-runtime is the ROS-free
sibling of ros2-runtime. Vendor SDKs are imported lazily (the
[ur]/[franka] extras), so this module loads on every host. Built
against the frozen substrate Protocol per RFC-0014; spec gaps are in
SPEC-GAPS.md, not silently patched.
"""

from __future__ import annotations

from urml_cobot_runtime._version import __version__
from urml_cobot_runtime.adapter import (
    CobotConfig,
    DoosanDrflAdapter,
    FrankaFciAdapter,
    KinovaKortexAdapter,
    TechmanTmflowAdapter,
    UrRtdeAdapter,
    load_cobot_config,
)

__all__ = [
    "CobotConfig",
    "DoosanDrflAdapter",
    "FrankaFciAdapter",
    "KinovaKortexAdapter",
    "TechmanTmflowAdapter",
    "UrRtdeAdapter",
    "__version__",
    "load_cobot_config",
]
