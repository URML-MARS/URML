"""urml_marine_runtime — underwater-vehicle reference runtime for URML.

  BlueRovAdapter (+ MarineConfig, load_marine_config)
    BlueROV2 / ArduSub via MAVLink (pymavlink). No ROS 2 dependency —
    the underwater analog of PX4Adapter's no-ROS proof. Activates the
    `underwater_thrusters` mobility.drive_type (already in the v0.1
    schema). pymavlink is imported lazily (the [marine] extra), so this
    module loads on every host.
"""

from __future__ import annotations

from urml_marine_runtime._version import __version__
from urml_marine_runtime.adapter import BlueRovAdapter, MarineConfig, load_marine_config

__all__ = [
    "BlueRovAdapter",
    "MarineConfig",
    "__version__",
    "load_marine_config",
]
