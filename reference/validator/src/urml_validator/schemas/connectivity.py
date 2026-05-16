"""Layer-1 — Abstract connectivity capability and link-loss safety contract.

Added by RFC-0006. Two concerns live here:

  - ``Connectivity`` is an optional sibling of mobility/manipulation/perception
    on the manifest. It declares the abstract *link roles* a robot supports.
  - ``LinkLossRule`` is the structured replacement for the envelope's old
    free-form ``link_loss_policy: str``. A deployment declares, per role,
    what the robot must do when that link is lost.

Everything here is **substrate-neutral by construction**. A link *role* is an
abstraction (operator-control, status, peer, bulk-data); the transport medium
that carries it (WiFi, 5G, LTE, RF, fibre, …) is Layer 0 and is deliberately
not modelled. ``AssuranceClass`` is an *assurance* abstraction, never a medium.

Schema version: tracks v0.1 (see RFC-0006).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LinkRole(StrEnum):
    """The abstract role a communication link plays for the robot.

    Closed by design: adding a role is a one-way door, the same posture the
    primitive vocabulary takes. ``peer_link`` is declared now (with no
    behavioural semantics) so the future multi-robot RFC is additive rather
    than a breaking enum change.
    """

    COMMAND_LINK = "command_link"      # operator/supervisor → robot control
    TELEMETRY_LINK = "telemetry_link"  # robot → operator status/health
    PEER_LINK = "peer_link"            # robot ↔ robot (future swarm; capability only)
    PAYLOAD_LINK = "payload_link"      # bulk mission/sensor data


class AssuranceClass(StrEnum):
    """Abstract, **ordered** assurance level of a declared link.

    Low → high. This is the reconciliation of "transport media as intent":
    intent can depend on a link's *assurance*, never on its radio. The
    ordering is load-bearing — a future RFC can express "require >= assured"
    additively without a breaking change. Ordinal value is the enum's
    position in ``_ORDER``.
    """

    BEST_EFFORT = "best_effort"
    MONITORED = "monitored"
    ASSURED = "assured"
    SAFETY_CRITICAL = "safety_critical"

    @property
    def rank(self) -> int:
        """0-based ordinal, low→high. For future ``>=`` policy comparisons."""
        return _ASSURANCE_ORDER.index(self)


_ASSURANCE_ORDER: tuple[AssuranceClass, ...] = (
    AssuranceClass.BEST_EFFORT,
    AssuranceClass.MONITORED,
    AssuranceClass.ASSURED,
    AssuranceClass.SAFETY_CRITICAL,
)


class DeclaredLink(BaseModel):
    """One abstract link the robot declares it supports.

    Properties are abstract only. ``required_for_operation`` and
    ``autonomous_when_lost`` are the two booleans the validator's link-loss
    coherence check reasons over; ``max_outage_seconds`` is a declared
    tolerance the envelope may tighten but never relax.
    """

    model_config = ConfigDict(extra="forbid")

    role: LinkRole
    required_for_operation: bool = Field(
        False,
        description="If true, the robot cannot operate without this link present.",
    )
    autonomous_when_lost: bool = Field(
        False,
        description=(
            "If true, the robot can continue its mission with this link absent. "
            "Required for a `continue_autonomous` link-loss action to be coherent."
        ),
    )
    max_outage_seconds: float | None = Field(
        None,
        ge=0,
        description=(
            "Declared maximum tolerable outage for this link, in seconds. "
            "Abstract tolerance, not a runtime timeout. None = unbounded."
        ),
    )
    assurance_class: AssuranceClass = Field(
        AssuranceClass.BEST_EFFORT,
        description="Abstract assurance level. Never a transport medium.",
    )
    description: str | None = None


class Connectivity(BaseModel):
    """Optional manifest block declaring the robot's abstract link roles.

    Sibling of mobility/manipulation/perception/provenance. When absent (and
    no envelope link-loss rule requires a role) connectivity checks are a
    no-op — the feature is opt-in at the manifest level, like `provenance`.
    """

    model_config = ConfigDict(extra="forbid")

    links: list[DeclaredLink] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_roles(self) -> Connectivity:
        roles = [link.role for link in self.links]
        if len(roles) != len(set(roles)):
            dupes = sorted({r.value for r in roles if roles.count(r) > 1})
            raise ValueError(f"connectivity.links has duplicate role(s): {dupes}")
        return self

    def link_for(self, role: LinkRole) -> DeclaredLink | None:
        """The declared link for ``role``, or None if the robot does not declare it."""
        return next((link for link in self.links if link.role == role), None)


class LinkLossAction(StrEnum):
    """What the robot must do when a governed link is lost.

    The union of every value the home/drone/industrial profiles already name,
    plus ``continue_autonomous`` (only coherent when the governed link is
    declared ``autonomous_when_lost``).
    """

    RETURN_TO_HOME = "return_to_home"
    HOVER = "hover"
    LAND_NOW = "land_now"
    HALT_AND_REPORT = "halt_and_report"
    CONTINUE_AUTONOMOUS = "continue_autonomous"


class LinkLossRule(BaseModel):
    """A deployment-declared rule: if ``role`` is lost, perform ``action``.

    Replaces the envelope's old free-form ``link_loss_policy: str``. The
    presence of a rule governing a role *is* the declaration that the
    deployment depends on that link (Pass 2 treats governed roles as
    required).
    """

    model_config = ConfigDict(extra="forbid")

    role: LinkRole
    action: LinkLossAction
    max_outage_seconds: float | None = Field(
        None,
        ge=0,
        description=(
            "Optional per-rule outage tolerance. May only tighten (be <= ) "
            "the manifest's declared tolerance for the same role."
        ),
    )
