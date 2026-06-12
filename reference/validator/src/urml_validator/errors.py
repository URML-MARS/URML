"""Structured validation errors.

The output format of the validator is the contract the LLM bridge uses to
revise emissions. Stability here matters: any code surfaced by a returned
``ValidationError`` is a part of the public API.

Error codes are namespaced: ``argument.*``, ``capability.*``, ``envelope.*``,
``binding.*``, ``policy.*``, ``fleet.*``. New codes may be added between minor
versions; existing codes do not change meaning.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorCode(StrEnum):
    """Stable, namespaced error codes the validator emits.

    Surface stability: these strings are part of the validator's public API
    and are consumed by the LLM bridge's revision flow. Renames are breaking.
    """

    # Pass 1 — argument typing (delegated to pydantic, surfaced here).
    ARGUMENT_TYPE = "argument.type"
    ARGUMENT_MISSING_REQUIRED = "argument.missing_required"
    ARGUMENT_UNKNOWN_FIELD = "argument.unknown_field"
    ARGUMENT_CONSTRAINT = "argument.constraint_violation"

    # Pass 2 — capability declarations on the manifest.
    CAPABILITY_MISSING_MOBILITY = "capability.missing_mobility"
    CAPABILITY_MISSING_MANIPULATION = "capability.missing_manipulation"
    CAPABILITY_MISSING_PERCEPTION = "capability.missing_perception"
    CAPABILITY_MISSING_STATION_KEEPING = "capability.missing_station_keeping"
    CAPABILITY_MISSING_GRIPPER = "capability.missing_gripper"
    CAPABILITY_ARM_NOT_DECLARED = "capability.arm_not_declared"
    CAPABILITY_BIMANUAL_REQUIRES_TWO_ARMS = "capability.bimanual_requires_two_arms"
    CAPABILITY_MISSING_CAMERA = "capability.missing_camera"
    CAPABILITY_MISSING_SENSOR = "capability.missing_sensor"
    CAPABILITY_MISSING_FRAME = "capability.missing_frame"
    # RFC-0290: the manifest's frame graph is malformed.
    CAPABILITY_FRAME_PARENT_UNDECLARED = "capability.frame_parent_undeclared"
    CAPABILITY_FRAME_CYCLE = "capability.frame_cycle"
    CAPABILITY_MISSING_LOCATION = "capability.missing_location"
    CAPABILITY_MISSING_OBJECT_CLASS = "capability.missing_object_class"
    CAPABILITY_MISSING_DOCKING_STATION = "capability.missing_docking_station"
    CAPABILITY_MISSING_DOCKING_SERVICE = "capability.missing_docking_service"
    CAPABILITY_MISSING_EVENT = "capability.missing_event"
    CAPABILITY_MISSING_OUTPUT = "capability.missing_output"
    CAPABILITY_FIXED_CAMERA_TARGET = "capability.fixed_camera_target"
    CAPABILITY_VIDEO_UNSUPPORTED = "capability.video_unsupported"
    CAPABILITY_MISSING_SPEECH_OUTPUT = "capability.missing_speech_output"
    CAPABILITY_MISSING_SPEECH_INPUT = "capability.missing_speech_input"
    CAPABILITY_DRIVE_TYPE_NOT_AERIAL = "capability.drive_type_not_aerial"
    CAPABILITY_MISSING_SERVICE_CEILING = "capability.missing_service_ceiling"
    CAPABILITY_MISSING_HOME_LOCATION = "capability.missing_home_location"
    # RFC-0006: a required abstract link role is absent from manifest.connectivity.
    CAPABILITY_MISSING_LINK_ROLE = "capability.missing_link_role"
    # RFC-0015: call_program references a program / args not declared in manifest.programs.
    CAPABILITY_MISSING_PROGRAM = "capability.missing_program"
    CAPABILITY_PROGRAM_ARG_MISMATCH = "capability.program_arg_mismatch"
    # RFC-0250: substrate.autopilot_class required when drive_type is a drone class.
    CAPABILITY_MISSING_AUTOPILOT_CLASS = "capability.missing_autopilot_class"
    CAPABILITY_AUTOPILOT_CLASS_NOTE_REQUIRED = "capability.autopilot_class_note_required"
    # RFC-0251: substrate.rmw_implementation custom requires note; QoS history rule.
    CAPABILITY_RMW_IMPLEMENTATION_NOTE_REQUIRED = "capability.rmw_implementation_note_required"
    CAPABILITY_QOS_KEEP_LAST_REQUIRES_DEPTH = "capability.qos_keep_last_requires_depth"
    # RFC-0385: substrate.ipc generation coherence.
    CAPABILITY_IPC_RUNTIME_NAME_REQUIRED = "capability.ipc_runtime_name_required"
    CAPABILITY_IPC_CONFIG_PATH_REQUIRED = "capability.ipc_config_path_required"
    CAPABILITY_IPC_RUNTIME_NAME_NOT_APPLICABLE = "capability.ipc_runtime_name_not_applicable"
    CAPABILITY_IPC_GENERATION_NOTE_REQUIRED = "capability.ipc_generation_note_required"
    # RFC-0016: realtime timing-block coherence.
    CAPABILITY_WATCHDOG_SHORTER_THAN_CYCLE = "capability.watchdog_shorter_than_cycle"
    # RFC-0469: acyclic (SDO / mailbox) regime coherence.
    CAPABILITY_ACYCLIC_TIMEOUT_SHORTER_THAN_CYCLE = (
        "capability.acyclic_timeout_shorter_than_cycle"
    )
    # RFC-0477: substrate.clock time-synchronization coherence.
    CAPABILITY_CLOCK_SYNC_PROTOCOL_REQUIRED = "capability.clock_sync_protocol_required"
    CAPABILITY_CLOCK_OFFSET_NOT_APPLICABLE = "capability.clock_offset_not_applicable"
    # RFC-0478: substrate.bringup ordered-sequence coherence.
    CAPABILITY_BRINGUP_DUPLICATE_ELEMENT = "capability.bringup_duplicate_element"
    CAPABILITY_BRINGUP_DEPENDENCY_UNDECLARED = "capability.bringup_dependency_undeclared"
    CAPABILITY_BRINGUP_DEPENDENCY_CYCLE = "capability.bringup_dependency_cycle"
    # RFC-0020: AV profile — plan_path requires a declared HD map.
    CAPABILITY_MISSING_HD_MAP = "capability.missing_hd_map"
    # RFC-0019: AUTOSAR ara::com program binding must declare the full id triple.
    CAPABILITY_ARA_COM_BINDING_INCOMPLETE = "capability.ara_com_binding_incomplete"
    # RFC-0017: digital/analog output actuation (`set_output`).
    CAPABILITY_OUTPUT_LINE_NOT_DECLARED = "capability.output_line_not_declared"
    CAPABILITY_OUTPUT_VALUE_TYPE_MISMATCH = "capability.output_value_type_mismatch"
    CAPABILITY_OUTPUT_VALUE_OUT_OF_RANGE = "capability.output_value_out_of_range"
    # RFC-0018: minimal sensor/actuator MCU-node declaration coherence.
    CAPABILITY_MINIMAL_NODE_WITH_MOBILITY = "capability.minimal_node_with_mobility"
    CAPABILITY_MINIMAL_NODE_LOCOMOTION_INCONSISTENT = "capability.minimal_node_locomotion_inconsistent"
    CAPABILITY_MINIMAL_NODE_UNDECLARED_OUTPUT = "capability.minimal_node_undeclared_output"
    CAPABILITY_MINIMAL_NODE_UNDECLARED_SENSOR = "capability.minimal_node_undeclared_sensor"
    # RFC-0260: Layer-4 NL-infrastructure (language block) coherence. The first
    # three are warnings (a `listen`/`speak` program with no declared engine; an
    # inconsistent translation language list); the advisory flags a copyleft /
    # non-commercial engine-license shape worth a human's attention.
    CAPABILITY_STT_ENGINE_UNDECLARED = "capability.stt_engine_undeclared"
    CAPABILITY_TTS_ENGINE_UNDECLARED = "capability.tts_engine_undeclared"
    CAPABILITY_TRANSLATION_LANGUAGES_INCONSISTENT = "capability.translation_languages_inconsistent"
    CAPABILITY_ENGINE_LICENSE_ADVISORY = "capability.engine_license_advisory"
    # RFC-0383: learned-policy training-envelope coherence.
    CAPABILITY_LEARNED_POLICY_TERRAIN_MISMATCH = "capability.learned_policy_terrain_mismatch"
    CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING = "capability.learned_policy_exceeds_training"

    # RFC-0384: whole-body kinematic structure + stability limits.
    CAPABILITY_WHOLE_BODY_INCONSISTENT = "capability.whole_body_inconsistent"
    CAPABILITY_WHOLE_BODY_UNSTABLE_COM = "capability.whole_body_unstable_com"
    CAPABILITY_CANNOT_CARRY_WHILE_MOVING = "capability.cannot_carry_while_moving"

    # Pass 3 — safety envelope (numeric caps + spatial constraints).
    ENVELOPE_VELOCITY_EXCEEDED = "envelope.velocity_exceeded"
    ENVELOPE_ALTITUDE_EXCEEDED = "envelope.altitude_exceeded"
    ENVELOPE_PAYLOAD_EXCEEDED = "envelope.payload_exceeded"
    ENVELOPE_FORCE_EXCEEDED = "envelope.force_exceeded"
    ENVELOPE_GEOFENCE_VIOLATION = "envelope.geofence_violation"
    ENVELOPE_OCCUPANCY_ZONE_INTRUSION = "envelope.occupancy_zone_intrusion"
    # RFC-0006: structured link-loss policy coherence.
    ENVELOPE_LINK_LOSS_UNDECLARED_ROLE = "envelope.link_loss_undeclared_role"
    ENVELOPE_LINK_LOSS_INCOHERENT = "envelope.link_loss_incoherent"
    ENVELOPE_LINK_OUTAGE_EXCEEDS_DECLARED = "envelope.link_outage_exceeds_declared"
    # RFC-0382: monitorable temporal-logic properties.
    ENVELOPE_MONITORABLE_PARSE_ERROR = "envelope.monitorable_parse_error"
    ENVELOPE_MONITORABLE_UNDECLARED_SIGNAL = "envelope.monitorable_undeclared_signal"

    # Pass 4 — variable bindings.
    BINDING_DUPLICATE_STORE_AS = "binding.duplicate_store_as"
    BINDING_UNRESOLVED_REFERENCE = "binding.unresolved_reference"
    BINDING_TYPE_MISMATCH = "binding.type_mismatch"

    # Pass 5 — compliance policy (RFC-0004).
    # The policy namespace is reserved; policy authors may emit any
    # `policy.*` string via PolicyRule.on_violation.code, not just these.
    POLICY_COUNTRY_DENIED = "policy.country_denied"
    POLICY_VENDOR_DENIED = "policy.vendor_denied"
    POLICY_HBOM_MISSING = "policy.hbom_missing"
    POLICY_ATTESTATION_INSUFFICIENT = "policy.attestation_insufficient"
    POLICY_RULE_INVALID = "policy.rule_invalid"
    # RFC-0260 — US-federal origin gate on a declared STT engine. Fires only
    # when the bundled default compliance policy is in effect (vosk is
    # Russian-origin); accepted without `--policy` or under a custom policy.
    POLICY_STT_ENGINE_ORIGIN_DENIED = "policy.stt_engine_origin_denied"

    # RFC-0005 — structured HBOM-content predicates (Pass 5 sub-pass).
    # Emitted when a policy rule reaches into a component's parsed Hardware
    # Bill of Materials rather than the manifest-declared provenance facts.
    # The country/vendor predicates walk the full CycloneDX pedigree, so a
    # covered part hidden in an ancestor or variant is caught at any depth.
    POLICY_HBOM_COMPONENT_COUNTRY_DENIED = "policy.hbom_component_country_denied"
    POLICY_HBOM_COMPONENT_VENDOR_DENIED = "policy.hbom_component_vendor_denied"
    # The HBOM file exists but could not be read as the declared format, or its
    # SHA-256 did not match the manifest's declared hash (a tampered or stale
    # HBOM). The default-policy templates treat it as an error so a broken HBOM
    # cannot silently bypass content rules.
    POLICY_HBOM_PARSE_FAILED = "policy.hbom_parse_failed"
    # The HBOM uri is remote (a scheme the validator does not fetch in v0.2) or
    # the local file is absent. Warning by default: the validator does not phone
    # home, so a remote or air-gapped HBOM degrades to "could not check" rather
    # than a hard failure.
    POLICY_HBOM_URI_UNREACHABLE = "policy.hbom_uri_unreachable"

    # Fleet — multi-robot coherence (RFC-0286). Fired only by `validate_fleet`;
    # a single-robot program with no roster never produces these.
    # An `on:` / `barrier:` node names a member not declared in the roster, or a
    # step is not addressed to any member of a multi-member fleet.
    FLEET_UNDECLARED_MEMBER = "fleet.undeclared_member"
    # A primitive scoped to a member whose manifest cannot satisfy it (the
    # underlying single-robot capability check, re-keyed to that member).
    FLEET_CAPABILITY_UNSUPPORTED_ON_MEMBER = "fleet.capability_unsupported_on_member"
    # Two distinct members are driven to the same declared location concurrently
    # inside one `parallel` with no rendezvous — a cross-robot collision risk.
    FLEET_CONCURRENT_SHARED_WORKSPACE = "fleet.concurrent_shared_workspace"
    # A `barrier` names a member whose manifest does not declare the `peer_link`
    # connectivity role required to synchronize (RFC-0006 reserved that role).
    FLEET_BARRIER_MISSING_PEER_LINK = "fleet.barrier_missing_peer_link"
    # RFC-0291: warning — a roster `shared_frame` is declared by no member, so the
    # geometric collision check silently has nothing to compare in it.
    FLEET_SHARED_FRAME_UNDECLARED = "fleet.shared_frame_undeclared"
    # RFC-0290: warning — a member's world `anchor` names a frame it doesn't declare,
    # so its targets won't resolve to the world.
    FLEET_ANCHOR_FRAME_UNDECLARED = "fleet.anchor_frame_undeclared"

    # Internal / programmer-error categories.
    INTERNAL = "internal.error"


Severity = Literal["error", "warning"]


class ValidationError(BaseModel):
    """A single static-validation error or warning.

    All fields are JSON-serializable so the LLM bridge can pass the structured
    error verbatim back to the language model for revision.

    The ``code`` field accepts either an ``ErrorCode`` enum value (preferred
    for built-in codes) or a plain string in the ``policy.*`` namespace
    (used for author-defined codes emitted by ``PolicyRule.on_violation``).
    The validator coerces a string to ``ErrorCode`` when the string matches
    a defined enum value; otherwise the string is preserved verbatim.
    """

    model_config = ConfigDict(extra="forbid")

    code: ErrorCode | str = Field(
        ...,
        description=(
            "Namespaced error code. ErrorCode enum values for built-in codes; "
            "any 'policy.*' string for author-defined policy codes."
        ),
    )
    severity: Severity = Field("error", description="`error` rejects the program; `warning` does not.")
    primitive: str | None = Field(
        None,
        description="The verb of the affected primitive (e.g., 'move_to'), if any.",
    )
    path: list[str] = Field(
        default_factory=list,
        description="JSON-Pointer-style path into the program tree. "
        "Example: ['behavior', 'steps', '2', 'move_to', 'location'].",
    )
    field: str | None = Field(
        None,
        description="Specific field within the primitive's args, if applicable.",
    )
    message: str = Field(..., description="Human-readable explanation.")
    suggestion: str | None = Field(
        None,
        description="Suggested correction. Consumed by the LLM bridge revision flow.",
    )
    detail: dict[str, Any] | None = Field(
        None,
        description=(
            "Optional structured detail for the error. Populated by Pass 5 (policy) "
            "with rule_id, policy_id, offending_value, allowed/denied lists, and a "
            "remediation_hint. Existing Pass 1-4 errors do not populate this field."
        ),
    )

    def render(self) -> str:
        """Compact one-line rendering used for log lines and pytest assertions."""
        prefix = "/".join(self.path) if self.path else "<program>"
        return f"[{self.code_str}] {prefix}: {self.message}"

    @property
    def code_str(self) -> str:
        """The error code as a plain string, regardless of whether it's enum or raw."""
        return str(self.code)


class ValidationResult(BaseModel):
    """The top-level result of validating a program against a manifest+envelope."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool = Field(..., description="True iff no `error`-severity errors fired.")
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationError] = Field(default_factory=list)

    @property
    def all_issues(self) -> list[ValidationError]:
        """Errors first, then warnings, in the order they were emitted."""
        return list(self.errors) + list(self.warnings)

    def codes(self) -> list[str]:
        """Just the error codes (as strings), in order. Convenient for assertions in tests."""
        return [str(e.code) for e in self.all_issues]

    def has(self, code: ErrorCode | str) -> bool:
        """True iff at least one error or warning with the given code is present."""
        target = str(code)
        return any(str(e.code) == target for e in self.all_issues)
