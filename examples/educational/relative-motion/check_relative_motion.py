#!/usr/bin/env python3
"""RFC-0630: relative motion (`drive` / `turn`) on a frameless educational buggy.

The worked example from Discussion #497: a frameless two-motor, wheel-encoder
robot (a GoPiGo3) whose natural vocabulary is "drive forward X" and "spin X
degrees". URML expresses that with the `turn` and `drive` primitives, gated by
the `educational` profile and the `mobility.supports_relative_motion` capability
so the validator still refuses motion a robot cannot perform.

This script validates a four-corner square program against the buggy, then shows
the ways the gate rejects misuse: the wrong profile, a robot that does not declare
relative motion, and a drive past the declared distance bound. It also shows the
RFC-0665 radius form (`drive: {radius, arc}`), which names an arc by its radius and
sweep angle so a curved drive needs no arc-length arithmetic (the factor-of-2 slip
from Discussion #572), bounded by the arc length it travels. It is hermetic (the
validator only, no robot) and deterministic, so the committed
``relative-motion-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "buggy.manifest.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _square_program() -> dict[str, Any]:
    """Drive a square: at each corner, turn 90 then drive a side; one side is an arc."""
    side = {"drive": {"distance": 0.5}}
    corner = {"turn": {"angle": 90}}
    return {
        "profile": ["educational"],
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                side,
                corner,
                side,
                corner,
                {"drive": {"distance": 0.5, "arc": 10}},  # a gently curved side
                corner,
                side,
            ],
        },
    }


def _emit(lines: list[str], label: str, program: dict[str, Any], manifest: dict[str, Any], profiles: tuple[str, ...]) -> None:
    result = validate(program, manifest, profiles=profiles, policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] {label}")
    if not result.accepted:
        codes = ", ".join(sorted({e.code_str for e in result.errors}))
        lines.append(f"   -> {codes}")
    lines.append("")


def render_report() -> str:
    manifest = _load(MANIFEST)
    lines = [
        "URML relative motion on a frameless educational buggy (RFC-0630, RFC-0665).",
        "`drive` / `turn` are gated by the educational profile and the",
        "mobility.supports_relative_motion capability; the validator refuses misuse.",
        "An arc can be named by path length (`distance`) or by radius (RFC-0665).",
        f"robot: {manifest['robot_id']}   drive_type: {manifest['mobility']['drive_type']}",
        "",
    ]

    prog = _square_program()

    # 1. The happy path: educational profile + a relative-motion-capable buggy.
    _emit(lines, "educational buggy drives a square (turn 90 + drive 0.5 m, one arc side)", prog, manifest, ("educational",))

    # 2. Wrong profile: drive/turn are educational-only for now.
    _emit(lines, "same program, but the educational profile is not active", prog, manifest, ())

    # 3. A robot that does not declare relative motion.
    no_cap = copy.deepcopy(manifest)
    no_cap["mobility"]["supports_relative_motion"] = False
    _emit(lines, "a robot that does not declare supports_relative_motion", prog, no_cap, ("educational",))

    # 4. A drive past the declared per-move distance bound (max_relative_distance = 2.0 m).
    too_far = {
        "profile": ["educational"],
        "behavior": {"type": "sequence", "steps": [{"drive": {"distance": 5.0}}]},
    }
    _emit(lines, "a single drive of 5.0 m past the 2.0 m bound", too_far, manifest, ("educational",))

    # 5. RFC-0665: the radius form. "Orbit 180 degrees with a 5 cm radius" is
    # `drive: {radius: 0.05, arc: 180}`, the two numbers the utterance gives, with
    # no arc-length arithmetic (the factor-of-2 slip from Discussion #572).
    radius_form = {
        "profile": ["educational"],
        "behavior": {"type": "sequence", "steps": [{"drive": {"radius": 0.05, "arc": 180}}]},
    }
    _emit(lines, "radius form: orbit 180 degrees at a 5 cm radius (RFC-0665)", radius_form, manifest, ("educational",))

    # 6. The radius form is bounded by the arc length it travels, not the radius: a
    # 1.0 m radius over 180 degrees is a pi (~3.14) m arc, past the 2.0 m bound.
    radius_too_far = {
        "profile": ["educational"],
        "behavior": {"type": "sequence", "steps": [{"drive": {"radius": 1.0, "arc": 180}}]},
    }
    _emit(lines, "radius form bounded by arc length: 1.0 m radius over 180 deg is a 3.14 m arc, past 2.0 m", radius_too_far, manifest, ("educational",))

    # 7. Exactly one of distance / radius: giving both is rejected before any robot moves.
    both = {
        "profile": ["educational"],
        "behavior": {"type": "sequence", "steps": [{"drive": {"distance": 0.157, "radius": 0.05, "arc": 180}}]},
    }
    _emit(lines, "both distance and radius given (overspecified) is rejected", both, manifest, ("educational",))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "relative-motion-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
