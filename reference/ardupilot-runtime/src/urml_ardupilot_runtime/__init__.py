"""urml_ardupilot_runtime — ArduPilot / MAVLink reference runtime for URML.

Public API:

  ArduCopterAdapter(config)
    MAVLink adapter for ArduCopter (Pixhawk-class boards running ArduPilot,
    or ArduCopter SITL). Subclasses the PX4 reference adapter and adds the
    ArduPilot-specific preamble that PX4 does not need: GUIDED mode entry,
    explicit arming, ack filtering by command id, arrival waits, global
    (WGS84) setpoints, camera trigger, and output lines (gripper, winch,
    servo). pymavlink is imported lazily so this module loads everywhere.

  ArduPilotAdapterConfig
    Connection + identity + location bindings. Loaded from YAML via
    load_ardupilot_config(path).

  probe(config)
    Read-only identity snapshot of the connected autopilot. Also exposed as
    ``python -m urml_ardupilot_runtime.probe COM5``.
"""

from __future__ import annotations

from urml_ardupilot_runtime._version import __version__
from urml_ardupilot_runtime.adapter import ArduCopterAdapter, probe
from urml_ardupilot_runtime.config import (
    ArduPilotAdapterConfig,
    CameraTrigger,
    GlobalPosition,
    OutputLineBinding,
    load_ardupilot_config,
)

__all__ = [
    "ArduCopterAdapter",
    "ArduPilotAdapterConfig",
    "CameraTrigger",
    "GlobalPosition",
    "OutputLineBinding",
    "__version__",
    "load_ardupilot_config",
    "probe",
]
