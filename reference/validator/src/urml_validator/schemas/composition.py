"""Layer-3 — Behavior composition schema.

The composition layer is what turns a list of primitives into a behavior:
sequence, branch, parallel, retry, and on-error handling, plus variable
bindings produced by primitives (`store_as`) and referenced by later steps
(`$name`).

The Step model wraps the YAML single-key-dict surface for primitives so a
list of `{move_to: {...}}` / `{detect: {...}}` parses cleanly. Nested
behaviors (a `sequence` inside a `parallel`, etc.) are recursive and use
pydantic's forward-reference support.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, model_validator

from urml_validator.schemas.common import Identifier
from urml_validator.schemas.primitives import (
    BimanualArgs,
    CallProgramArgs,
    CaptureArgs,
    DetectArgs,
    DockArgs,
    FollowTrajectoryArgs,
    GraspArgs,
    HoverArgs,
    LandArgs,
    ListenArgs,
    MeasureArgs,
    MoveToArgs,
    PickFromArgs,
    PlaceAtArgs,
    PlanPathArgs,
    ReleaseArgs,
    ReportArgs,
    ReturnToHomeArgs,
    ScanArgs,
    SpeakArgs,
    SwapToolArgs,
    TakeOffArgs,
    WaitArgs,
    WaitForArgs,
)

# ---------------------------------------------------------------------------
# Step: a single primitive invocation.
# ---------------------------------------------------------------------------


_PRIMITIVE_FIELDS = (
    "move_to",
    "dock",
    "hover",
    "wait",
    "wait_for",
    "grasp",
    "release",
    "bimanual",
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
    "call_program",
    "plan_path",
    "follow_trajectory",
)


class Step(BaseModel):
    """A primitive invocation in a behavior.

    YAML surface: `{primitive_name: {args}}` — e.g.:

        - move_to:
            location: kitchen

    Exactly one of the per-primitive fields below must be set on a Step.
    """

    model_config = ConfigDict(extra="forbid")

    move_to: MoveToArgs | None = None
    dock: DockArgs | None = None
    hover: HoverArgs | None = None
    wait: WaitArgs | None = None
    wait_for: WaitForArgs | None = None
    grasp: GraspArgs | None = None
    release: ReleaseArgs | None = None
    bimanual: BimanualArgs | None = None
    detect: DetectArgs | None = None
    scan: ScanArgs | None = None
    measure: MeasureArgs | None = None
    capture: CaptureArgs | None = None
    report: ReportArgs | None = None
    speak: SpeakArgs | None = None
    listen: ListenArgs | None = None
    take_off: TakeOffArgs | None = None
    land: LandArgs | None = None
    return_to_home: ReturnToHomeArgs | None = None
    pick_from: PickFromArgs | None = None
    place_at: PlaceAtArgs | None = None
    swap_tool: SwapToolArgs | None = None
    call_program: CallProgramArgs | None = None
    plan_path: PlanPathArgs | None = None
    follow_trajectory: FollowTrajectoryArgs | None = None

    @model_validator(mode="after")
    def _exactly_one_primitive(self) -> Step:
        present = [name for name in _PRIMITIVE_FIELDS if getattr(self, name) is not None]
        if len(present) != 1:
            raise ValueError(
                f"a Step must have exactly one primitive; got {len(present)}: {present!r}"
            )
        return self

    @property
    def primitive_name(self) -> str:
        """Return the verb of the single primitive this Step holds."""
        for name in _PRIMITIVE_FIELDS:
            if getattr(self, name) is not None:
                return name
        raise AssertionError("unreachable: _exactly_one_primitive should have caught this")


# ---------------------------------------------------------------------------
# Composition operators.
# ---------------------------------------------------------------------------


OnError = Literal["abort_and_report", "continue", "retry"]


class _BaseBehavior(BaseModel):
    """Common fields on every behavior composition node."""

    model_config = ConfigDict(extra="forbid")

    on_error: OnError | None = None
    label: str | None = None  # optional human-readable annotation


# RFC-0286 adds two fleet-addressing nodes: `on` (scope a subtree to a fleet
# member) and `barrier` (synchronize members). They are tagged like every other
# composition node so the discriminator stays a single, closed switch.
_TAG_TYPES = {"sequence", "branch", "parallel", "retry", "on", "barrier"}

# Map a composition class name back to its tag. `OnMember` is the one node whose
# class name is not its tag, so the discriminator cannot just lowercase it.
_CLASS_NAME_TO_TAG = {"onmember": "on", "barrier": "barrier"}


def _discriminate(value: object) -> str:
    """Pick the discriminator tag for a BehaviorOrStep node.

    - dict with `type: sequence|branch|parallel|retry|on|barrier` -> that type
    - any other dict (single-key primitive dict) -> "step"
    - pydantic model instance: its class name lowered (or mapped), or "step"
    """
    if isinstance(value, dict):
        type_field = value.get("type")
        if isinstance(type_field, str) and type_field in _TAG_TYPES:
            return type_field
        return "step"
    cls_name = type(value).__name__.lower()
    if cls_name in _CLASS_NAME_TO_TAG:
        return _CLASS_NAME_TO_TAG[cls_name]
    if cls_name in _TAG_TYPES:
        return cls_name
    return "step"


class Sequence(_BaseBehavior):
    """Execute `steps` in order. Fails the sequence if any step fails (default)."""

    type: Literal["sequence"] = "sequence"
    steps: list[BehaviorOrStep] = Field(..., min_length=1)


class Branch(_BaseBehavior):
    """Conditional execution: if `condition`, run `if_true`; else `if_false`."""

    type: Literal["branch"] = "branch"
    condition: str  # condition expression; semantic-checked by the validator
    if_true: BehaviorOrStep
    if_false: BehaviorOrStep | None = None


class Parallel(_BaseBehavior):
    """Execute `branches` concurrently."""

    type: Literal["parallel"] = "parallel"
    branches: list[BehaviorOrStep] = Field(..., min_length=2)
    complete_when: Literal["all", "any", "first_to_succeed"] = "all"


class Retry(_BaseBehavior):
    """Repeat `behavior` until success or `max_attempts` is reached."""

    type: Literal["retry"] = "retry"
    behavior: BehaviorOrStep
    max_attempts: int = Field(..., gt=0)
    until: str | None = None  # condition expression


# ---------------------------------------------------------------------------
# Fleet-addressing nodes (RFC-0286).
# ---------------------------------------------------------------------------


class OnMember(_BaseBehavior):
    """Scope `body` to a single fleet member (RFC-0286).

    Every primitive beneath an `on:` node is dispatched to the named roster
    member's robot. The node has exactly one child (`body`), so it preserves
    the single-root-tree invariant — it is a tagged wrapper, not a new kind of
    fan-out. A program with no `on:` node is a single-robot program and behaves
    exactly as before this RFC.

    YAML surface:

        - type: on
          member: courier
          body:
            type: sequence
            steps: [ ... ]
    """

    type: Literal["on"] = "on"
    member: Identifier  # roster handle this subtree is dispatched to
    body: BehaviorOrStep


class Barrier(_BaseBehavior):
    """Synchronize fleet members at a rendezvous point (RFC-0286).

    A leaf node: execution does not proceed past a `barrier` until every named
    member has reached it. This is the "sync command" — it is what makes a
    handoff safe (the receiving robot does not act until the delivering robot
    has arrived and stopped). Every named member must declare the `peer_link`
    connectivity role (validated by `fleet.barrier_missing_peer_link`).

    YAML surface:

        - type: barrier
          members: [courier, arm]
    """

    type: Literal["barrier"] = "barrier"
    members: list[Identifier] = Field(..., min_length=2)

    @model_validator(mode="after")
    def _unique_members(self) -> Barrier:
        if len(self.members) != len(set(self.members)):
            dupes = sorted({m for m in self.members if self.members.count(m) > 1})
            raise ValueError(f"barrier has duplicate member(s): {dupes}")
        return self


# The Behavior-or-Step union -- tagged for pydantic's discriminator.
BehaviorOrStep = Annotated[
    Annotated[Sequence, Tag("sequence")]
    | Annotated[Branch, Tag("branch")]
    | Annotated[Parallel, Tag("parallel")]
    | Annotated[Retry, Tag("retry")]
    | Annotated[OnMember, Tag("on")]
    | Annotated[Barrier, Tag("barrier")]
    | Annotated[Step, Tag("step")],
    Discriminator(_discriminate),
]


# Resolve forward references on the recursive classes now that BehaviorOrStep
# exists as a module-level alias.
Sequence.model_rebuild()
Branch.model_rebuild()
Parallel.model_rebuild()
Retry.model_rebuild()
OnMember.model_rebuild()
Barrier.model_rebuild()


# Public alias used by program.py.
Behavior = BehaviorOrStep
