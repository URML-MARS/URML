"""The ROSAdapter Protocol — the substrate-neutral surface the runtime needs.

Design notes:

- The Protocol is **higher-level than raw ROS 2** (`send_navigation_goal`
  rather than `send_goal_async` on a Nav2 action client). The intent is
  to keep the runtime substrate-neutral. A non-ROS adapter (PX4/MAVLink,
  OPC UA Robotics, vendor SDK) can implement the same surface without
  pretending to be ROS.
- Each method maps to one URML primitive's *dispatch step*. The runtime
  handles composition, validation, and variable bindings; the adapter
  handles the actual robot.
- Every method returns a typed result with a `success: bool` and any
  output bindings (object references, sensor values, media handles).
  Failures are *returned*, not raised — the runtime maps them to its
  on-error policy.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Result types — what the adapter returns to the runtime
# ---------------------------------------------------------------------------


class SubstrateResult(BaseModel):
    """Base class for adapter results. Every result has at minimum a success
    flag and an optional reason string for diagnostics."""

    model_config = ConfigDict(extra="forbid")

    success: bool
    reason: str | None = Field(
        None,
        description="Free-text diagnostic when success is False; ignored when success is True.",
    )


class NavigationResult(SubstrateResult):
    """Result of a `send_navigation_goal` call.

    Populated by `move_to`, `dock`, `hover`. The adapter is responsible for
    interpreting the goal's intent against the substrate's planner; the
    runtime only consumes the success flag and an optional `final_pose`.
    """

    final_pose: dict[str, float] | None = None  # {x, y, z?, yaw?, ...}
    frame: str | None = None


class ManipulationResult(SubstrateResult):
    """Result of a `send_manipulation_goal` call (grasp / release)."""

    grip_force_n: float | None = None  # actual measured force, where available


class DetectionResult(SubstrateResult):
    """Result of a `query_detection` call.

    A successful detection has a payload describing what was found. URML
    binds this to the requested `store_as` name; downstream primitives
    can dereference fields via `$name.pose`, `$name.attributes.color`, etc.
    """

    payload: dict[str, Any] | None = Field(
        None,
        description="Detected-object dict with at least `class`, `pose`, `frame`, "
        "`attributes`, `confidence`. None when success is False.",
    )


class ScanResult(SubstrateResult):
    """Result of a `run_scan` call. The payload mirrors RFC-0002's scan store_as shape."""

    payload: dict[str, Any] | None = Field(
        None,
        description="Scan result dict with at least `samples`, `coverage`, `anomalies`.",
    )


class MeasurementResult(SubstrateResult):
    """Result of a `take_measurement` call."""

    payload: dict[str, Any] | None = Field(
        None,
        description="Measurement dict with at least `value`, `unit`, `timestamp`.",
    )


class CaptureResult(SubstrateResult):
    """Result of a `capture_media` call."""

    payload: dict[str, Any] | None = Field(
        None,
        description="Media handle dict with at least `type`, `format`, `pose`, `frame`, `uri`.",
    )


class WaitResult(SubstrateResult):
    """Result of a `wait_for_condition` call.

    Populated when the wait resolves (timeout or condition satisfied). The
    payload carries the resolved value (e.g., the user's spoken input).
    """

    timed_out: bool = False
    payload: dict[str, Any] | None = None


class ListenResult(SubstrateResult):
    """Result of an `acquire_speech` call (home profile `listen` primitive).

    The payload mirrors the home-profile spec's listen-result shape:
    `{transcription, confidence, choice_index}`. `choice_index` is set only
    when `expected: choice` was used and the runtime maps the transcription
    to one of the declared choices.
    """

    timed_out: bool = False
    payload: dict[str, Any] | None = Field(
        None,
        description="Listen result dict with at least `transcription` (str), "
        "`confidence` (float 0..1), and optionally `choice_index` (int) when "
        "expected=choice.",
    )


# ---------------------------------------------------------------------------
# The Protocol itself
# ---------------------------------------------------------------------------


@runtime_checkable
class ROSAdapter(Protocol):
    """The substrate-facing surface the URML runtime uses.

    Every method maps to one URML primitive's dispatch step. Adapters must
    NOT raise on robot-side failures — failures are returned in the result's
    `success` field so the runtime's on-error policy can decide what to do.
    Unrecoverable errors (the substrate process died, the network broke)
    MAY raise; the runtime wraps those into `PrimitiveExecutionError`.
    """

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        """Move the robot to a named location or pose. Used by `move_to`, `hover`.

        `carrying`, when set, is the **resolved object payload** from a prior
        `detect` (or other binding-producing primitive) — not the URML
        reference string. The runtime handles the resolution.
        """
        ...

    def send_docking_goal(
        self,
        *,
        station: str,
        service: str,
        until: str | None = None,
    ) -> NavigationResult:
        """Return to a declared docking station and perform a service. Used by `dock`."""
        ...

    def send_manipulation_goal(
        self,
        *,
        action: Literal["grasp", "release"],
        target: dict[str, Any] | None = None,
        force_n: float | None = None,
        approach: Literal["top", "side", "front", "auto"] = "auto",
        release_mode: Literal["drop", "place", "hand_to_user"] | None = None,
        release_at: dict[str, Any] | str | None = None,
    ) -> ManipulationResult:
        """Grasp or release. Used by `grasp`, `release`.

        `target` is the **resolved object payload** (dict with class, pose,
        attributes, etc.) the runtime got from a prior `detect`. `release_at`
        may be either a resolved object dict or a literal named-location
        string, depending on whether the URML used `$ref` or a name.
        """
        ...

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        """Perceive an object matching criteria. Used by `detect`."""
        ...

    def run_scan(
        self,
        *,
        area: dict[str, Any],
        pattern: Literal["serpentine", "spiral", "grid", "adaptive"],
        overlap: float,
        altitude: float | None,
        media: Literal["photo", "video", "sensor_only"],
        sensor: str | None,
    ) -> ScanResult:
        """Survey an area with a declared pattern. Used by `scan`."""
        ...

    def take_measurement(
        self,
        *,
        what: str,
        target: str | None,
        sensor: str | None,
    ) -> MeasurementResult:
        """Take a single sensor reading. Used by `measure`."""
        ...

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        """Capture a photo or bounded video. Used by `capture`."""
        ...

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        """Block until a condition resolves or times out. Used by `wait_for`."""
        ...

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        """Pause in place for a duration. Used by `wait`."""
        ...

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        """Send structured information upstream. Used by `report`."""
        ...

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        """Speak an utterance to the user. Used by `speak` (home profile)."""
        ...

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        """Listen for spoken input and return a transcription. Used by `listen` (home profile).

        For `expected: choice`, the adapter is responsible for mapping the
        transcription to one of `choices` and populating `payload.choice_index`.
        For `expected: confirmation`, the adapter maps to a yes/no judgement;
        URML does not standardize how that decision is represented in
        `transcription` (the substrate decides).
        """
        ...
