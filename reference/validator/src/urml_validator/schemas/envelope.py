"""Safety envelope schema.

The envelope declares the limits a deployment imposes on top of (and never
weaker than) what the capability manifest declares. The envelope is a
deployment-time policy artifact: same robot, two deployments, different
envelopes.

The validator applies the *strictest* of envelope, manifest, and profile-
default constraints. Envelope cannot relax — only tighten.
"""

from __future__ import annotations

from typing import Literal

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


class MonitorableProperty(BaseModel):
    """A runtime-monitorable temporal property (RFC-0382).

    The static envelope checks numeric caps and spatial constraints once,
    before dispatch. A monitorable property is a time-varying property a
    runtime monitor enforces during execution: "speed stays under 0.3
    whenever person_distance is below 2.0", "the robot stops within 500 ms of
    a stop request". URML declares it in a small closed temporal-logic core
    over signals the manifest and envelope already declare; the validator
    checks the expression parses and references only declared signals, and a
    backend (RTAMT, Reelay, Copilot, MoonLight) compiles and runs it. URML
    does not run the monitor.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    severity: Literal["info", "warning", "critical"] = Field(
        "warning",
        description="How a downstream monitor treats a violation. Advisory to URML.",
    )
    dialect: Literal["stl", "stl_strel", "custom"] = Field(
        "stl",
        description="Temporal-logic dialect the expression is written in. `custom` is carried verbatim.",
    )
    expression: str = Field(
        ...,
        min_length=1,
        description="The property in the declared dialect (see urml_validator.monitorable for the core grammar).",
    )
    signals: list[Identifier] = Field(
        default_factory=list,
        description="Optional explicit signal list; when omitted the validator infers signals from the expression.",
    )


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

    # RFC-0382: runtime-monitorable temporal properties. Declared here, parsed
    # and signal-checked by the validator, compiled + enforced by a monitor
    # backend. URML does not run the monitor.
    monitorable_properties: list[MonitorableProperty] = Field(default_factory=list)
