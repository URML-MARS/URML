"""urml_isaac_runtime — simulator reference runtime for URML.

  IsaacAdapter (+ IsaacConfig, load_isaac_config)
    NVIDIA Isaac Sim physics via the official Apache-2.0 ``isaacsim`` wheel. **No
    ROS 2 dependency** — the purest substrate-neutrality acid-test
    proof: a simulator faithfully implementing the frozen substrate
    Protocol with zero ROS, headless and offline. ``isaacsim`` is
    imported lazily (the [sim] extra), so this module loads on every
    host.
"""

from __future__ import annotations

from urml_isaac_runtime._version import __version__
from urml_isaac_runtime.adapter import IsaacAdapter, IsaacConfig, load_isaac_config

__all__ = [
    "IsaacAdapter",
    "IsaacConfig",
    "__version__",
    "load_isaac_config",
]
