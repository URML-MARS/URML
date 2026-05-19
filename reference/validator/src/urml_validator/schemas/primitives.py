"""Layer-2 — Intent primitive arg schemas.

One pydantic model per primitive. The model represents the *arguments* of the
primitive (what appears under the verb name in YAML). The `Step` wrapper in
`composition.py` maps the YAML surface (a single-key dict like
`{"move_to": {...}}`) onto these models.

Each model below mirrors the per-primitive section of RFC-0002 Detailed Design.
Additional cross-field validation that requires the manifest or envelope is
the *validator's* job (next milestone), not the schema's.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from urml_validator.schemas.common import (
    Duration,
    Force,
    Identifier,
    Pose,
    Speed,
    VarRef,
)

# ---------------------------------------------------------------------------
# 1. move_to
# ---------------------------------------------------------------------------


class MoveToArgs(BaseModel):
    """Go to a named location or a pose."""

    model_config = ConfigDict(extra="forbid")

    location: Identifier | None = None
    pose: Pose | None = None
    frame: Identifier | None = None
    carrying: VarRef | None = None
    speed: Speed | float | None = None

    @model_validator(mode="after")
    def _exactly_one_target(self) -> MoveToArgs:
        if (self.location is None) == (self.pose is None):
            raise ValueError("move_to requires exactly one of `location` or `pose`")
        if self.pose is not None and self.frame is None:
            raise ValueError("move_to with `pose` requires `frame`")
        return self


# ---------------------------------------------------------------------------
# 2. dock
# ---------------------------------------------------------------------------


class DockArgs(BaseModel):
    """Return to a declared station and optionally perform a service."""

    model_config = ConfigDict(extra="forbid")

    at: Identifier | None = None  # defaults to manifest's primary dock if omitted
    service: Identifier = "park"
    until: Literal["full", "depleted"] | Duration | None = None


# ---------------------------------------------------------------------------
# 3. hover
# ---------------------------------------------------------------------------


class HoverArgs(BaseModel):
    """Actively maintain position against disturbances."""

    model_config = ConfigDict(extra="forbid")

    over: VarRef | Identifier | None = None
    duration: Duration | None = None
    until: str | None = None  # condition string; type-checked by validator
    tolerance: float | None = Field(None, gt=0)

    @model_validator(mode="after")
    def _at_most_one_bound(self) -> HoverArgs:
        if self.duration is not None and self.until is not None:
            raise ValueError("hover: `duration` and `until` are mutually exclusive")
        return self


# ---------------------------------------------------------------------------
# 4. wait
# ---------------------------------------------------------------------------


class WaitArgs(BaseModel):
    """Pause in place passively for a duration."""

    model_config = ConfigDict(extra="forbid")

    duration: Duration


# ---------------------------------------------------------------------------
# 5. wait_for
# ---------------------------------------------------------------------------


class SensorThreshold(BaseModel):
    """Threshold predicate used inside `wait_for(condition: ...)`."""

    model_config = ConfigDict(extra="forbid")

    sensor: Identifier
    op: Literal["gt", "lt", "eq", "ne", "gte", "lte"]
    value: float


class WaitForCondition(BaseModel):
    """Exactly one of the condition kinds must be set."""

    model_config = ConfigDict(extra="forbid")

    event: Identifier | None = None
    signal: Identifier | None = None
    input: Literal["speech", "text", "gesture", "button", "external"] | None = None
    sensor_threshold: SensorThreshold | None = None

    @model_validator(mode="after")
    def _exactly_one(self) -> WaitForCondition:
        candidates = ("event", "signal", "input", "sensor_threshold")
        set_fields = [f for f in candidates if getattr(self, f) is not None]
        if len(set_fields) != 1:
            raise ValueError(
                "wait_for.condition requires exactly one of: "
                "event, signal, input, sensor_threshold"
            )
        return self


class WaitForArgs(BaseModel):
    """Block until an external event/signal/input."""

    model_config = ConfigDict(extra="forbid")

    condition: WaitForCondition
    timeout: Duration | None = None
    on_timeout: Literal["error", "continue"] = "error"
    store_as: Identifier | None = None


# ---------------------------------------------------------------------------
# 6. grasp
# ---------------------------------------------------------------------------


class GraspArgs(BaseModel):
    """Close a gripper on a detected target."""

    model_config = ConfigDict(extra="forbid")

    target: VarRef
    force: Force | Literal["gentle", "firm"] | float | None = None
    approach: Literal["top", "side", "front", "auto"] = "auto"


# ---------------------------------------------------------------------------
# 7. release
# ---------------------------------------------------------------------------


class ReleaseArgs(BaseModel):
    """Open a gripper with a declared mode."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["drop", "place", "hand_to_user"]
    at: VarRef | Identifier | None = None
    height: float | None = Field(None, ge=0)

    @model_validator(mode="after")
    def _place_requires_at(self) -> ReleaseArgs:
        if self.mode == "place" and self.at is None:
            raise ValueError("release(mode: place) requires `at`")
        return self


# ---------------------------------------------------------------------------
# 8. detect
# ---------------------------------------------------------------------------


class DetectAttributes(BaseModel):
    """Class-specific attributes used to narrow a `detect` query.

    The schema is permissive — different object classes have different
    attribute sets. The validator may apply class-specific tightening at
    validation time.
    """

    model_config = ConfigDict(extra="allow")

    color: str | None = None
    size: str | dict[str, float] | None = None
    tag: str | None = None


class DetectWhere(BaseModel):
    """Search-region constraint for `detect`."""

    model_config = ConfigDict(extra="forbid")

    near: VarRef | Identifier | None = None
    within: float | None = Field(None, gt=0)


class DetectArgs(BaseModel):
    """Find an object matching criteria and bind it to a variable."""

    model_config = ConfigDict(extra="forbid")

    object: Identifier
    attributes: DetectAttributes | None = None
    where: DetectWhere | None = None
    store_as: Identifier | None = None


# ---------------------------------------------------------------------------
# 9. scan
# ---------------------------------------------------------------------------


class ScanArea(BaseModel):
    """Area specification for `scan`.

    Exactly one of `polygon`, `bounding_box`, or `named_region` must be set.
    """

    model_config = ConfigDict(extra="forbid")

    polygon: list[Pose] | None = None  # list of corner poses
    bounding_box: dict[str, float] | None = None  # {min_x, max_x, min_y, max_y, ...}
    named_region: Identifier | None = None

    @model_validator(mode="after")
    def _exactly_one(self) -> ScanArea:
        set_fields = [
            f for f in ("polygon", "bounding_box", "named_region") if getattr(self, f) is not None
        ]
        if len(set_fields) != 1:
            raise ValueError(
                "scan.area requires exactly one of: polygon, bounding_box, named_region"
            )
        return self


class ScanArgs(BaseModel):
    """Survey an area with a declared pattern."""

    model_config = ConfigDict(extra="forbid")

    area: ScanArea
    pattern: Literal["serpentine", "spiral", "grid", "adaptive"] = "serpentine"
    overlap: Annotated[float, Field(ge=0, le=1)] = 0.3
    altitude: float | None = None  # drone profile alias for pose.z; ground profiles ignore
    media: Literal["photo", "video", "sensor_only"] = "photo"
    sensor: Identifier | None = None
    store_as: Identifier


# ---------------------------------------------------------------------------
# 10. measure
# ---------------------------------------------------------------------------


class MeasureArgs(BaseModel):
    """Take a single reading and bind it."""

    model_config = ConfigDict(extra="forbid")

    what: Literal[
        "distance",
        "temperature",
        "weight",
        "pressure",
        "humidity",
        "depth",
        "wind_speed",
        "current",
        "voltage",
    ] | Identifier
    target: VarRef | Identifier | None = None
    sensor: Identifier | None = None
    store_as: Identifier


# ---------------------------------------------------------------------------
# 11. capture
# ---------------------------------------------------------------------------


class CaptureAttributes(BaseModel):
    """Optional media attributes for `capture`."""

    model_config = ConfigDict(extra="forbid")

    resolution: str | None = None  # "1080p", "4k", ...
    format: str | None = None
    frame_rate: float | None = Field(None, gt=0)


class CaptureArgs(BaseModel):
    """Capture a media artifact and bind a handle."""

    model_config = ConfigDict(extra="forbid")

    media: Literal["photo", "video"]
    target: VarRef | Identifier | None = None
    duration: Duration | None = None
    attributes: CaptureAttributes | None = None
    store_as: Identifier

    @model_validator(mode="after")
    def _video_requires_duration(self) -> CaptureArgs:
        if self.media == "video" and self.duration is None:
            raise ValueError("capture(media: video) requires `duration`")
        if self.media == "photo" and self.duration is not None:
            raise ValueError("capture(media: photo) must not declare `duration`")
        return self


# ---------------------------------------------------------------------------
# 12. report
# ---------------------------------------------------------------------------


class ReportArgs(BaseModel):
    """Send structured information upstream."""

    model_config = ConfigDict(extra="forbid")

    to: Literal["user", "log", "caller"] | Identifier = "user"
    facts: dict[str, object]
    attachments: list[VarRef] | None = None
    status: Literal["success", "partial", "failure"] = "success"
    severity: Literal["info", "notice", "warning", "error"] = "info"


# ---------------------------------------------------------------------------
# Home-profile primitives (RFC-0002 §Profile-extensibility authorizes these).
# ---------------------------------------------------------------------------


class SpeakArgs(BaseModel):
    """Emit a spoken utterance to the user (home profile)."""

    model_config = ConfigDict(extra="forbid")

    utterance: str = Field(..., min_length=1)
    locale: str | None = None  # BCP-47; default = manifest's primary_locale
    style: Literal["notice", "warning", "conversational"] = "conversational"
    interrupt: bool = False


class ListenArgs(BaseModel):
    """Block until the user provides spoken input (home profile)."""

    model_config = ConfigDict(extra="forbid")

    prompt: str | None = None
    locale: str | None = None
    timeout: Duration | None = None
    expected: Literal["free_form", "confirmation", "choice"] = "free_form"
    choices: list[str] | None = None
    store_as: Identifier | None = None

    @model_validator(mode="after")
    def _choices_iff_choice(self) -> ListenArgs:
        if self.expected == "choice" and not self.choices:
            raise ValueError("listen(expected: choice) requires non-empty `choices`")
        if self.expected != "choice" and self.choices is not None:
            raise ValueError("listen.choices is only allowed when expected == 'choice'")
        return self


# ---------------------------------------------------------------------------
# Drone-profile primitives (RFC-0002 §Profile-extensibility authorizes these).
# ---------------------------------------------------------------------------


class TakeOffArgs(BaseModel):
    """Begin flight: ascend from ground position to declared altitude (drone profile)."""

    model_config = ConfigDict(extra="forbid")

    altitude: float = Field(..., gt=0, description="Target altitude in meters.")
    climb_rate: float | None = Field(
        None, gt=0, description="Optional climb rate in m/s. Substrate default if omitted."
    )


class LandArgs(BaseModel):
    """End flight: descend to a declared landing location (drone profile)."""

    model_config = ConfigDict(extra="forbid")

    at: Identifier | None = None
    precision: Literal["standard", "precise"] = "standard"


class ReturnToHomeArgs(BaseModel):
    """Abort current flight intent and return to declared home location (drone profile)."""

    model_config = ConfigDict(extra="forbid")

    speed: float | None = Field(None, gt=0)
    altitude: float | None = Field(None, gt=0)


# ---------------------------------------------------------------------------
# Industrial-profile primitives (RFC-0002 §Profile-extensibility authorizes
# these; RFC-0013 operationalizes them).
# ---------------------------------------------------------------------------


class PickFromArgs(BaseModel):
    """Pick a detected object from a declared station (industrial profile).

    Convenience over `move_to(source) + detect(object) + grasp($target)` for
    the most-common industrial pattern. Produces an `object` binding (same
    shape as `detect`) so `place_at.held` can reference it.
    """

    model_config = ConfigDict(extra="forbid")

    source: Identifier
    object: Identifier
    attributes: DetectAttributes | None = None
    force: Force | Literal["gentle", "firm"] | float | None = None
    store_as: Identifier | None = None


class PlaceAtArgs(BaseModel):
    """Place a held object at a declared station (industrial profile).

    Symmetric to `pick_from`; convenience over `move_to(target) +
    release(mode: place|drop)`. `held` is a `$ref` to a prior `pick_from`
    (or `detect`) binding.
    """

    model_config = ConfigDict(extra="forbid")

    target: Identifier
    held: VarRef
    mode: Literal["place", "drop"] = "place"
    height: float | None = Field(None, ge=0)

    @model_validator(mode="after")
    def _height_iff_drop(self) -> PlaceAtArgs:
        if self.height is not None and self.mode != "drop":
            raise ValueError("place_at.height is only allowed when mode == 'drop'")
        return self


class SwapToolArgs(BaseModel):
    """Change the end-of-arm tool at a declared tool-change station
    (industrial profile).

    Dispatches through the existing docking-station service mechanism: the
    station named by `at` must declare a `swap_tool` service. The
    `accepted_tools` per-station manifest field is deferred, so `to` is not
    validated against an accepted-tool list in v0.1 (see RFC-0013).
    """

    model_config = ConfigDict(extra="forbid")

    at: Identifier
    to: Identifier


# ---------------------------------------------------------------------------
# Registry of primitive names -> arg-model classes.
# ---------------------------------------------------------------------------

PRIMITIVE_NAMES: tuple[str, ...] = (
    "move_to",
    "dock",
    "hover",
    "wait",
    "wait_for",
    "grasp",
    "release",
    "detect",
    "scan",
    "measure",
    "capture",
    "report",
    "speak",
    "listen",
    "take_off",
    "land",
    "return_to_home",
    "pick_from",
    "place_at",
    "swap_tool",
)

PRIMITIVE_MODELS: dict[str, type[BaseModel]] = {
    "move_to": MoveToArgs,
    "dock": DockArgs,
    "hover": HoverArgs,
    "wait": WaitArgs,
    "wait_for": WaitForArgs,
    "grasp": GraspArgs,
    "release": ReleaseArgs,
    "detect": DetectArgs,
    "scan": ScanArgs,
    "measure": MeasureArgs,
    "capture": CaptureArgs,
    "report": ReportArgs,
    "speak": SpeakArgs,
    "listen": ListenArgs,
    "take_off": TakeOffArgs,
    "land": LandArgs,
    "return_to_home": ReturnToHomeArgs,
    "pick_from": PickFromArgs,
    "place_at": PlaceAtArgs,
    "swap_tool": SwapToolArgs,
}
