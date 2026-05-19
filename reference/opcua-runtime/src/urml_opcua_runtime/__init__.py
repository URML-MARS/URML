"""urml_opcua_runtime — industrial-automation reference runtime for URML.

  OpcUaAdapter (+ OpcUaConfig, load_opcua_config)
    OPC UA Robotics companion-spec robot cells via asyncua. **No ROS 2
    dependency** — the industrial-automation analog of the PX4/marine
    no-ROS proof, hitting the factory-floor / federal-procurement wedge
    (RFC-0007). asyncua is imported lazily (the [opcua] extra), so this
    module loads on every host. Built against the frozen substrate
    Protocol per RFC-0014; spec gaps are recorded in SPEC-GAPS.md, not
    silently patched.
"""

from __future__ import annotations

from urml_opcua_runtime._version import __version__
from urml_opcua_runtime.adapter import OpcUaAdapter, OpcUaConfig, load_opcua_config

__all__ = [
    "OpcUaAdapter",
    "OpcUaConfig",
    "__version__",
    "load_opcua_config",
]
