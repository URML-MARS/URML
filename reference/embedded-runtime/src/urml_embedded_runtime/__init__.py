"""urml_embedded_runtime — educational-MCU reference runtime for URML.

  EmbeddedAdapter (+ EmbeddedConfig, load_embedded_config)
    micro:bit / Arduino-class platforms over a plain serial line.
    **No ROS 2 dependency** — URML scales DOWN to a microcontroller,
    serving the educational flywheel (RFC-0011). pyserial is imported
    lazily (the [serial] extra), so this module loads on every host.
    Built against the frozen substrate Protocol per RFC-0014; the
    minimal-MCU manifest gap is recorded in SPEC-GAPS.md (RFC-0018),
    not silently patched.
"""

from __future__ import annotations

from urml_embedded_runtime._version import __version__
from urml_embedded_runtime.adapter import (
    EmbeddedAdapter,
    EmbeddedConfig,
    load_embedded_config,
)

__all__ = [
    "EmbeddedAdapter",
    "EmbeddedConfig",
    "__version__",
    "load_embedded_config",
]
