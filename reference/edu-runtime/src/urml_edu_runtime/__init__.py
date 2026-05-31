"""urml_edu_runtime — educational-platform reference runtime for URML.

  VexV5Adapter         — VEX V5 brain via host-side Python SDK.
  LegoSpikeAdapter     — LEGO SPIKE Prime / Mindstorms hub over Pybricks BLE.
  ThymioAdapter        — Thymio over the Aseba TDM (Thymio Device Manager).
  RoboticalMartyAdapter — Robotical Marty v1/v2 via the martypy skill library.
  PetoiAdapter         — Petoi Bittle X / Bittle / Nybble Q via the OpenCat skill library.
  CircuitPythonAdapter — Adafruit CircuitPython (Python on MCU) via a host-side comms bridge.
  (+ EduConfig, BRAND_ADAPTERS, load_edu_config)

The classroom/maker adoption flywheel (RFC-0011). Each platform's
native SDK is imported lazily by its adapter (the marine/cobot
posture), so this module loads on every host without any [vex]/[lego]/
[thymio]/[marty] extra. Built against the frozen substrate Protocol per
RFC-0014; SPEC-GAPS.md cross-references RFC-0017 (LED/buzzer/button =
digital-IO) and RFC-0018 (non-mobile minimal node). No new RFC.

The Marty adapter is URML's first shipping adapter built in response to
an engaged outreach reply (RFC-0073 + robotical/martypy#52, 2026-05-25).
"""

from __future__ import annotations

from urml_edu_runtime._version import __version__
from urml_edu_runtime.adapter import (
    CircuitPythonAdapter,
    EduCommand,
    EduConfig,
    EduSkillCall,
    LegoSpikeAdapter,
    PetoiAdapter,
    RoboticalMartyAdapter,
    ThymioAdapter,
    VexV5Adapter,
    load_edu_config,
)

BRAND_ADAPTERS = {
    "vex": VexV5Adapter,
    "lego_spike": LegoSpikeAdapter,
    "thymio": ThymioAdapter,
    "marty": RoboticalMartyAdapter,
    "petoi": PetoiAdapter,
    "circuitpython": CircuitPythonAdapter,
}

__all__ = [
    "BRAND_ADAPTERS",
    "CircuitPythonAdapter",
    "EduCommand",
    "EduConfig",
    "EduSkillCall",
    "LegoSpikeAdapter",
    "PetoiAdapter",
    "RoboticalMartyAdapter",
    "ThymioAdapter",
    "VexV5Adapter",
    "__version__",
    "load_edu_config",
]
