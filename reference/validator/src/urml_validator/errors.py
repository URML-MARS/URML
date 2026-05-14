"""Structured validation errors.

The output format of the validator is the contract the LLM bridge uses to
revise emissions. Stability here matters: any code surfaced by a returned
``ValidationError`` is a part of the public API.

Error codes are namespaced: ``argument.*``, ``capability.*``, ``envelope.*``,
``binding.*``, ``policy.*``. New codes may be added between minor versions;
existing codes do not change meaning.
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
    CAPABILITY_MISSING_CAMERA = "capability.missing_camera"
    CAPABILITY_MISSING_SENSOR = "capability.missing_sensor"
    CAPABILITY_MISSING_FRAME = "capability.missing_frame"
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

    # Pass 3 — safety envelope (numeric caps + spatial constraints).
    ENVELOPE_VELOCITY_EXCEEDED = "envelope.velocity_exceeded"
    ENVELOPE_ALTITUDE_EXCEEDED = "envelope.altitude_exceeded"
    ENVELOPE_PAYLOAD_EXCEEDED = "envelope.payload_exceeded"
    ENVELOPE_FORCE_EXCEEDED = "envelope.force_exceeded"

    # Pass 4 — variable bindings.
    BINDING_DUPLICATE_STORE_AS = "binding.duplicate_store_as"
    BINDING_UNRESOLVED_REFERENCE = "binding.unresolved_reference"

    # Pass 5 — compliance policy (RFC-0004).
    # The policy namespace is reserved; policy authors may emit any
    # `policy.*` string via PolicyRule.on_violation.code, not just these.
    POLICY_COUNTRY_DENIED = "policy.country_denied"
    POLICY_VENDOR_DENIED = "policy.vendor_denied"
    POLICY_HBOM_MISSING = "policy.hbom_missing"
    POLICY_ATTESTATION_INSUFFICIENT = "policy.attestation_insufficient"
    POLICY_RULE_INVALID = "policy.rule_invalid"

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
