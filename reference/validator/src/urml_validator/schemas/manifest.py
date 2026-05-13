"""Layer-1 — Capability manifest schema.

A capability manifest is what a robot declares about itself: declared frames,
declared locations, mobility, manipulation, perception, docking stations, and
any declared events. The validator uses the manifest to check whether a
URML program can be executed by this robot.

Schema version: v0.1 (matches RFC-0002).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from urml_validator.schemas.common import Identifier, Pose


class Frame(BaseModel):
    """A declared coordinate frame.

    `parent` is the frame this frame is expressed relative to; the root frame
    has no parent.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    parent: Identifier | None = None


class DeclaredLocation(BaseModel):
    """A named place in the robot's world model.

    Programs reference these by name (`location: kitchen`); the validator
    resolves the reference against this list.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    pose: Pose
    frame: Identifier
    description: str | None = None


class Mobility(BaseModel):
    """Mobility capabilities declared by the robot.

    Required by `move_to`, `dock`, `hover`, `scan` (for area surveys), and
    profile-specific motion primitives. A robot without `mobility` cannot
    execute these primitives.
    """

    model_config = ConfigDict(extra="forbid")

    drive_type: Literal[
        "differential",
        "omnidirectional",
        "ackermann",
        "tracked",
        "multirotor",
        "fixed_wing",
        "vtol",
        "manipulator_base",
        "underwater_thrusters",
    ]
    max_velocity: float = Field(..., ge=0, description="Maximum velocity in m/s.")
    max_payload: float | None = Field(None, ge=0, description="Maximum payload in kg.")
    station_keeping: bool = Field(
        False,
        description=(
            "Whether the robot can actively maintain position against disturbances "
            "(required for `hover`)."
        ),
    )
    service_ceiling: float | None = Field(
        None, ge=0, description="Maximum altitude (m). Required for aerial profiles."
    )


class Gripper(BaseModel):
    """A gripper declared in the manifest's manipulation block."""

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    kind: Literal["pneumatic", "servo_electric", "vacuum", "magnetic", "compliant"]
    force_min_n: float = Field(..., ge=0)
    force_max_n: float = Field(..., gt=0)
    accepted_classes: list[Identifier] = Field(default_factory=list)
    movable: bool = True


class Manipulation(BaseModel):
    """Manipulation capabilities declared by the robot.

    Required by `grasp`, `release`. A robot without `manipulation` cannot
    execute those.
    """

    model_config = ConfigDict(extra="forbid")

    arm_count: int = Field(..., ge=0)
    grippers: list[Gripper] = Field(default_factory=list)
    reachable_workspace_m: float | None = Field(None, ge=0)


class Camera(BaseModel):
    """A camera declared in the manifest's perception block."""

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    movable: bool = False
    supports_photo: bool = True
    supports_video: bool = False
    supports_stream: bool = False
    max_resolution: str | None = None  # "1080p", "4k", ...


class Sensor(BaseModel):
    """A non-camera sensor declared in the manifest's perception block."""

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    measurement_type: Literal[
        "distance",
        "temperature",
        "weight",
        "pressure",
        "humidity",
        "depth",
        "wind_speed",
        "current",
        "voltage",
        "speech",
        "custom",
    ]
    range_min: float | None = None
    range_max: float | None = None
    units: str | None = None


class Perception(BaseModel):
    """Perception capabilities declared by the robot.

    Required by `detect`, `scan`, `measure`, `capture`, and by any
    `wait_for(condition.sensor_threshold: ...)`.
    """

    model_config = ConfigDict(extra="forbid")

    cameras: list[Camera] = Field(default_factory=list)
    sensors: list[Sensor] = Field(default_factory=list)
    object_vocabulary: list[Identifier] = Field(default_factory=list)


class DockingStation(BaseModel):
    """A declared docking station and the services it provides.

    `dock(service: ...)` is rejected by the validator unless the target
    station declares the requested service.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    pose: Pose
    frame: Identifier
    services: list[Identifier] = Field(
        default_factory=lambda: ["park"],
        description="Core: park, charge. Profile-extensible: swap_battery, "
        "swap_tool, refuel, transfer_payload, download_data, swap_consumable.",
    )


class Outputs(BaseModel):
    """Declared upstream-output channels for `report`.

    `to: user`, `to: log`, and `to: caller` are universal; custom destinations
    must be declared here.
    """

    model_config = ConfigDict(extra="forbid")

    named_endpoints: list[Identifier] = Field(default_factory=list)


class HBOMRef(BaseModel):
    """Reference to a Hardware Bill of Materials document.

    URML records the reference and an integrity hash; URML v0.1 does not parse
    SBOM/HBOM content. `format` is a free string; the recommended value is
    `cyclonedx-1.7` but any format identifier is accepted.
    """

    model_config = ConfigDict(extra="forbid")

    format: str = Field(..., description="HBOM format identifier (e.g., 'cyclonedx-1.7', 'spdx-3.0').")
    uri: str = Field(..., description="URI to the HBOM document. May be local (./hbom/x.json) or remote.")
    sha256: str | None = Field(
        None,
        description="Hex-encoded SHA-256 integrity hash. Required when uri is local; recommended otherwise.",
    )


class ProvenanceComponent(BaseModel):
    """A single declared hardware component and its origin facts.

    `role` is the load-bearing selector. Policies typically gate on critical
    components only. `country_of_origin` and `country_of_final_assembly` are
    distinct because NDAA-style rules often care about both.
    """

    model_config = ConfigDict(extra="forbid")

    id: Identifier
    role: Literal["critical", "non_critical", "informational"]
    vendor: str = Field(..., description="Machine-readable vendor identifier. Free string in v0.1.")
    country_of_origin: str = Field(
        ...,
        description="ISO 3166-1 alpha-2 country code, or 'unknown'.",
    )
    country_of_final_assembly: str = Field(
        ...,
        description="ISO 3166-1 alpha-2 country code, or 'unknown'. Often differs from country_of_origin.",
    )
    hbom_ref: HBOMRef | None = None


class Provenance(BaseModel):
    """Hardware-provenance declaration for the robot.

    Added by RFC-0003 / RFC-0004. Optional sibling of mobility/manipulation/
    perception. When present, the validator's Pass 5 evaluates a compliance
    policy against this block. When absent, Pass 5 is a no-op for the manifest.
    """

    model_config = ConfigDict(extra="forbid")

    manifest_attestation: Literal[
        "self_declared",
        "third_party_audited",
        "cryptographically_signed",
    ] = Field(
        "self_declared",
        description="Who asserts the provenance is true. Policies may require a minimum level.",
    )
    attestation_uri: str | None = Field(
        None,
        description="Optional URI to a signed attestation document.",
    )
    components: list[ProvenanceComponent] = Field(
        default_factory=list,
        description="Declared components and their per-component provenance facts.",
    )


class CapabilityManifest(BaseModel):
    """A robot's complete capability declaration.

    The top-level type the validator consumes alongside a URML program and
    a safety envelope.
    """

    model_config = ConfigDict(extra="forbid")

    manifest_version: Literal["0.1"] = "0.1"
    robot_id: Identifier
    description: str | None = None

    frames: list[Frame] = Field(default_factory=list)
    declared_locations: list[DeclaredLocation] = Field(default_factory=list)
    declared_events: list[Identifier] = Field(default_factory=list)

    mobility: Mobility | None = None
    manipulation: Manipulation | None = None
    perception: Perception | None = None

    docking_stations: list[DockingStation] = Field(default_factory=list)
    outputs: Outputs = Field(default_factory=Outputs)

    # RFC-0004: optional hardware provenance for compliance enforcement.
    provenance: Provenance | None = None
