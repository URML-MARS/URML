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
from urml_validator.schemas.connectivity import Connectivity


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


class OperationalClearance(BaseModel):
    """The robot's operational-volume buffer for fleet deconfliction (RFC-0287).

    Models a UTM operational volume (ASTM F3548 Volume3D) as a buffer around the
    robot's target: a lateral footprint circle of ``radius_m`` and a vertical band
    of ``±vertical_m`` (altitude for aerial robots, depth for underwater robots,
    a thin ground band otherwise). Two members conflict only if their volumes
    intersect both laterally and vertically within a shared frame and the same
    medium; a `barrier` separates them in time.

    Optional: a robot without `clearance` falls back to name-based comparison.
    Forward path: asymmetric ``vertical_up_m`` / ``vertical_down_m`` and a polygon
    footprint are additive future fields — circle + symmetric band is the v0.1 minimal.
    """

    model_config = ConfigDict(extra="forbid")

    radius_m: float = Field(..., gt=0, description="Lateral footprint radius (m).")
    vertical_m: float = Field(
        ..., gt=0, description="Vertical half-band (m): altitude (air) / depth (water)."
    )


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
        "quadruped",  # RFC-0009: four-legged platforms (Spot, ANYmal, Vision 60)
        "biped",  # RFC-0009: bipedal/humanoid locomotion (Digit, Optimus, Apollo, NEO)
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
    clearance: OperationalClearance | None = Field(
        None,
        description=(
            "Operational-volume buffer for fleet collision deconfliction (RFC-0287). "
            "Optional; absent means name-based fallback for pairs involving this robot."
        ),
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
    """A non-camera sensor declared in the manifest's perception block.

    URML's Sensor block declares **what the sensor can do**, not what a
    deployment configures it to do. Fields like `beam_count`, `channels`,
    `time_sync_methods`, and `rate_hz_max` are capability declarations
    (RFC-0039); runtime substrates (Ouster's `LidarMode` + `UDPLidarProfile`,
    ROS 2 driver parameters, vendor-specific configuration files) pick the
    active mode at deployment time.
    """

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
        "point_cloud",       # RFC-0039: 3D lidars and similar multi-channel sensors.
        "custom",
    ]
    range_min: float | None = None
    range_max: float | None = None
    units: str | None = None

    # RFC-0039 additions (v0.2 Sensor schema iteration). All optional and
    # additive; existing manifests validate unchanged.
    beam_count: int | None = Field(
        default=None,
        ge=1,
        description="Vertical beam count for lidar-class sensors. SKU-fixed.",
    )
    channels: list[str] | None = Field(
        default=None,
        description=(
            "Data channels the sensor publishes (free-form list; conventional "
            "lidar values: range, intensity, reflectivity, near_ir)."
        ),
    )
    time_sync_methods: list[str] | None = Field(
        default=None,
        description=(
            "Capability list of supported timestamping methods (free-form; "
            "conventional values: ptp, nmea, ieee_1588, ntp). URML declares "
            "the supported set; the substrate driver selects one."
        ),
    )
    rate_hz_max: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Declared sample-rate ceiling in Hz. Substrate drivers may "
            "configure the sensor below this ceiling at deployment time."
        ),
    )


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


class ProgramArg(BaseModel):
    """A single declared argument of a substrate program.

    The `type` is one of the three URML scalar kinds. The validator uses the
    declared name and type to capability-check a `call_program`'s `args` before
    execution (RFC-0015 Pass-2 check). Depth stops at scalar typing by design.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    type: Literal["string", "number", "boolean"]


class Program(BaseModel):
    """A substrate-defined program/method the robot exposes by name.

    Added by RFC-0015. A `call_program` step is rejected by the validator
    unless its `name` is declared here, preserving validate-before-actuate even
    though the program body is opaque to URML. `call_program` is the
    substrate-specific last resort, not a substitute for modelling a behavior
    with real primitives; a manifest only declares `programs:` when the
    substrate genuinely exposes named routines (e.g. a Kawasaki AS-language
    program, an OPC UA method node, a commissioned PLC job).
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    description: str | None = None
    args: list[ProgramArg] = Field(
        default_factory=list,
        description="Declared argument signature. Empty means the program takes no arguments.",
    )


class QosProfile(BaseModel):
    """DDS QoS profile declaration (RFC-0251).

    Used inside `Substrate.rmw_options.qos_profile` to declare the
    deployment-wide QoS that the ROS 2 RMW layer applies. The fields mirror
    OMG DDS QoS policies: reliability, durability, history (with depth when
    keep_last), deadline, lifespan. All fields are optional individually;
    when `history: keep_last` is declared, `history_depth` is required.
    """

    model_config = ConfigDict(extra="forbid")

    reliability: Literal["reliable", "best_effort"] | None = None
    durability: Literal["volatile", "transient_local", "transient", "persistent"] | None = None
    history: Literal["keep_last", "keep_all"] | None = None
    history_depth: int | None = Field(default=None, ge=1)
    deadline_ms: int | None = Field(default=None, ge=0)
    lifespan_ms: int | None = Field(default=None, ge=0)


class RmwOptions(BaseModel):
    """ROS 2 RMW options declaration (RFC-0251).

    Used inside `Substrate.rmw_options` to declare deployment-wide DDS / RMW
    configuration: the default QoS profile, the discovery topology, and an
    optional substrate-specific config-file reference. The fields are
    informational at validate time (URML's no-cloud invariant honors the
    config_reference as opaque documentation), but the runtime adapter
    consumes them at dispatch time.
    """

    model_config = ConfigDict(extra="forbid")

    qos_profile: QosProfile | None = None
    discovery_topology: Literal[
        "simple",
        "discovery_server",
        "xml_configured",
        "peer",
        "client",
        "router",
    ] | None = None
    config_reference: str | None = Field(
        default=None,
        description=(
            "RMW-specific config file path (e.g. CycloneDDS XML, Fast DDS "
            "profiles XML). Opaque to the validator; documentation for "
            "downstream tooling."
        ),
    )


class Substrate(BaseModel):
    """Substrate-class declarations beneath URML's runtime.

    Added by RFC-0250 (autopilot_class). Extended by RFC-0251 with
    rmw_implementation + rmw_options. Future RFCs in the 0252-0285 range
    will add additional fields (ipc_substrate, maturity_tier, bridges,
    etc.).

    Validator rules currently enforced:
    - RFC-0250: drone-class drive_type requires autopilot_class; custom
      requires autopilot_class_note.
    - RFC-0251: rmw_implementation == 'custom' requires
      rmw_implementation_note; qos_profile.history == 'keep_last' requires
      history_depth (also enforced by QosProfile's own constraints).
    """

    model_config = ConfigDict(extra="forbid")

    autopilot_class: Literal["px4", "ardupilot", "pixhawk_classic", "custom"] | None = Field(
        default=None,
        description=(
            "Drone-autopilot substrate class. Required when "
            "mobility.drive_type is multirotor / fixed_wing / vtol."
        ),
    )
    autopilot_class_note: str | None = Field(
        default=None,
        description="Required when autopilot_class is 'custom'. Free-text description of the autopilot stack.",
    )

    # RFC-0251 additions: ROS 2 RMW implementation and QoS / discovery
    # options. Both are optional in the v0.1 schema; the
    # "required-when-class==ros2" rule from the RFC is deferred until a
    # `substrate.class` field exists (no such field in v0.1).
    rmw_implementation: Literal[
        "rmw_fastrtps_cpp",
        "rmw_cyclonedds_cpp",
        "rmw_zenoh_cpp",
        "rmw_connextdds",
        "custom",
    ] | None = Field(
        default=None,
        description=(
            "ROS 2 RMW implementation. Closed enum; `custom` requires "
            "`rmw_implementation_note`. Per RFC-0251."
        ),
    )
    rmw_implementation_note: str | None = Field(
        default=None,
        description="Required when rmw_implementation is 'custom'. Free-text description of the RMW stack.",
    )
    rmw_options: RmwOptions | None = None


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

    # RFC-0015: optional substrate-program declarations for `call_program`.
    programs: list[Program] = Field(default_factory=list)

    docking_stations: list[DockingStation] = Field(default_factory=list)
    outputs: Outputs = Field(default_factory=Outputs)

    # RFC-0004: optional hardware provenance for compliance enforcement.
    provenance: Provenance | None = None

    # RFC-0006: optional abstract connectivity capability.
    connectivity: Connectivity | None = None

    # RFC-0250: optional substrate-class declarations (autopilot, RMW, IPC, etc.).
    substrate: Substrate | None = None
