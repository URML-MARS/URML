#!/usr/bin/env python3
"""Declare a mission, validate it, then compile it to an INAV waypoint mission.

The worked example from the iNavFlight/inav engagement
(iNavFlight/inav#11651). The maintainer (sensei-hacker) restated URML's role
exactly: a human or LLM states the goal and the constraints (geofence, limits),
URML checks the aircraft can fly it, and then compiles the result into an INAV
mission. He also flagged that physical limits (minimum turn radius) and INAV
capabilities (return-to-home) are what such a check should leverage.

This script is that flow, hermetically. It reads the aircraft manifest and the
safety envelope, validates each mission, and for an admissible one compiles the
URML program into an INAV waypoint mission (WAYPOINT / RTH / LAND). For an
inadmissible one (a leg that crosses the road, i.e. leaves the geofence) it stops
at validation and never compiles. return_to_home maps to INAV's RTH; the
"don't cross the road" constraint is a geofence the validator enforces (Pass 3)
before any waypoint is emitted.

Minimum turn radius is a fixed-wing kinodynamic limit URML does not yet declare;
see the README for where it would slot in (a manifest field, parallel to
RFC-0518) and become a pre-compile check. It is not invented here.

It is hermetic (the validator only, no flight controller) and deterministic, so
the committed `inav-mission-report.txt` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "inav-aircraft.manifest.yaml"
ENVELOPE = _HERE / "mission.envelope.yaml"
MISSIONS = _HERE / "missions.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def compile_inav(program: dict[str, Any], locations: dict[str, dict[str, float]]) -> list[str]:
    """Map a validated URML program onto INAV waypoint-mission lines."""
    wps: list[str] = []
    n = 0
    for step in program["behavior"]["steps"]:
        verb, args = next(iter(step.items()))
        args = args or {}
        if verb == "take_off":
            wps.append(f"  launch     climb to {float(args.get('altitude', 0.0))} m AGL")
        elif verb == "move_to":
            p = locations[args["location"]]
            n += 1
            wps.append(f"  WP{n}  WAYPOINT  x={p.get('x', 0.0)} y={p.get('y', 0.0)} alt={p.get('z', 0.0)}")
        elif verb == "return_to_home":
            n += 1
            wps.append(f"  WP{n}  RTH")
        elif verb == "land":
            n += 1
            wps.append(f"  WP{n}  LAND")
    return wps


def render_report() -> str:
    manifest = _load(MANIFEST)
    envelope = _load(ENVELOPE)
    missions = _load(MISSIONS)["missions"]
    locations = {loc["name"]: loc["pose"] for loc in manifest["declared_locations"]}

    lines = [
        "URML mission -> validate -> compile to an INAV waypoint mission.",
        "Geofence ('don't cross the road') is enforced before any waypoint is emitted.",
        f"aircraft: {manifest['robot_id']}  |  envelope: {envelope['deployment_id']}",
        "",
    ]
    for m in missions:
        result = validate(m["program"], manifest, envelope, policy=None)
        if result.accepted:
            lines.append(f"[COMPILED] {m['label']}")
            lines += compile_inav(m["program"], locations)
        else:
            codes = ", ".join(e.code_str for e in result.errors)
            lines.append(f"[REJECTED] {m['label']}")
            lines.append(f"   refused at validation [{codes}]; nothing compiled to INAV.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "inav-mission-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
