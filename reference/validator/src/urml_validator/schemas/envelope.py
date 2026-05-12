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


class GeofencePolygon(BaseModel):
    """A polygon outside which the robot refuses to move.

    Coordinates are expressed in the frame named by `frame`.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    frame: Identifier
    vertices: list[tuple[float, float]] = Field(..., min_length=3)


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

    # Loss-of-communication policy (aerial: return to home; ground: halt; etc.).
    link_loss_policy: str | None = None  # free-form for now; tightened later
