#!/usr/bin/env python3
"""Validate a drone command against a declared envelope, then hand it to gym-pybullet-drones.

For learnsyslab/gym-pybullet-drones#312. @JacopoPan noted the repo's design driver
is KISS, so this stays frugal and adds NOTHING to that repo: it imports nothing
from gym-pybullet-drones, and gym-pybullet-drones imports nothing from URML. The
gate lives entirely on the URML side.

URML declares what the quadcopter can do (quadcopter.manifest.yaml: an aerial
multirotor with a service ceiling and a speed limit) and a deployment declares the
arena it may fly in (arena.envelope.yaml: a 3 by 3 m box with a 2.5 m altitude
cap). A commanded flight is validated against both before any target is handed to
the gym-pybullet-drones control interface. An out-of-arena or too-high command is
refused statically, with no PyBullet and no drone.

The flight is a minimal one: take off, go to a waypoint, land. The example
validates it three ways, then shows the admissible flight mapped onto the target
positions a gym-pybullet-drones position controller (for example DSLPIDControl)
would fly to. Hermetic and deterministic (validator only), so the committed
``gym-pybullet-drones-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "quadcopter.manifest.yaml"
ENVELOPE = _HERE / "arena.envelope.yaml"
_PROFILES = ("drone",)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _flight(takeoff_alt: float, waypoint: tuple[float, float, float]) -> dict[str, Any]:
    """Take off, fly to a waypoint, land. The command a policy or an operator issues."""
    wx, wy, wz = waypoint
    return {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"take_off": {"altitude": takeoff_alt}},
                {"move_to": {"pose": {"x": wx, "y": wy, "z": wz}, "frame": "world"}},
                {"land": {}},
            ],
        },
    }


def _codes(result: Any) -> list[str]:
    return sorted({e.code_str for e in result.errors})


def _control_plan(flight: dict[str, Any]) -> list[str]:
    """Map the admissible flight onto gym-pybullet-drones control targets."""
    lines = [
        "# The admissible flight, handed to the gym-pybullet-drones control interface",
        "",
        "Each validated primitive becomes a target position for the drone's position",
        "controller (e.g. DSLPIDControl.computeControlFromState(state, target_pos)),",
        "which gym-pybullet-drones turns into motor RPMs and steps. URML never imports",
        "gym-pybullet-drones; it only decides which targets are admissible to send.",
        "",
    ]
    pos = [0.0, 0.0, 0.0]  # start on the home pad
    for step in flight["behavior"]["steps"]:
        verb, args = next(iter(step.items()))
        if verb == "take_off":
            pos = [0.0, 0.0, float(args["altitude"])]
            lines.append(f"  take_off(altitude={args['altitude']})  ->  target_pos = ({pos[0]:g}, {pos[1]:g}, {pos[2]:g})")
        elif verb == "move_to":
            p = args["pose"]
            pos = [float(p["x"]), float(p["y"]), float(p["z"])]
            lines.append(f"  move_to({pos[0]:g}, {pos[1]:g}, {pos[2]:g})       ->  target_pos = ({pos[0]:g}, {pos[1]:g}, {pos[2]:g})")
        elif verb == "land":
            pos = [pos[0], pos[1], 0.0]
            lines.append(f"  land                    ->  target_pos = ({pos[0]:g}, {pos[1]:g}, {pos[2]:g})")
    return lines


def render_report() -> str:
    manifest = _load(MANIFEST)
    envelope = _load(ENVELOPE)

    admissible = _flight(1.5, (1.0, 1.0, 1.5))
    too_high = _flight(3.0, (1.0, 1.0, 1.5))          # take_off above the 2.5 m arena cap
    out_of_arena = _flight(1.5, (5.0, 5.0, 1.5))      # waypoint outside the 3x3 m box

    lines = [
        "URML validate-before-actuate gate for a gym-pybullet-drones quadcopter (#312).",
        "URML declares the drone (aerial multirotor, 5 m ceiling, 2 m/s) and the arena",
        "envelope (3x3 m box, 2.5 m cap), and validates a command against both before any",
        "target reaches the gym-pybullet-drones controller. Nothing is added to that repo.",
        "",
        "Flight: take off, fly to a waypoint, land.",
        "",
        "# 1. An admissible flight (inside the arena, under the cap)",
        "",
    ]

    ok = validate(admissible, manifest, envelope=envelope, profiles=_PROFILES, policy=None)
    lines.append(f"[{'VALID' if ok.accepted else 'REJECTED'}] take off 1.5 m, go to (1, 1, 1.5), land")
    if ok.accepted:
        lines.append("   Every step is within the aircraft's capability and the arena envelope.")
    else:
        lines.append("   -> " + ", ".join(_codes(ok)))
    lines.append("")

    lines += ["# 2. Too high: take-off altitude above the arena cap", ""]
    hi = validate(too_high, manifest, envelope=envelope, profiles=_PROFILES, policy=None)
    lines.append(f"[{'VALID' if hi.accepted else 'REJECTED'}] take off 3.0 m (arena cap is 2.5 m)")
    lines.append("   -> " + ", ".join(_codes(hi)))
    lines.append("   3.0 m is within the 5 m service ceiling but above the arena's 2.5 m cap, so")
    lines.append("   the deployment envelope refuses it. The command never reaches the controller.")
    lines.append("")

    lines += ["# 3. Out of bounds: a waypoint outside the arena footprint", ""]
    oob = validate(out_of_arena, manifest, envelope=envelope, profiles=_PROFILES, policy=None)
    lines.append(f"[{'VALID' if oob.accepted else 'REJECTED'}] fly to (5, 5, 1.5), outside the 3x3 m box")
    lines.append("   -> " + ", ".join(_codes(oob)))
    lines.append("   The waypoint is outside the declared geofence, so it is refused statically.")
    lines.append("")

    lines += _control_plan(admissible)

    lines += [
        "",
        "# The point",
        "",
        "The gate is on the URML side and adds nothing to gym-pybullet-drones. A command",
        "is checked against the declared aircraft and arena first; only an admissible one",
        "is turned into a target for the position controller. Frugal, and validate before",
        "actuate.",
    ]

    assert ok.accepted, "the in-arena flight should be admissible"
    assert not hi.accepted and "envelope.altitude_exceeded" in _codes(hi), "too-high must be refused"
    assert not oob.accepted and "envelope.geofence_violation" in _codes(oob), "out-of-arena must be refused"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "gym-pybullet-drones-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
