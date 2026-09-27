"""Rulebook schema (RFC-0702, Draft).

A rulebook states what law or an organization allows a robot to do. The
normative format is ``spec/layer-1-hal/rulebook.md``; this module is that
format as pydantic models, and the rulebook pass (``rulebook_engine.py``)
judges programs against them.

Four deployment-time files, four owners: the manifest says what the robot
can do, the safety envelope what the site allows physically, the rulebook
what law and company policy allow, and the compliance policy what the robot
may be made of. A rulebook names places and never draws them; zone names
resolve against the manifest's declared areas and the envelope's zones.

The format constraints the models enforce (spec, *File format*):

1. No expression language: a rule is one of six fixed kinds with flat keys.
2. Unknown keys are rejected at every level.
3. The issuer kind and the source status agree.
4. A deployment rulebook carries only declarations and exceptions; other
   rulebooks never carry them.
5. A government rulebook carries ``reviewed``, a jurisdiction, and a cite
   with a URL on every rule and obligation.
6. Rule and obligation ids share one namespace and are unique in a file.

Checks that need more than one file (duplicate rulebook ids, conflicting
declarations, exceptions to rules in other files) run in the rulebook pass.
A program passing a rulebook is not a legal compliance determination.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)

from urml_validator.schemas.common import Identifier

#: The only rulebook format version v0.1 accepts.
RULEBOOK_VERSION = "0.1"

#: A declaration value, and a value a condition or `require_declared` allows.
#: Strict: a boolean is never an integer, and a quoted number stays a string.
Scalar = StrictStr | StrictInt | StrictBool

#: A number of 0 or more. Integers are accepted; booleans and numeric strings
#: are not, and neither are NaN and infinity.
NonNegativeNumber = Annotated[StrictFloat, Field(ge=0, allow_inf_nan=False)]

#: An integer of 1 or more (booleans are rejected).
PositiveInt = Annotated[StrictInt, Field(ge=1)]

#: The quantities a `cap` rule can bound. The unit is part of the name.
Quantity = Literal["altitude_agl_m", "speed_m_per_s", "grip_force_n"]

IssuerKind = Literal["government", "organization", "deployment"]

SourceStatus = Literal[
    "final_rule",
    "enacted_statute",
    "organization_policy",
    "deployment_declaration",
]

#: The source statuses each issuer kind may declare. There is no status for a
#: proposed rule, so no government rulebook can encode one.
STATUS_FOR_ISSUER: dict[str, frozenset[str]] = {
    "government": frozenset({"final_rule", "enacted_statute"}),
    "organization": frozenset({"organization_policy"}),
    "deployment": frozenset({"deployment_declaration"}),
}

#: Mirrors `Mobility.drive_type` in schemas/manifest.py. A test keeps the two
#: lists equal.
DriveType = Literal[
    "differential",
    "omnidirectional",
    "ackermann",
    "tracked",
    "multirotor",
    "fixed_wing",
    "vtol",
    "manipulator_base",
    "underwater_thrusters",
    "quadruped",
    "biped",
]

#: The Layer-2 primitive names a `forbid_primitive` rule can list: the field
#: names of `Step` in schemas/composition.py. A test keeps the two lists equal.
PrimitiveName = Literal[
    "move_to",
    "drive",
    "turn",
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
    "look_at",
    "gesture",
    "take_off",
    "land",
    "return_to_home",
    "pick_from",
    "place_at",
    "swap_tool",
    "call_program",
    "plan_path",
    "follow_trajectory",
    "set_output",
]

#: Primitives with a name argument, the only ones `names` and `except_names`
#: may filter: call_program (`name`), set_output (`output`), gesture (`name`).
NAMED_PRIMITIVES: frozenset[str] = frozenset({"call_program", "set_output", "gesture"})

#: The six rule kinds. A rule carries exactly one of these keys.
RULE_KINDS: tuple[str, ...] = (
    "cap",
    "forbid_primitive",
    "forbid_zone_entry",
    "forbid_over_people",
    "require_declared",
    "max_concurrent_aircraft",
)

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RULE_REF = re.compile(r"^([a-z][a-z0-9_]{0,63})/([a-z][a-z0-9_]{0,63})$")


def _iso_date(value: object) -> object:
    """A date is an ISO-8601 calendar date written as a quoted string."""
    if isinstance(value, date):
        raise ValueError(
            'write the date as a quoted string, for example "2026-09-26"; '
            "YAML reads an unquoted date as a date object"
        )
    if isinstance(value, str):
        if not _ISO_DATE.match(value):
            raise ValueError(f"{value!r} is not an ISO-8601 date (YYYY-MM-DD)")
        date.fromisoformat(value)  # rejects impossible dates such as 2026-02-30
    return value


#: An ISO-8601 calendar date, written as a quoted YAML string.
IsoDate = Annotated[StrictStr, BeforeValidator(_iso_date)]


class _Strict(BaseModel):
    """Base for every rulebook model: unknown keys are rejected."""

    model_config = ConfigDict(extra="forbid")


class Cite(_Strict):
    """The source a rule, an obligation or a condition encodes."""

    text: StrictStr = Field(..., min_length=1, description="Citation text, for example `14 CFR 107.51(b)`.")
    url: StrictStr | None = Field(None, description="Where the cited text can be read.")


class Condition(_Strict):
    """Holds when the merged deployment declarations have `key` with a value in `allowed`."""

    key: Identifier
    allowed: list[Scalar] = Field(..., min_length=1)
    cite: Cite | None = None


class Issuer(_Strict):
    """Who issued the rules: a government, an organization, or the operator (deployment)."""

    kind: IssuerKind
    name: StrictStr = Field(..., min_length=1)
    jurisdiction: StrictStr | None = Field(
        None, description="Required for a government rulebook, for example `US`."
    )

    @model_validator(mode="after")
    def _jurisdiction_for_government(self) -> Issuer:
        if self.kind == "government" and not self.jurisdiction:
            raise ValueError("a government issuer names its jurisdiction")
        return self


class AppliesTo(_Strict):
    """When a rulebook is in scope, and the declarations that switch it off."""

    profiles: list[Identifier] | None = None
    drive_types: list[DriveType] | None = None
    unless_declared: list[Condition] | None = None


# ---------------------------------------------------------------------------
# Rule kinds
# ---------------------------------------------------------------------------


class CapBody(_Strict):
    """A value the program states that is above `max` violates the rule."""

    quantity: Quantity
    max: NonNegativeNumber


class ForbidPrimitiveBody(_Strict):
    """A step that uses a listed primitive violates the rule, optionally only by name or in zones."""

    primitives: list[PrimitiveName] = Field(..., min_length=1)
    in_zones: list[Identifier] | None = None
    names: list[Identifier] | None = None
    except_names: list[Identifier] | None = None

    @model_validator(mode="after")
    def _name_filters(self) -> ForbidPrimitiveBody:
        if self.names is not None and self.except_names is not None:
            raise ValueError("names and except_names are mutually exclusive")
        for key in ("names", "except_names"):
            values = getattr(self, key)
            if values is None:
                continue
            if not values:
                raise ValueError(f"{key} is non-empty when present")
            unnamed = [p for p in self.primitives if p not in NAMED_PRIMITIVES]
            if unnamed:
                raise ValueError(
                    f"{key} is allowed only when every listed primitive has a name argument "
                    f"(call_program, set_output, gesture); {', '.join(unnamed)} has none"
                )
        return self


class ForbidZoneEntryBody(_Strict):
    """A step that sends the robot to a place in one of the zones violates the rule."""

    zones: list[Identifier] = Field(..., min_length=1)


class ForbidOverPeopleBody(_Strict):
    """An aircraft target in a people-occupancy zone violates the rule, unless a condition holds."""

    unless_declared: list[Condition] | None = None


class RequireDeclaredBody(_Strict):
    """A deployment rulebook declares `key`, with a value in `allowed` when it is given."""

    key: Identifier
    allowed: list[Scalar] | None = None


class MaxConcurrentAircraftBody(_Strict):
    """How many aircraft a fleet program may have airborne at once."""

    max: PositiveInt | None = None
    max_per_remote_pilot: PositiveInt | None = None

    @model_validator(mode="after")
    def _exactly_one_limit(self) -> MaxConcurrentAircraftBody:
        if (self.max is None) == (self.max_per_remote_pilot is None):
            raise ValueError("max_concurrent_aircraft takes exactly one of max or max_per_remote_pilot")
        return self


class Rule(_Strict):
    """One rule: common fields plus exactly one kind key."""

    id: Identifier
    title: StrictStr
    cite: Cite | None = None
    exceptable: StrictBool = False
    note: StrictStr | None = None

    cap: CapBody | None = None
    forbid_primitive: ForbidPrimitiveBody | None = None
    forbid_zone_entry: ForbidZoneEntryBody | None = None
    forbid_over_people: ForbidOverPeopleBody | None = None
    require_declared: RequireDeclaredBody | None = None
    max_concurrent_aircraft: MaxConcurrentAircraftBody | None = None

    @model_validator(mode="before")
    @classmethod
    def _exactly_one_kind(cls, data: Any) -> Any:
        if isinstance(data, dict):
            present = [kind for kind in RULE_KINDS if kind in data]
            if len(present) != 1:
                raise ValueError(
                    f"a rule carries exactly one kind key ({', '.join(RULE_KINDS)}); "
                    f"got {', '.join(present) if present else 'none'}"
                )
            if data[present[0]] is None:
                raise ValueError(f"the {present[0]} body is a mapping; write {{}} when it has no keys")
        return data

    @property
    def kind(self) -> str:
        """The rule's kind key."""
        for kind in RULE_KINDS:
            if getattr(self, kind) is not None:
                return kind
        raise AssertionError("unreachable: _exactly_one_kind leaves exactly one kind key")


class Obligation(_Strict):
    """A rule a static check cannot judge. Listed in every report, never checked."""

    id: Identifier
    title: StrictStr
    text: StrictStr | None = None
    cite: Cite


class RuleException(_Strict):
    """A deployment's recorded exception to one exceptable rule.

    `limit` is required for cap and max_concurrent_aircraft rules and not
    allowed for other kinds; the rulebook pass checks it against the rule it
    names, because that rule lives in another file.
    """

    rule: StrictStr = Field(..., description="`<rulebook_id>/<rule_id>`.")
    basis: StrictStr = Field(..., min_length=1, description="The legal or organizational basis.")
    limit: Annotated[StrictInt, Field(ge=0)] | NonNegativeNumber | None = None
    expires: IsoDate | None = None

    @field_validator("rule")
    @classmethod
    def _rule_reference(cls, value: str) -> str:
        if not _RULE_REF.match(value):
            raise ValueError(f"rule is `<rulebook_id>/<rule_id>`, two identifiers; got {value!r}")
        return value

    @field_validator("basis")
    @classmethod
    def _basis_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("basis names the legal or organizational basis; it is not blank")
        return value

    @property
    def rulebook_id(self) -> str:
        return self.rule.split("/", 1)[0]

    @property
    def rule_id(self) -> str:
        return self.rule.split("/", 1)[1]


class Rulebook(_Strict):
    """A complete rulebook file (spec/layer-1-hal/rulebook.md)."""

    rulebook_version: Literal["0.1"]
    rulebook_id: Identifier
    title: StrictStr = Field(..., min_length=1)
    issuer: Issuer
    maintained_by: StrictStr | None = None
    source_status: SourceStatus
    effective: IsoDate | None = None
    reviewed: IsoDate | None = None
    description: StrictStr | None = None
    applies_to: AppliesTo | None = None
    rules: list[Rule] = Field(default_factory=list)
    obligations: list[Obligation] = Field(default_factory=list)
    declarations: dict[Identifier, Scalar] | None = None
    exceptions: list[RuleException] | None = None

    @model_validator(mode="after")
    def _coherent(self) -> Rulebook:
        kind = self.issuer.kind
        if self.source_status not in STATUS_FOR_ISSUER[kind]:
            allowed = " or ".join(sorted(STATUS_FOR_ISSUER[kind]))
            raise ValueError(
                f"a {kind} rulebook has source_status {allowed}, not {self.source_status}"
            )
        present = self.model_fields_set
        carried: list[str]
        if kind == "deployment":
            carried = [key for key in ("applies_to", "rules", "obligations") if key in present]
            if carried:
                raise ValueError(
                    "a deployment rulebook carries only declarations and exceptions, "
                    f"not {', '.join(carried)}"
                )
        else:
            carried = [key for key in ("declarations", "exceptions") if key in present]
            if carried:
                raise ValueError(
                    f"only a deployment rulebook carries declarations and exceptions; "
                    f"this {kind} rulebook carries {', '.join(carried)}"
                )
        entries: list[Rule | Obligation] = [*self.rules, *self.obligations]
        if kind == "government":
            if self.reviewed is None:
                raise ValueError("a government rulebook carries reviewed, the date its text was last checked")
            uncited = [entry.id for entry in entries if entry.cite is None or not entry.cite.url]
            if uncited:
                raise ValueError(
                    "every rule and obligation of a government rulebook carries a cite "
                    f"with a url; missing on {', '.join(uncited)}"
                )
        ids = [entry.id for entry in entries]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(
                f"rule and obligation ids share one namespace and are unique; "
                f"duplicated: {', '.join(duplicates)}"
            )
        return self

    def rule(self, rule_id: str) -> Rule | None:
        """The rule with this id, or None."""
        return next((r for r in self.rules if r.id == rule_id), None)
