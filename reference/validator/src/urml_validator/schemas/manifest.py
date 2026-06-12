"""Layer-1 — Capability manifest schema.

A capability manifest is what a robot declares about itself: declared frames,
declared locations, mobility, manipulation, perception, docking stations, and
any declared events. The validator uses the manifest to check whether a
URML program can be executed by this robot.

Schema version: v0.1 (matches RFC-0002).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from urml_validator.schemas.common import Identifier, Pose, Transform
from urml_validator.schemas.connectivity import Connectivity


class Frame(BaseModel):
    """A declared coordinate frame.

    `parent` is the frame this frame is expressed relative to; the root frame
    has no parent. `transform` (RFC-0290) is this frame's pose *in its parent*:
    a point `p` here maps to the parent as `R·p + t`. With transforms declared
    up the parent chain, the validator can express any pose in any connected
    frame (cross-frame geometry). A frame with a `parent` but no `transform` is
    not numerically related to it — checks that would need the relation abstain.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    parent: Identifier | None = None
    transform: Transform | None = None


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
    """The robot's operational-volume buffer for fleet deconfliction (RFC-0291).

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
            "Operational-volume buffer for fleet collision deconfliction (RFC-0291). "
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


class Arm(BaseModel):
    """A named arm in a multi-arm manipulator (RFC-0010).

    The optional, richer form of `arm_count`: declares each arm by name and
    binds it to a declared gripper, so the validator can check that an
    addressed `grasp(arm: ...)` / `release(arm: ...)` / `bimanual` references
    an arm that exists and resolve the force/accepted-classes check against
    that arm's gripper. `arm_count` is retained; `arms` is optional and, when
    present, SHOULD have `len(arms) == arm_count`.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    gripper_ref: Identifier


class Manipulation(BaseModel):
    """Manipulation capabilities declared by the robot.

    Required by `grasp`, `release`, `bimanual`. A robot without `manipulation`
    cannot execute those.
    """

    model_config = ConfigDict(extra="forbid")

    arm_count: int = Field(..., ge=0)
    grippers: list[Gripper] = Field(default_factory=list)
    reachable_workspace_m: float | None = Field(None, ge=0)
    arms: list[Arm] = Field(
        default_factory=list,
        description=(
            "Optional per-arm declaration (RFC-0010). Each arm has a `name` and "
            "a `gripper_ref` into `grippers`. Absent means arms are anonymous and "
            "`arm_count` alone bounds multi-arm addressing."
        ),
    )

    @model_validator(mode="after")
    def _arms_are_consistent(self) -> Manipulation:
        """Each declared arm's `gripper_ref` must resolve to a declared gripper,
        and arm names must be unique (RFC-0010 manifest integrity)."""
        if not self.arms:
            return self
        gripper_names = {g.name for g in self.grippers}
        seen: set[str] = set()
        for arm in self.arms:
            if arm.name in seen:
                raise ValueError(f"manipulation.arms has duplicate arm name {arm.name!r}")
            seen.add(arm.name)
            if arm.gripper_ref not in gripper_names:
                raise ValueError(
                    f"manipulation.arms[{arm.name!r}].gripper_ref {arm.gripper_ref!r} "
                    f"is not a declared gripper (declared: {sorted(gripper_names)!r})"
                )
        return self


class Point2(BaseModel):
    """A 2-D point (metres) in the robot's body frame (RFC-0384).

    Used for `whole_body.support_polygon` vertices.
    """

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class Point3(BaseModel):
    """A 3-D point (metres) in the robot's body frame (RFC-0384).

    Used for `whole_body.center_of_mass`.
    """

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    z: float


class KinematicChain(BaseModel):
    """One kinematic chain (limb) of a whole-body robot (RFC-0384).

    A declarative structural element, not a dynamics model: it names a limb,
    classifies it, and states its degrees of freedom. An `arm` chain MAY bind
    to a declared `manipulation.arms[].name` via `arm_ref` so the whole-body
    structure and the manipulation surface stay consistent.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    kind: Literal["leg", "arm", "torso", "head", "other"]
    dof: int = Field(..., ge=1, description="Degrees of freedom in this chain.")
    arm_ref: Identifier | None = Field(
        None,
        description=(
            "For kind=arm: the `manipulation.arms[].name` this chain realizes "
            "(RFC-0010). Resolved by the validator."
        ),
    )


class WholeBody(BaseModel):
    """Whole-body kinematic structure and stability limits (RFC-0384).

    The capability shape of a legged / humanoid robot: which limbs it has, and
    the static stability envelope a request is validated against. URML declares
    these as structure and limits; realizing balance is the substrate's job
    (the RFC-0010 line). Every field is a static declaration, not live state.

    The richer stability fields (`center_of_mass`, `support_polygon`,
    `max_tilt_deg`) are declarations the validator checks statically (a declared
    center of mass must lie within the declared support polygon); they are not a
    runtime controller model.
    """

    model_config = ConfigDict(extra="forbid")

    chains: list[KinematicChain] = Field(
        default_factory=list,
        description="The robot's kinematic chains (legs, arms, torso, head).",
    )
    static_stable: bool = Field(
        True,
        description=(
            "Whether the robot can hold a static pose without continuously "
            "stepping/balancing. False means it must keep moving to stay upright."
        ),
    )
    can_carry_while_moving: bool = Field(
        True,
        description="Whether the platform can locomote while holding a payload.",
    )
    max_incline_deg: float | None = Field(
        None, ge=0, le=90,
        description="Steepest ground incline (degrees) the platform can traverse.",
    )
    max_tilt_deg: float | None = Field(
        None, ge=0, le=90,
        description="Maximum body tilt (degrees) the platform tolerates while stable.",
    )
    center_of_mass: Point3 | None = Field(
        None,
        description="Nominal center of mass in the body frame (m). Static declaration.",
    )
    support_polygon: list[Point2] | None = Field(
        None,
        description=(
            "Nominal support footprint as a polygon of body-frame vertices (m). "
            "With `center_of_mass`, the validator checks static stability "
            "(the CoM must lie within the polygon)."
        ),
    )

    @model_validator(mode="after")
    def _well_formed(self) -> WholeBody:
        """Intra-block integrity: unique chain names, `arm_ref` only on arms, and
        a support polygon (when present) needs at least three vertices. Cross-block
        rules (leg count vs drive_type, arm_ref resolution, CoM-in-polygon) carry
        stable error codes and live in the validator (RFC-0384)."""
        seen: set[str] = set()
        for chain in self.chains:
            if chain.name in seen:
                raise ValueError(f"whole_body.chains has duplicate chain name {chain.name!r}")
            seen.add(chain.name)
            if chain.kind != "arm" and chain.arm_ref is not None:
                raise ValueError(
                    f"whole_body.chains[{chain.name!r}] sets arm_ref but kind is "
                    f"{chain.kind!r}, not 'arm'"
                )
        if self.support_polygon is not None and len(self.support_polygon) < 3:
            raise ValueError("whole_body.support_polygon needs at least 3 vertices")
        return self


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


class OutputLine(BaseModel):
    """A declared digital or analog output line for `set_output` (RFC-0017).

    Models the large class of end-effectors and cell signals that are *just a
    line write*: a glue dispenser, a vacuum solenoid, a paint trigger, an ag
    spot-sprayer relay, an MCU GPIO, a "cycle done" PLC handshake. The line is
    declared here so the validator rejects an undeclared line and refuses a
    value outside the declared range *before* anything actuates. `safe_state`
    is the value the line rests at / auto-reverts to after a pulse.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    kind: Literal["digital", "analog"]
    range: tuple[float, float] | None = Field(
        None,
        description="Closed [min, max] for an analog line. Required for `analog`, omitted for `digital`.",
    )
    safe_state: bool | float = Field(
        ...,
        description="Rest / auto-revert value. bool for a digital line; a number within `range` for analog.",
    )

    @model_validator(mode="after")
    def _check_kind_coherence(self) -> "OutputLine":
        if self.kind == "digital":
            if self.range is not None:
                raise ValueError(f"output line {self.name!r}: a digital line must not declare a `range`.")
            if not isinstance(self.safe_state, bool):
                raise ValueError(f"output line {self.name!r}: a digital line's `safe_state` must be a boolean.")
        else:  # analog
            if self.range is None:
                raise ValueError(f"output line {self.name!r}: an analog line must declare a `range`.")
            lo, hi = self.range
            if lo > hi:
                raise ValueError(f"output line {self.name!r}: range min {lo} exceeds max {hi}.")
            if isinstance(self.safe_state, bool) or not (lo <= float(self.safe_state) <= hi):
                raise ValueError(
                    f"output line {self.name!r}: analog `safe_state` must be a number within {self.range}."
                )
        return self


class Outputs(BaseModel):
    """Declared output channels.

    `named_endpoints` are upstream destinations for `report` (`to: user`,
    `to: log`, `to: caller` are universal; custom destinations are declared
    here). `lines` are physical digital/analog output lines driven by
    `set_output` (RFC-0017).
    """

    model_config = ConfigDict(extra="forbid")

    named_endpoints: list[Identifier] = Field(default_factory=list)
    lines: list[OutputLine] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_line_names(self) -> "Outputs":
        names = [line.name for line in self.lines]
        dupes = {n for n in names if names.count(n) > 1}
        if dupes:
            raise ValueError(f"duplicate output line name(s): {sorted(dupes)!r}.")
        return self


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


class AraComBinding(BaseModel):
    """AUTOSAR Adaptive `ara::com` binding for a declared program (RFC-0019).

    Binds a `call_program` to a concrete AUTOSAR service-method invocation: the
    service id / instance id / method id triple that identifies the operation on
    the Adaptive Platform. The program's `args` are the typed argument template
    the validator already checks (RFC-0015); this binding adds only the routing
    triple, so AUTOSAR rides `call_program` rather than a new primitive. The id
    fields are optional in the schema and required by the validator when a
    binding is present, so an incomplete binding yields a stable `capability.*`
    error rather than a generic argument error.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["ara_com"]
    service_id: int | None = Field(None, ge=0, description="AUTOSAR service id.")
    instance_id: int | None = Field(None, ge=0, description="AUTOSAR service-instance id.")
    method_id: int | None = Field(None, ge=0, description="AUTOSAR method id within the service.")


class Program(BaseModel):
    """A substrate-defined program/method the robot exposes by name.

    Added by RFC-0015. A `call_program` step is rejected by the validator
    unless its `name` is declared here, preserving validate-before-actuate even
    though the program body is opaque to URML. `call_program` is the
    substrate-specific last resort, not a substitute for modelling a behavior
    with real primitives; a manifest only declares `programs:` when the
    substrate genuinely exposes named routines (e.g. a Kawasaki AS-language
    program, an OPC UA method node, a commissioned PLC job).

    A program MAY carry an optional substrate `binding` (RFC-0019) pinning it to
    a concrete substrate operation (currently `ara_com` for AUTOSAR Adaptive).
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    description: str | None = None
    args: list[ProgramArg] = Field(
        default_factory=list,
        description="Declared argument signature. Empty means the program takes no arguments.",
    )
    binding: AraComBinding | None = Field(
        default=None,
        description="Optional substrate binding (RFC-0019), e.g. an AUTOSAR ara::com id triple.",
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


class IpcSubstrate(BaseModel):
    """Zero-copy IPC sub-substrate declaration (RFC-0385).

    The transport beneath the RMW middleware: an Eclipse iceoryx generation
    (or a custom equivalent) used for high-frequency, large-payload paths
    (camera images, lidar clouds) via true shared-memory zero-copy. The two
    iceoryx generations differ in a way the manifest must capture:

    - `iceoryx1` is RouDi-daemon based; a deployment registers against a
      central broker named by `runtime_name`.
    - `iceoryx2` is decentralized (no RouDi); a deployment is configured from
      a global config named by `config_path`, and `runtime_name` does not apply.

    Surfaced by the engaged iceoryx / iceoryx2 thread
    ([RFC-0210](../../../docs/rfcs/0210-iceoryx-outreach.md) /
    [RFC-0305](../../../docs/rfcs/0305-iceoryx2-outreach.md)).
    """

    model_config = ConfigDict(extra="forbid")

    generation: Literal["iceoryx1", "iceoryx2", "custom"]
    runtime_name: str | None = Field(
        default=None,
        description="RouDi daemon name (iceoryx1 only; the central broker to register against).",
    )
    config_path: str | None = Field(
        default=None,
        description="Path to the decentralized global config (iceoryx2 only; replaces the RouDi daemon).",
    )
    generation_note: str | None = Field(
        default=None,
        description="Required when generation is 'custom'. Free-text description of the IPC stack.",
    )
    messaging_pattern: Literal["pub_sub", "request_response", "event"] | None = Field(
        default=None,
        description="Primary messaging pattern used over the IPC transport.",
    )
    shared_memory_budget_mb: float | None = Field(
        default=None, ge=0,
        description="Shared-memory budget for zero-copy transfers, in MiB.",
    )
    max_publishers: int | None = Field(default=None, ge=0)
    max_subscribers: int | None = Field(default=None, ge=0)


class ClockSync(BaseModel):
    """Substrate time-synchronization regime (RFC-0477).

    A fieldbus clock cannot always be hidden. The moment a deployment must
    synchronize events caught *outside* the bus (the reason a ROS 2 backbone
    exists), the bus and the rest of the system have to share a time reference.
    There are two honest ways to declare that, surfaced by the
    ethercat_driver_ros2 maintainer (RFC-0320):

    - `reference: bus` — the bus clock *is* the system time reference. This
      gives the strongest real-time guarantee, especially when a slave has
      dedicated timing hardware (IEEE-1588 acceleration, GPS, an atomic clock);
      declare that with `hardware_timestamping: true`.
    - `reference: master_synced` — the bus rides the master's clock, which is
      synchronized to the user / system clock. This requires a sync protocol
      and puts a bound on the user clock's drift (`user_clock_max_offset_ms`).

    This complements the per-sensor `time_sync_methods` (RFC-0039): that field
    records how a sensor timestamps; this block records the substrate's clock
    architecture. Like the rest of `substrate`, it is a declaration of the
    hardware's regime, not a guarantee URML polices; v0.1 checks only coherence.
    """

    model_config = ConfigDict(extra="forbid")

    reference: Literal["bus", "master_synced"] = Field(
        ...,
        description=(
            "Who holds the time reference: the bus clock itself, or a master "
            "clock synchronized to the user / system clock."
        ),
    )
    sync_protocol: Literal[
        "ieee1588", "gptp", "ethercat_dc", "ptp", "gps", "none"
    ] | None = Field(
        default=None,
        description=(
            "Time-synchronization mechanism shared between bus and user. "
            "Required (and not 'none') when reference is 'master_synced'."
        ),
    )
    hardware_timestamping: bool = Field(
        default=False,
        description=(
            "Whether a slave provides dedicated timing hardware (IEEE-1588 "
            "acceleration, GPS, atomic clock) backing the reference."
        ),
    )
    user_clock_max_offset_ms: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Bound on the user clock's offset from the reference, ms. Only "
            "applicable when reference is 'master_synced'."
        ),
    )
    note: str | None = Field(
        default=None, description="Optional free-text description of the clock topology."
    )


class SubstrateElement(BaseModel):
    """A substrate element with declared ordering dependencies (RFC-0478).

    The order in which bus elements are brought up, configured, and recovered
    is load-bearing: a drive cannot init before its power bus, a gripper cannot
    configure before the arm it hangs off, and error recovery may need a
    different order than bring-up. `depends_on` declares bring-up order;
    `recovery_after` declares the (possibly different) error-recovery order.
    Both are dependency relations; the validator derives no schedule, it only
    checks the declaration is coherent (every dependency declared, no cycle).
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$",
        max_length=64,
        description="snake_case identifier for the element (a drive, a power bus, an I/O coupler).",
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="Element ids that must be brought up before this one.",
    )
    recovery_after: list[str] = Field(
        default_factory=list,
        description=(
            "Element ids that must be recovered before this one during error "
            "recovery. Empty means bring-up order applies."
        ),
    )


class Bringup(BaseModel):
    """Ordered bring-up / recovery plan for substrate elements (RFC-0478).

    Declares the bus elements and their ordering dependencies so the manifest
    captures a structural fact URML otherwise loses: the order constraints that
    a powering architecture and configuration interdependencies impose. The
    validator checks the dependency graphs are coherent (declared ids, acyclic);
    it does not execute the sequence.
    """

    model_config = ConfigDict(extra="forbid")

    elements: list[SubstrateElement] = Field(
        ..., min_length=1, description="The substrate elements and their ordering dependencies."
    )


class Substrate(BaseModel):
    """Substrate-class declarations beneath URML's runtime.

    Added by RFC-0250 (autopilot_class). Extended by RFC-0251 with
    rmw_implementation + rmw_options, and by RFC-0385 with `ipc` (the
    zero-copy IPC sub-substrate), RFC-0477 with `clock` (time synchronization),
    and RFC-0478 with `bringup` (ordered element bring-up / recovery). Future
    RFCs in the 0252-0285 range will add additional fields.

    Validator rules currently enforced:
    - RFC-0250: drone-class drive_type requires autopilot_class; custom
      requires autopilot_class_note.
    - RFC-0251: rmw_implementation == 'custom' requires
      rmw_implementation_note; qos_profile.history == 'keep_last' requires
      history_depth (also enforced by QosProfile's own constraints).
    - RFC-0385: ipc.generation coherence (iceoryx1 needs runtime_name;
      iceoryx2 needs config_path and forbids runtime_name; custom needs
      generation_note).
    - RFC-0477: clock.reference == 'master_synced' requires a sync_protocol
      other than 'none'; user_clock_max_offset_ms is only applicable then.
    - RFC-0478: bringup element ids are unique, every depends_on / recovery_after
      references a declared element, and both dependency graphs are acyclic.
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

    # RFC-0385: optional zero-copy IPC sub-substrate (iceoryx generation).
    ipc: IpcSubstrate | None = None

    # RFC-0477: optional time-synchronization regime of the substrate clock.
    clock: ClockSync | None = None

    # RFC-0478: optional ordered bring-up / recovery plan for bus elements.
    bringup: Bringup | None = None


class ValidationContext(BaseModel):
    """Optional simulation-fidelity hints (RFC-0381).

    Two advisory, closed-enum fields recording the validation context a
    deployment's intent was checked in: the terrain class it runs over and
    the fidelity tier it was validated against. Both are read by the
    simulation reference runtimes (a Chrono runtime selects a deformable
    terrain model for ``terrain_fidelity: deformable``); neither gates a
    primitive, and the validator enforces only enum membership. Surfaced
    and queued by RFC-0328 (Project Chrono) and the Move #24 sim wave.
    """

    model_config = ConfigDict(extra="forbid")

    terrain_fidelity: Literal["rigid", "deformable", "granular", "unmodeled"] | None = Field(
        default=None,
        description="Terrain class the deployment runs over. Read by sim runtimes; not enforced.",
    )
    simulator_target_class: Literal[
        "kinematic",
        "rigid_body",
        "high_fidelity_multibody",
        "photoreal",
        "hardware",
    ] | None = Field(
        default=None,
        description="Fidelity tier the intent was validated against. Closed enum; growth is RFC-gated.",
    )


class CommandRange(BaseModel):
    """One command quantity a learned policy was trained over (RFC-0383)."""

    model_config = ConfigDict(extra="forbid")

    quantity: Literal["linear_velocity_x", "linear_velocity_y", "yaw_rate"] = Field(
        ...,
        description="Command quantity (closed set; grows by RFC as a fixture exercises each).",
    )
    min: float
    max: float
    unit: Literal["m_per_s", "rad_per_s"]

    @model_validator(mode="after")
    def _ordered(self) -> CommandRange:
        if self.max < self.min:
            raise ValueError(f"command_range max {self.max} is below min {self.min}")
        return self


class PayloadRange(BaseModel):
    """Payload mass range a learned policy was trained under (RFC-0383)."""

    model_config = ConfigDict(extra="forbid")

    min: float = Field(0.0, ge=0)
    max: float = Field(..., ge=0)
    unit: Literal["kg"] = "kg"

    @model_validator(mode="after")
    def _ordered(self) -> PayloadRange:
        if self.max < self.min:
            raise ValueError(f"payload_range max {self.max} is below min {self.min}")
        return self


class LearnedPolicy(BaseModel):
    """The envelope a learned controller was trained and validated under (RFC-0383).

    A learned policy is valid only inside its training distribution. This block
    declares that distribution so the validator can refuse a deployment whose
    admissible intent (the strictest of the mechanical and safety-envelope
    ceilings) exceeds what the policy was trained for. The export mechanism (how
    a training framework emits these limits) is out of scope; URML defines the
    declaration and the static check.
    """

    model_config = ConfigDict(extra="forbid")

    policy_ref: str | None = Field(
        default=None,
        description="Opaque handle to the policy artifact (URI / registry id / path). Documentation, not parsed.",
    )
    command_ranges: list[CommandRange] = Field(default_factory=list)
    terrain_classes: list[Literal["rigid", "deformable", "granular", "unmodeled"]] = Field(
        default_factory=list,
        description="Terrain classes (RFC-0381 vocabulary) the policy was trained and validated on.",
    )
    payload_range: PayloadRange | None = None
    enforcement: Literal["reject", "warn"] = Field(
        "warn",
        description="Whether an out-of-training-envelope deployment is a validation error or a warning.",
    )


class AcyclicRegime(BaseModel):
    """The asynchronous (acyclic) command regime of the substrate (RFC-0469).

    A fieldbus carries two kinds of traffic. Cyclic process data (EtherCAT PDO,
    a CANopen PDO) runs on the guaranteed cadence the parent `realtime` block
    describes: the answer is immediate and a watchdog catches a missed cycle.
    Acyclic mailbox traffic (EtherCAT SDO, a CANopen SDO, an OPC UA method call)
    has no guaranteed return time, so a watchdog is the wrong instrument. There
    the honest contract is a *timeout* plus an explicit *goal-reached check*: the
    command may take an unbounded-but-bounded time, and completion is confirmed
    by reading back state, not by assuming the next cycle carries the answer.

    This optional sub-block lets a manifest declare that the substrate also
    exposes an acyclic path and how a command over it is bounded. Like the rest
    of `realtime`, it is a declaration of the hardware's regime, not a real-time
    guarantee URML polices; v0.1 enforces only internal coherence.
    """

    model_config = ConfigDict(extra="forbid")

    timeout_ms: float = Field(
        ...,
        gt=0,
        description=(
            "Deadline for an acyclic (SDO / mailbox) command before it is "
            "treated as failed. Unlike a cyclic watchdog this bounds a "
            "transaction with no guaranteed return time, ms."
        ),
    )
    requires_goal_check: bool = Field(
        True,
        description=(
            "Whether completion of an acyclic command must be confirmed by an "
            "explicit goal-reached / read-back check rather than assumed. True "
            "by default: an async mailbox answer is not implied by the next "
            "control cycle."
        ),
    )


class Realtime(BaseModel):
    """Cyclic / real-time timing contract of the substrate (RFC-0016).

    Fieldbus and OPC UA substrates run under a cyclic timing contract: a fixed
    control period and a watchdog deadline that faults the cell to a safe state
    if missed. This optional block lets the manifest declare that regime so it
    is a faithful description of the hardware. It is a *declaration*, not a
    contract URML enforces: `guarantee` states the honesty level, and v0.1
    enforces only internal coherence (watchdog >= one cycle), never a real-time
    guarantee. A future RFC may add an envelope-dwell Pass-3 rule.

    The same substrate often exposes an acyclic mailbox path alongside the
    cyclic one; `acyclic` (RFC-0469) declares that regime, which is bounded by a
    timeout and a goal-reached check rather than a cyclic watchdog.
    """

    model_config = ConfigDict(extra="forbid")

    cyclic_period_ms: float = Field(..., gt=0, description="Nominal control-cycle period, ms.")
    watchdog_ms: float = Field(
        ..., gt=0, description="Deadline before the substrate faults to a safe state, ms."
    )
    requested_packet_interval_ms: float | None = Field(
        None, gt=0, description="Fieldbus requested packet interval (RPI), ms. Optional."
    )
    guarantee: Literal["best_effort", "soft", "hard"] = Field(
        ...,
        description=(
            "Honest timing regime. Explicit so a manifest cannot imply a "
            "hard-real-time promise URML does not police."
        ),
    )
    acyclic: AcyclicRegime | None = Field(
        None,
        description=(
            "Optional asynchronous (SDO / mailbox) regime declaration (RFC-0469). "
            "Present when the substrate also serves acyclic commands."
        ),
    )


class HdMap(BaseModel):
    """A bound HD map a planner cost-maps against (RFC-0020).

    Format-neutral: `format` is a free label (lanelet2, opendrive, ...); the
    validator checks the declaration is present, not the map's internals.
    """

    model_config = ConfigDict(extra="forbid")

    format: str = Field(..., description="HD-map format label, e.g. lanelet2 or opendrive.")
    uri: str = Field(..., description="Location of the map artifact.")
    sha256: str | None = Field(None, description="Optional content hash of the map artifact.")
    frame: Identifier | None = Field(None, description="Frame the map is expressed in.")


class OddRegion(BaseModel):
    """A named region of the operational design domain (RFC-0020)."""

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    polygon: list[Point2] = Field(..., min_length=3, description="Region boundary (>= 3 vertices).")


class Odd(BaseModel):
    """Operational Design Domain: where the AV is allowed to operate (RFC-0020)."""

    model_config = ConfigDict(extra="forbid")

    regions: list[OddRegion] = Field(default_factory=list)
    max_velocity_mps: float | None = Field(
        None, ge=0, description="ODD speed cap; follow_trajectory must not exceed it."
    )
    weather: list[str] | None = Field(None, description="Permitted weather conditions.")


class Mrm(BaseModel):
    """Minimum-Risk Maneuver when the ODD is exited or a trajectory aborts (RFC-0020)."""

    model_config = ConfigDict(extra="forbid")

    strategy: Literal["pull_over", "stop_in_lane", "controlled_stop"]


class AvProfile(BaseModel):
    """AV-profile manifest block (RFC-0020): HD map, ODD, and MRM.

    Research-grade by construction; `production_safety_certified` is a profile
    attribute (`spec/profiles/av/`), not a manifest claim. The block is optional
    and fully additive; `plan_path` requires `hd_map` to be present.
    """

    model_config = ConfigDict(extra="forbid")

    hd_map: HdMap | None = None
    odd: Odd | None = None
    mrm: Mrm | None = None


class MinimalNode(BaseModel):
    """A non-mobile sensor/actuator microcontroller node (RFC-0018).

    The honest declaration for the large class of classroom hardware that is
    not a robot in the mobility/manipulation/perception sense: a fixed micro:bit
    with an LED + buzzer + light sensor, a breadboard with one servo. Such a node
    has no honest `mobility`, no manipulator, often no camera — but it does sense
    and actuate. Rather than fake a `differential` mobility so a fixture
    validates (silent schema-bending), it declares `minimal_node` and the
    conformance suite recognises it as a coherent class.

    Declarative only — it introduces no primitive. The actuation verb a minimal
    node uses is RFC-0017's `set_output` over a declared `outputs.lines[]`;
    `declared_outputs` names those lines, `declared_sensors` names entries in
    `perception.sensors` when present. `minimal_node` and `mobility` are mutually
    exclusive (a thing either drives or declares that it does not).
    """

    model_config = ConfigDict(extra="forbid")

    class_: Literal["sensor", "actuator", "sensor_actuator"] = Field(..., alias="class")
    declared_sensors: list[Identifier] = Field(
        default_factory=list,
        description="Sensor names; each MUST also appear in `perception.sensors` when that block is present.",
    )
    declared_outputs: list[Identifier] = Field(
        default_factory=list,
        description="Output-line names the node's `set_output` targets; each MUST be a declared `outputs.lines[]` line.",
    )
    has_locomotion: bool = Field(
        False,
        description="Explicit: a minimal node does not move. MUST be False; declare `mobility` instead if it does.",
    )

    @model_validator(mode="after")
    def _class_matches_declarations(self) -> "MinimalNode":
        """A `sensor` node declares sensors; an `actuator` node declares outputs;
        `sensor_actuator` may declare both. (Intra-block coherence; cross-refs to
        perception/outputs are checked by the validator with capability.* codes.)"""
        if self.class_ in ("sensor", "sensor_actuator") and not self.declared_sensors:
            raise ValueError(f"minimal_node class {self.class_!r} requires at least one declared_sensors entry")
        if self.class_ in ("actuator", "sensor_actuator") and not self.declared_outputs:
            raise ValueError(f"minimal_node class {self.class_!r} requires at least one declared_outputs entry")
        return self


class SttOptions(BaseModel):
    """Speech-to-text engine options (RFC-0260). All optional, deployment hints."""

    model_config = ConfigDict(extra="forbid")

    inference_runtime: Literal["cpu", "gpu", "embedded"] | None = None
    quantization_level: Literal["fp32", "fp16", "int8", "int4"] | None = None
    latency_class: Literal["realtime", "batched", "offline"] | None = None
    model_size: Literal["tiny", "base", "small", "medium", "large"] | None = None


class TtsOptions(BaseModel):
    """Text-to-speech engine options (RFC-0260)."""

    model_config = ConfigDict(extra="forbid")

    voice_id: str | None = None
    sample_rate_hz: int | None = Field(None, gt=0)


class TranslationOptions(BaseModel):
    """Translation engine options (RFC-0260).

    `source_languages` should cover the languages the Layer-4 grammar accepts;
    `target_languages` is the runtime-side language(s) the pipeline emits.
    """

    model_config = ConfigDict(extra="forbid")

    source_languages: list[str] = Field(default_factory=list)
    target_languages: list[str] = Field(default_factory=list)
    offline_capable: bool | None = None


class EngineOptions(BaseModel):
    """Per-engine option sub-blocks under `language` (RFC-0260)."""

    model_config = ConfigDict(extra="forbid")

    stt: SttOptions | None = None
    tts: TtsOptions | None = None
    translation: TranslationOptions | None = None


class Language(BaseModel):
    """Layer-4 natural-language infrastructure declaration (RFC-0260).

    The `listen` and `speak` primitives are substrate-dependent: a deployment
    composes them with a speech-to-text engine, a text-to-speech engine, and
    (for multilingual deployments) a translation engine. This block lets a
    manifest declare which engine class implements each, so the validator can
    reason about the Layer-4 pipeline rather than treating substrate-neutrality
    as merely rhetorical. Closed enums with a `custom` escape hatch (which
    requires a `_note`). Optional and additive; a deployment with no `listen` /
    `speak` programs need not declare it.

    Engine-class values are origin-neutral at the schema level. A US-federal
    origin gate (the Russian-origin `vosk` STT engine) is enforced by the
    validator only when the bundled default compliance policy is in effect, the
    same two-layer split URML uses elsewhere: the schema validates shape, the
    policy validates substrate-permissibility.
    """

    model_config = ConfigDict(extra="forbid")

    stt_engine_class: Literal[
        "whisper", "faster_whisper", "whisper_cpp", "vosk", "porcupine_handoff", "custom"
    ] | None = None
    stt_engine_class_note: str | None = None
    tts_engine_class: Literal[
        "openvoice", "piper", "mozilla_tts", "espeak", "custom"
    ] | None = None
    tts_engine_class_note: str | None = None
    translation_engine_class: Literal[
        "opus_mt", "argos_translate", "marian_nmt", "nllb", "libretranslate", "custom"
    ] | None = None
    translation_engine_class_note: str | None = None
    engine_options: EngineOptions | None = None

    @model_validator(mode="after")
    def _custom_requires_note(self) -> "Language":
        """A `custom` engine class must name the engine via its `_note`."""
        if self.stt_engine_class == "custom" and not self.stt_engine_class_note:
            raise ValueError("language.stt_engine_class 'custom' requires stt_engine_class_note")
        if self.tts_engine_class == "custom" and not self.tts_engine_class_note:
            raise ValueError("language.tts_engine_class 'custom' requires tts_engine_class_note")
        if self.translation_engine_class == "custom" and not self.translation_engine_class_note:
            raise ValueError(
                "language.translation_engine_class 'custom' requires translation_engine_class_note"
            )
        return self


# RFC-0262: license-boundary declarations. The canonical SPDX-style license
# identifiers URML reasons about, and the restrictiveness ordering (least to
# most) the policy gate uses. CC-BY-NC is most-restrictive (commercial gate);
# `unknown` is most-restrictive (ambiguity). Shared with RFC-0304.
LicenseId = Literal[
    "apache_2_0",
    "bsd_3_clause",
    "mit",
    "mpl_2_0",
    "epl_2_0",
    "lgpl_3_0",
    "gpl_2_0",
    "gpl_3_0",
    "agpl_3_0",
    "cc_by_4_0",
    "cc_by_nc_4_0",
    "unknown",
]

#: Restrictiveness ordering (RFC-0262 §validator behavior 5), least to most.
LICENSE_RESTRICTIVENESS: tuple[str, ...] = (
    "apache_2_0",
    "mit",
    "bsd_3_clause",
    "mpl_2_0",
    "epl_2_0",
    "lgpl_3_0",
    "gpl_2_0",
    "gpl_3_0",
    "agpl_3_0",
    "cc_by_4_0",
    "cc_by_nc_4_0",
    "unknown",
)

#: Licenses URML may vendor in-source (Apache-2.0-compatible). Vendoring any
#: other (a copyleft / non-commercial license) is a hard error; use a
#: subprocess / network / cross-citation boundary instead.
VENDORABLE_LICENSES: frozenset[str] = frozenset(
    {"apache_2_0", "bsd_3_clause", "mit", "mpl_2_0"}
)


class LicenseComponent(BaseModel):
    """One license-bearing component the deployment composes with (RFC-0262).

    `boundary` is the integration shape: `vendored` (source pulled into a URML
    adapter, only legal for Apache-2.0-compatible licenses), `subprocess` (a
    separate process the adapter calls; the boundary insulates URML's Apache-2.0
    source), `network_rest` (a network service called over HTTP), or
    `cross_citation` (API / vocabulary reference only, no code reuse).
    `commercial_use_gate: true` flags a non-commercial component (NLLB-200's
    CC-BY-NC weights); the gate is declarative until the deployment-commercial
    flag (RFC-0268) lands.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    license: LicenseId
    boundary: Literal["vendored", "subprocess", "network_rest", "cross_citation"]
    commercial_use_gate: bool | None = None
    network_endpoint: str | None = None
    secret_reference: str | None = Field(
        None,
        description="Opaque audit pointer, e.g. 'env:VAR' or 'vault:path'. Not dereferenced.",
    )

    @model_validator(mode="after")
    def _network_rest_requires_endpoint(self) -> "LicenseComponent":
        if self.boundary == "network_rest" and not self.network_endpoint:
            raise ValueError(
                f"licensing component {self.name!r}: boundary 'network_rest' requires network_endpoint"
            )
        return self


class Licensing(BaseModel):
    """Per-component license-boundary declaration (RFC-0262).

    Extends URML's federal-procurement narrative from substrate-origin (NDAA
    889) and provenance to substrate-license-boundary. Optional and additive;
    a deployment composing only Apache-2.0 / BSD / MIT substrates need not
    declare it. `policy_required_max_restrictiveness`, when set and a policy is
    enforced, refuses any component whose license is more restrictive than the
    cap.
    """

    model_config = ConfigDict(extra="forbid")

    components: list[LicenseComponent] = Field(default_factory=list)
    policy_required_max_restrictiveness: LicenseId | None = None


class Deployment(BaseModel):
    """Deployment-level metadata, principally the commercial-use posture (RFC-0268).

    Closes RFC-0262's commercial-use-gate loop: a `commercial_use_gate: true`
    licensing component (NLLB-200's CC-BY-NC weights, an AGPL network surface)
    is only a *violation* when the deployment itself is commercial. This block
    declares that. `commercial_use` defaults to **true** (most-restrictive): the
    cost of accidentally shipping a CC-BY-NC weight in a sold product is higher
    than the cost of an explicit `commercial_use: false`, so a genuinely
    non-commercial deployment must say so. `deployment_class` is informational
    (documents the why); `commercial_use` is the enforced gate.
    """

    model_config = ConfigDict(extra="forbid")

    commercial_use: bool = Field(
        True,
        description="Whether the deployment is commercial. Defaults true (most-restrictive).",
    )
    deployment_class: Literal[
        "research", "education", "hobby", "production", "unspecified"
    ] | None = None
    organization: str | None = None
    declared_at: str | None = None


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

    # RFC-0381: optional simulation-fidelity hints (terrain + validation tier).
    validation: ValidationContext | None = None

    # RFC-0383: optional learned-controller training envelope.
    learned_policy: LearnedPolicy | None = None

    # RFC-0384: optional whole-body kinematic structure + stability limits.
    whole_body: WholeBody | None = None

    # RFC-0016: optional cyclic / real-time timing contract.
    realtime: Realtime | None = None

    # RFC-0020: optional AV-profile declarations (HD map, ODD, MRM).
    av: AvProfile | None = None

    # RFC-0018: optional minimal sensor/actuator MCU-node declaration.
    # Mutually exclusive with `mobility` (checked in the validator).
    minimal_node: MinimalNode | None = None

    # RFC-0260: optional Layer-4 NL-infrastructure engine declarations
    # (speech-to-text / text-to-speech / translation engine classes).
    language: Language | None = None

    # RFC-0262: optional per-component license-boundary declarations.
    licensing: Licensing | None = None

    # RFC-0268: optional deployment metadata (commercial-use posture).
    deployment: Deployment | None = None
