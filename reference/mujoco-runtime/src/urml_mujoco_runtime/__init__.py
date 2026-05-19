"""urml_mujoco_runtime — simulator reference runtime for URML.

  MujocoAdapter (+ MujocoConfig, load_mujoco_config)
    MuJoCo physics via the official Apache-2.0 ``mujoco`` wheel. **No
    ROS 2 dependency** — the purest substrate-neutrality acid-test
    proof: a simulator faithfully implementing the frozen substrate
    Protocol with zero ROS, headless and offline. ``mujoco`` is
    imported lazily (the [sim] extra), so this module loads on every
    host.
"""

from __future__ import annotations

from urml_mujoco_runtime._version import __version__
from urml_mujoco_runtime.adapter import MujocoAdapter, MujocoConfig, load_mujoco_config

__all__ = [
    "MujocoAdapter",
    "MujocoConfig",
    "__version__",
    "load_mujoco_config",
]
