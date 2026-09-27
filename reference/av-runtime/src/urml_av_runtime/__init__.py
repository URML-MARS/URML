"""urml_av_runtime — autonomous-vehicle reference runtime for URML.

  AutowareAdapter (+ AutowareConfig, load_av_config)
    The Autoware Universe AD API (``autoware_adapi_v1_msgs``) backing for
    URML's AV trajectory verbs (RFC-0020): ``plan_path`` sets a route via
    ``/api/routing/set_route_points``; ``follow_trajectory`` engages
    autonomous driving via ``/api/operation_mode/change_to_autonomous``,
    under an optional published speed cap. It is the first substrate to
    implement the ``TrajectoryAdapter`` Protocol (only ``MockROSAdapter``
    did before). rclpy and the Autoware messages are imported lazily, so
    this module loads on every host, including Windows.
"""

from __future__ import annotations

from urml_av_runtime._version import __version__
from urml_av_runtime.adapter import AutowareAdapter
from urml_av_runtime.config import AutowareConfig, MapPose, load_av_config

__all__ = [
    "AutowareAdapter",
    "AutowareConfig",
    "MapPose",
    "__version__",
    "load_av_config",
]
