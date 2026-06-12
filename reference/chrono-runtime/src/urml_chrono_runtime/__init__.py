"""urml_chrono_runtime — high-fidelity validation runtime for URML.

  ChronoAdapter (+ ChronoConfig, load_chrono_config)
    Project Chrono multibody / multi-physics via PyChrono. **No ROS 2
    dependency.** Chrono is the high-fidelity *validation* target: a
    URML program is checked statically against the capability manifest
    and safety envelope first, then the same validated intent is driven
    through a short Chrono simulation segment and the dynamics (system
    time, contacts, the commanded driver inputs) come back as evidence.
    ``pychrono`` is imported lazily (it ships via conda-forge), so this
    module loads on every host without it.
"""

from __future__ import annotations

from urml_chrono_runtime._version import __version__
from urml_chrono_runtime.adapter import ChronoAdapter, ChronoConfig, load_chrono_config
from urml_chrono_runtime.terramechanics import TerramechanicsParams, TerramechanicsScene

__all__ = [
    "ChronoAdapter",
    "ChronoConfig",
    "TerramechanicsParams",
    "TerramechanicsScene",
    "__version__",
    "load_chrono_config",
]
