"""Shared types used across multiple URML schemas.

These types appear in primitive signatures (`location`, `pose`, `$var`
references), in the manifest (declared frames, declared locations), and in
the envelope (bounded values). Defining them once here keeps the per-layer
schemas thin and consistent.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# A snake_case identifier for primitive names, variable names, location names,
# frame names, etc. The character class is deliberately conservative.
Identifier = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9_]*$", min_length=1, max_length=64),
]

# `$varname` reference to a prior `store_as` binding. The leading `$` is
# required by the URML surface syntax.
_VAR_REF_PATTERN = re.compile(r"^\$[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
VarRef = Annotated[
    str,
    StringConstraints(pattern=r"^\$[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$"),
]


def is_var_ref(s: str) -> bool:
    """Return True if `s` is a syntactically valid `$variable[.field...]` reference."""
    return bool(_VAR_REF_PATTERN.match(s))


# Duration values accept either a number (seconds) or an ISO-8601-like string
# with a units suffix (`30s`, `2m`, `1h`). The model accepts both forms; the
# validator normalises to seconds at check time.
_DURATION_PATTERN = re.compile(r"^\d+(\.\d+)?(s|ms|m|h)$")
Duration = Annotated[
    float | str,
    Field(description="Number of seconds, OR a string like '30s', '2m', '500ms', '1h'."),
]


def is_duration(value: float | str) -> bool:
    """Return True if `value` is a numeric duration or a valid duration string."""
    if isinstance(value, (int, float)):
        return value >= 0
    return bool(_DURATION_PATTERN.match(value))


class Pose(BaseModel):
    """A 6-DOF pose with optional fields.

    `x` and `y` are required; `z`, `yaw`, `pitch`, `roll` are optional and
    profile-specific. Units are SI (metres, radians). The accompanying `frame`
    field on the containing primitive declares the frame these values are
    expressed in.
    """

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    z: float | None = None
    yaw: float | None = None
    pitch: float | None = None
    roll: float | None = None


class Location(BaseModel):
    """A named place from the manifest's declared-locations vocabulary.

    Wraps a string so consumers can distinguish a name-by-reference from
    free-form values. The validator resolves the name against the manifest;
    parsing alone does not.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier


# Many primitives accept either a named location or an explicit pose+frame.
# This alias names that union for readability.
LocationOrPose = str | Pose


class Rotation(BaseModel):
    """A 3D rotation as roll/pitch/yaw Euler angles, in radians (RFC-0290).

    Applied in the ZYX convention (yaw, then pitch, then roll), matching the
    common ROS/aerospace order: R = Rz(yaw) · Ry(pitch) · Rx(roll). The same
    angle vocabulary `Pose` already uses. A future field may accept a quaternion.
    """

    model_config = ConfigDict(extra="forbid")

    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0


class Translation(BaseModel):
    """A 3D translation in metres (RFC-0290)."""

    model_config = ConfigDict(extra="forbid")

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Transform(BaseModel):
    """A rigid-body (SE(3)) transform: a translation plus a rotation (RFC-0290).

    On a `Frame`, it expresses that frame's pose **in its parent frame**: a point
    `p` in the frame maps to the parent as `R · p + t`. As a roster world-anchor,
    it places a member's frame in the shared world frame. Identity (all zeros) is
    the default and means "coincident with the parent / world".
    """

    model_config = ConfigDict(extra="forbid")

    translation: Translation = Field(default_factory=Translation)
    rotation: Rotation = Field(default_factory=Rotation)


class Speed(BaseModel):
    """Speed override: either an absolute value or a fraction of the manifest default.

    Used by `move_to` and `scan`. Fractions are 0..1.
    """

    model_config = ConfigDict(extra="forbid")

    value: float
    units: Literal["m_per_s", "fraction"] = "m_per_s"


class Force(BaseModel):
    """Gripper force: named level or explicit newtons.

    Profile defaults override when omitted on a primitive.
    """

    model_config = ConfigDict(extra="forbid")

    level: Literal["gentle", "firm"] | None = None
    newtons: float | None = None


# Grasp strategies a multi-fingered (dexterous) hand can be asked to perform
# (RFC-0586). Shared between the manifest (a dexterous gripper declares which
# of these it supports) and the `grasp` primitive (an optional `grasp_type`
# selects one, validated against the addressed gripper's declared set). The
# set is the common grasp taxonomy; `custom` is the escape hatch for a hand
# whose strategy does not map onto a standard name.
GraspType = Literal[
    "power",
    "precision",
    "lateral",
    "tripod",
    "pinch",
    "spherical",
    "hook",
    "custom",
]


# RFC-0631: how a capability claim was established. A manifest line ("this robot
# has a movable camera", "this gripper closes to 40 N", "this reach limit is 0.8
# m") is otherwise an unverifiable assertion the validator is forced to trust.
# An `evidence` tag records the claim's source so a reviewer, a tool, or an
# opt-in policy can tell a reviewed contract from a guess.
#
# The four sources, ordered by how checkable the claim is (weakest to strongest):
#
# - inferred  — an LLM or a heuristic guessed it. No external check; a machine's
#   best guess, the weakest class.
# - declared  — asserted by the integrator. No external check; an honest human
#   default.
# - derived   — extracted or computed from a structural robot description (USD /
#   UsdPhysics, URDF, SDF, a vendor asset). The strongest non-runtime evidence.
# - verified  — confirmed by a runtime smoke test or measurement.
EvidenceSource = Literal["inferred", "declared", "derived", "verified"]

# Strength order for an opt-in policy's `min_source` comparison. Higher is
# stronger; a claim with no `evidence` tag at all ranks below `inferred`.
EVIDENCE_SOURCE_RANK: dict[str, int] = {
    "inferred": 0,
    "declared": 1,
    "derived": 2,
    "verified": 3,
}


class EvidenceRef(BaseModel):
    """A structured pointer to the evidence backing a capability claim (RFC-0631).

    `kind` names the evidence's medium so a tool can act on it without parsing a
    free string: a USD prim path, a URDF link, a test identifier, or a URL.
    `value` is the pointer itself (e.g. `/World/robot/gripper`, `wrist_link`, a
    test id, or a https URL). The reference is recorded, not dereferenced: URML
    does not open the USD asset or run the test, it records which one backs the
    claim.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["usd_prim", "urdf_link", "test", "url"]
    value: str = Field(
        ...,
        min_length=1,
        description="The pointer (USD prim path, URDF link name, test id, or URL).",
    )


class Evidence(BaseModel):
    """How a capability claim was established (RFC-0631).

    Optional and advisory: attaching it changes no validation outcome on its
    own. It records the claim's `source` (inferred / declared / derived /
    verified), an optional structured `ref` to the evidence, and optional human
    `note`. An opt-in policy (`Policy.evidence_rules`) can require a minimum
    `source` for a class of capability; without such a policy, evidence is pure
    traceability a reviewer or a tool reads.
    """

    model_config = ConfigDict(extra="forbid")

    source: EvidenceSource
    ref: EvidenceRef | None = None
    note: str | None = None
