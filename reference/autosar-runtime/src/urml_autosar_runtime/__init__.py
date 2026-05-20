"""urml_autosar_runtime — industrial-automation reference runtime for URML.

  AutosarAdaptiveAdapter (+ AutosarConfig, load_autosar_config)
    AUTOSAR Adaptive companion-spec robot cells via ara. **No ROS 2
    dependency** — the industrial-automation analog of the PX4/marine
    no-ROS proof, hitting the factory-floor / federal-procurement wedge
    (RFC-0007). ara is imported lazily (the [autosar] extra), so this
    module loads on every host. Built against the frozen substrate
    Protocol per RFC-0014; spec gaps are recorded in SPEC-GAPS.md, not
    silently patched.
"""

from __future__ import annotations

from urml_autosar_runtime._version import __version__
from urml_autosar_runtime.adapter import AutosarAdaptiveAdapter, AutosarConfig, load_autosar_config

__all__ = [
    "AutosarAdaptiveAdapter",
    "AutosarConfig",
    "__version__",
    "load_autosar_config",
]
