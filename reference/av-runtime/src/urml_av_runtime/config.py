"""Deployment-side configuration for the Autoware AV adapter.

Which WGS84/map pose a manifest-declared location (``depot``, ``dropoff``)
resolves to, and which Autoware AD API service / topic names to drive, is
deployment-specific, so it lives here rather than in the URML
program/manifest/envelope (the ros2 / px4 / ardupilot ``location_to_*``
precedent).

The defaults track the documented Autoware Universe AD API
(``autoware_adapi_v1_msgs``): routing via ``/api/routing/set_route_points``,
actuation via ``/api/operation_mode/change_to_autonomous``, and a speed cap
published to the scenario-planning ``max_velocity`` topic. Every name is
overridable so the adapter tracks a specific Autoware release without a code
change.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class MapPose(BaseModel):
    """A goal pose in the map frame. ``yaw`` is the heading in radians."""

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    z: float = 0.0
    yaw: float = 0.0


class AutowareConfig(BaseModel):
    """Connection + AD API binding config for :class:`AutowareAdapter`."""

    model_config = ConfigDict(extra="forbid")

    ros2_namespace: str = Field(default="", description="ROS 2 namespace for the adapter node.")
    node_name: str = Field(default="urml_av_adapter", description="Node name the adapter creates.")
    map_frame: str = Field(default="map", description="Frame id stamped on the route goal.")

    location_to_pose: dict[str, MapPose] = Field(
        default_factory=dict,
        description="Map manifest-declared location names (depot, dropoff, ...) to map-frame poses.",
    )

    # AD API surface (autoware_adapi_v1_msgs). Overridable per Autoware release.
    set_route_service: str = "/api/routing/set_route_points"
    clear_route_service: str = "/api/routing/clear_route"
    change_to_autonomous_service: str = "/api/operation_mode/change_to_autonomous"
    set_route_srv_type: str = "autoware_adapi_v1_msgs.srv:SetRoutePoints"
    clear_route_srv_type: str = "autoware_adapi_v1_msgs.srv:ClearRoute"
    change_mode_srv_type: str = "autoware_adapi_v1_msgs.srv:ChangeOperationMode"

    # Speed cap: a latched VelocityLimit publish, since the AD API has no
    # per-call velocity-limit service across releases.
    velocity_limit_topic: str = "/planning/scenario_planning/max_velocity"
    velocity_limit_msg_type: str = "tier4_planning_msgs.msg:VelocityLimit"

    clear_route_before_plan: bool = Field(
        default=True,
        description="Clear any existing route before setting a new one (idempotent planning).",
    )
    service_timeout_seconds: float = Field(default=10.0, gt=0)

    def resolve_pose(self, name: str) -> MapPose | None:
        return self.location_to_pose.get(name)


def load_av_config(path: str | Path) -> AutowareConfig:
    """Parse an ``av_adapter.yaml`` file into an :class:`AutowareConfig`."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"av-config file {p} did not contain a YAML mapping at the top level.")
    return AutowareConfig.model_validate(data)
