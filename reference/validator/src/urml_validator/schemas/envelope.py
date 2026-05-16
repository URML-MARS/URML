"""Safety envelope schema.

The envelope declares the limits a deployment imposes on top of (and never
weaker than) what the capability manifest declares. The envelope is a
deployment-time policy artifact: same robot, two deployments, different
envelopes.

The validator applies the *strictest* of envelope, manifest, and profile-
default constraints. Envelope cannot relax — only tighten.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from urml_validator.schemas.common import Identifier
from urml_validator.schemas.connectivity import LinkLossRule


class GeofencePolygon(BaseModel):
    """A 2D polygon (footprint) optionally bounded above and below by altitude.

    Coordinates are expressed in the frame named by `frame`. The robot
    must stay inside the polygon's footprint AND (when set) within the
    declared altitude band. ``min_altitude`` and ``max_altitude`` are
    independent — supply only the bounds the deployment actually needs.

    Altitudes are in the frame's altitude reference (typically meters AGL
    for `agl` frames). The validator treats containment as inclusive at
    both bounds (a point exactly at `max_altitude` is inside).
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    frame: Identifier
    vertices: list[tuple[float, float]] = Field(..., min_length=3)
    min_altitude: float | None = Field(
        None,
        description="Lower altitude bound (inclusive). When omitted, no floor is enforced.",
    )
    max_altitude: float | None = Field(
        None,
        ge=0,
        description="Upper altitude bound (inclusive). When omitted, no ceiling is enforced.",
    )


class WeatherThresholds(BaseModel):
    """Operational weather limits, primarily for aerial profiles."""

    model_config = ConfigDict(extra="forbid")

    max_wind_m_per_s: float | None = Field(None, ge=0)
    min_visibility_m: float | None = Field(None, ge=0)
    allow_precipitation: bool = False


class PeopleOccupancyZone(BaseModel):
    """A zone where people are expected.

    Default behaviour: programs that would direct the robot through such a
    zone are rejected unless the deployment explicitly opts in via the manifest.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    frame: Identifier
    vertices: list[tuple[float, float]] = Field(..., min_length=3)
    allow_override: bool = False


class SafetyEnvelope(BaseModel):
    """A complete deployment-time safety envelope."""

    model_config = ConfigDict(extra="forbid")

    envelope_version: str = "0.1"
    deployment_id: Identifier | None = None
    description: str | None = None

    # Numeric caps (apply strictly atop manifest defaults; "None" = no envelope override).
    max_velocity: float | None = Field(None, ge=0)
    max_altitude: float | None = Field(None, ge=0)
    max_payload: float | None = Field(None, ge=0)
    max_grip_force_n: float | None = Field(None, ge=0)

    # Spatial constraints.
    geofences: list[GeofencePolygon] = Field(default_factory=list)
    people_occupancy_zones: list[PeopleOccupancyZone] = Field(default_factory=list)

    # Environmental.
    weather: WeatherThresholds | None = None

    # RFC-0006: structured, validated loss-of-communication policy.
    # Replaces the old free-form `link_loss_policy: str | None`. Each rule
    # governs one abstract link role; the validator checks each rule's action
    # is coherent with the manifest (Pass 2 + Pass 3).
    link_loss_policy: list[LinkLossRule] = Field(default_factory=list)
