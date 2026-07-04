"""RFC-0665: the radius form of `drive` and its structural + envelope rules.

`drive` can name a circular arc two ways: the arc-length form (`distance` + `arc`)
and the radius form (`radius` + `arc`), which are exactly equivalent through
`distance = radius x radians(arc)`. The radius form lets an utterance's radius and
sweep angle pass through without the caller computing an arc length, which is the
arithmetic a small model got wrong in Discussion #572.

These tests exercise the schema one-of (exactly one of distance / radius; radius
needs a non-zero arc) and the envelope check (the per-move distance bound applies
to the arc length the robot travels, for either form).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml

from urml_validator import validate

_MANIFEST_PATH = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "educational"
    / "relative-motion"
    / "buggy.manifest.yaml"
)
# The classroom buggy declares supports_relative_motion: true, max_relative_distance: 2.0.
MANIFEST: dict[str, Any] = yaml.safe_load(_MANIFEST_PATH.read_text(encoding="utf-8"))
PROFILES = ("educational",)


def _program(drive_args: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": ["educational"],
        "behavior": {"type": "sequence", "steps": [{"drive": drive_args}]},
    }


def _validate(drive_args: dict[str, Any]):
    return validate(_program(drive_args), MANIFEST, profiles=PROFILES, policy=None)


def test_radius_form_is_accepted() -> None:
    # "Orbit 180 degrees with a 5 cm radius": the #572 utterance, arithmetic-free.
    assert _validate({"radius": 0.05, "arc": 180}).accepted


def test_arc_length_form_still_accepted() -> None:
    # The RFC-0630 form is unchanged; its meaning does not move.
    assert _validate({"distance": math.pi * 0.05, "arc": 180}).accepted
    assert _validate({"distance": 0.5}).accepted  # straight line
    assert _validate({"distance": 0.5, "arc": 10}).accepted  # gentle arc


def test_radius_and_arc_length_forms_are_equivalent() -> None:
    # distance = radius x radians(arc): the two names for the same 5 cm-radius arc
    # both validate against the same bounded manifest.
    radius_form = _validate({"radius": 0.05, "arc": 180})
    arc_length_form = _validate({"distance": 0.05 * math.radians(180), "arc": 180})
    assert radius_form.accepted and arc_length_form.accepted


def test_both_distance_and_radius_is_rejected() -> None:
    result = _validate({"distance": 0.157, "radius": 0.05, "arc": 180})
    assert not result.accepted
    assert any(e.code_str == "argument.constraint_violation" for e in result.errors)


def test_neither_distance_nor_radius_is_rejected() -> None:
    result = _validate({"arc": 180})
    assert not result.accepted
    assert any(e.code_str == "argument.constraint_violation" for e in result.errors)


def test_radius_without_arc_is_rejected() -> None:
    result = _validate({"radius": 0.05})
    assert not result.accepted
    assert any(e.code_str == "argument.constraint_violation" for e in result.errors)


def test_radius_with_zero_arc_is_rejected() -> None:
    result = _validate({"radius": 0.05, "arc": 0})
    assert not result.accepted
    assert any(e.code_str == "argument.constraint_violation" for e in result.errors)


def test_envelope_bounds_the_radius_form_arc_length() -> None:
    # radius 1.0 m over 180 deg is a pi (~3.14) m arc, past the buggy's 2.0 m bound.
    # The bound must catch the arc length, not the 1.0 m radius (which is under it).
    result = _validate({"radius": 1.0, "arc": 180})
    assert not result.accepted
    assert any(e.code_str == "capability.relative_distance_exceeded" for e in result.errors)


def test_short_radius_arc_is_within_the_bound() -> None:
    # radius 0.05 m over 180 deg is a 0.157 m arc, comfortably within 2.0 m.
    assert _validate({"radius": 0.05, "arc": 180}).accepted
