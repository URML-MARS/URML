"""Deployment-side configuration for the cobot adapters.

A cobot is driven to *poses*. Which Cartesian/joint vector a
manifest-declared location name maps to is robot- and cell-specific,
so it does NOT belong in the URML program/manifest/envelope — it lives
in a ``cobot_adapter.yaml`` (the same principle as the PX4 runtime's
``location_to_pose`` and the marine runtime's ``location_to_waypoint``).
This is the documented home for joint-space waypoints (SPEC-GAPS item
E): a named location resolves to a 6-DoF pose here, no URML surface
change needed.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Pose(BaseModel):
    """A target pose vector. For UR: TCP pose [x,y,z,rx,ry,rz]. For Franka: joint or pose vector."""

    model_config = ConfigDict(extra="forbid")

    vector: list[float] = Field(default_factory=list, description="Robot-native pose/joint vector.")


class CobotConfig(BaseModel):
    """Connection + pose-mapping config shared by the UR and Franka adapters."""

    model_config = ConfigDict(extra="forbid")

    robot_ip: str = Field(
        default="127.0.0.1",
        description="Robot controller IP. UR: the CB/e-Series controller. Franka: the FCI host (FCI must be enabled).",
    )
    speed: float = Field(default=0.25, gt=0.0, description="Default linear/joint speed fraction or m/s.")
    location_to_pose: dict[str, Pose] = Field(default_factory=dict)

    def resolve_location(self, name: str) -> Pose | None:
        """Return the pose for a named location, or None if unmapped (returned, not raised)."""
        return self.location_to_pose.get(name)


def load_cobot_config(path: str | Path) -> CobotConfig:
    """Parse a ``cobot_adapter.yaml`` file into a ``CobotConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"cobot-config file {p} did not contain a YAML mapping at the top level.")
    return CobotConfig.model_validate(data)
