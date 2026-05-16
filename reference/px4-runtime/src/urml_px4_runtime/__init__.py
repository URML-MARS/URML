"""urml_px4_runtime — PX4 / MAVLink reference runtime for URML.

Public API:

  PX4Adapter(config)
    Real MAVLink adapter via pymavlink. Implements the same ROSAdapter
    Protocol as the ROS 2 runtime's RclpyAdapter — substrate-neutral by
    design. pymavlink is imported lazily so this module loads on every
    host; constructing the adapter without pymavlink raises a clear,
    actionable error.

  PX4AdapterConfig
    Connection + identity config (URL, system_id, component_id, default
    timeouts). Loaded from YAML via load_px4_config(path).

  CompositeAdapter(flight=..., companion=..., routing=None)
    Routes one URML program across two substrates — a PX4 flight
    adapter and a ROS 2 companion adapter — by dispatching each
    ROSAdapter method to whichever backend owns that capability.
    Imports neither pymavlink nor rclpy; loads on every host.
"""

from __future__ import annotations

from urml_px4_runtime._version import __version__
from urml_px4_runtime.adapter import PX4Adapter
from urml_px4_runtime.composite import COMPANION, FLIGHT, CompositeAdapter
from urml_px4_runtime.config import PX4AdapterConfig, load_px4_config

__all__ = [
    "COMPANION",
    "FLIGHT",
    "CompositeAdapter",
    "PX4Adapter",
    "PX4AdapterConfig",
    "__version__",
    "load_px4_config",
]
