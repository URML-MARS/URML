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
