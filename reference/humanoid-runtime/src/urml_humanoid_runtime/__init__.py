"""urml_humanoid_runtime — humanoid reference runtime for URML.

  DigitAdapter
    Agility Robotics Digit, a ROS 2 bipedal humanoid. Composes the ROS 2
    runtime's RclpyAdapter (the single-sourced-substrate pattern). v0.1
    covers the locomotion subset; whole-body/bimanual manipulation is a
    future RFC. rclpy is lazy inside RclpyAdapter, so this module loads
    on every host.

  HUMANOID_ADAPTERS
    Name → class registry ({"digit": DigitAdapter}) for config-driven
    selection (CI matrices, the conformance adapter_factory).

Agility Digit is the one humanoid on the multi-brand list with a usable
public SDK + sim, so it is the only one with an adapter. Tesla Optimus,
Figure, Apptronik Apollo and 1X NEO have no public SDK; per the plan
they are covered manifest + spec only, landing with the Phase-5
Mobility.drive_type RFC (a humanoid manifest cannot validate until that
schema gap is closed). No adapter is written for them — that would be
code with nothing to run against.
"""

from __future__ import annotations

from urml_humanoid_runtime._version import __version__
from urml_humanoid_runtime.digit import DigitAdapter

HUMANOID_ADAPTERS: dict[str, type] = {
    "digit": DigitAdapter,
}

__all__ = [
    "HUMANOID_ADAPTERS",
    "DigitAdapter",
    "__version__",
]
