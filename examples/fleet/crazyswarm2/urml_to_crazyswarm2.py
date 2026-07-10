#!/usr/bin/env python3
"""Map a validated URML fleet program onto the Crazyswarm2 per-UAV interface.

The worked example from the Crazyswarm2 engagement (IMRCLab/crazyswarm2#864).
@whoenig confirmed Crazyswarm2 supports per-UAV velocity and/or position control,
and that capabilities vary per drone, per operating area, and per swarm size,
which is exactly what URML's fleet model (RFC-0286 roster + RFC-0291 clearance
volumes) is built to carry. So this maps the two together, and only that:

  1. It validates the whole fleet program with ``validate_fleet`` first: every
     primitive against its member's manifest, AND the cross-robot checks, the
     load-bearing one being deconfliction. The three formation corners are
     checked against each Crazyflie's operational-clearance volume; send two
     drones to the same corner and the program is rejected
     (``fleet.concurrent_shared_workspace``) before a single command goes out.

  2. For each validated per-UAV primitive it emits the concrete Crazyswarm2
     interface (the real crazyflie_interfaces services):

       take_off -> /<cf>/takeoff  (crazyflie_interfaces/srv/Takeoff)
       move_to  -> /<cf>/go_to    (crazyflie_interfaces/srv/GoTo). GoTo needs a
                   duration, and @whoenig noted it must be long enough to respect
                   the drone's maximum velocity. URML declares max_velocity in the
                   manifest, so the duration is derived as distance / speed, with
                   speed the commanded move_to.speed if present and otherwise the
                   declared max_velocity, and always capped at max_velocity. The
                   emitted GoTo duration is therefore never shorter than the speed
                   limit allows.
       land     -> /<cf>/land      (crazyflie_interfaces/srv/Land)
       barrier  -> a fleet rendezvous: the runtime holds the next phase until all
                   named members reach completeState (no per-UAV command)

Hermetic (pure stdlib + the URML validator, no ROS 2, no radios, no Crazyflies)
and deterministic, so the committed ``dispatch-plan.txt`` is byte-asserted in CI.
This is the mapping, not a live node: a real flight needs Crazyswarm2 and a
positioning system, and a live rclpy dispatcher fanning the validated intent out
to the per-CF service clients is the natural next step.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate_fleet

_HERE = Path(__file__).resolve().parent
DEFAULT_FLEET = _HERE / "swarm-formation.fleet.yaml"


def _load_fleet(path: Path = DEFAULT_FLEET) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    """Load the two-document fleet file and resolve each member's manifest."""
    roster_doc, program_doc = yaml.safe_load_all(path.read_text(encoding="utf-8"))
    members: dict[str, dict[str, Any]] = {}
    for member in roster_doc.get("members", []):
        manifest_path = _HERE / f"{member['manifest']}.manifest.yaml"
        members[member["name"]] = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return roster_doc, members, program_doc


def _pose(manifest: dict[str, Any], name: str) -> dict[str, float]:
    for loc in manifest.get("declared_locations", []):
        if loc.get("name") == name:
            return loc.get("pose", {})
    raise KeyError(f"location {name!r} is not declared in the member manifest")


def _xyz(pose: dict[str, float]) -> str:
    return "(" + ", ".join(f"{float(pose.get(k, 0.0)):g}" for k in ("x", "y", "z")) + ")"


def _distance(a: dict[str, float], b: dict[str, float]) -> float:
    return math.sqrt(sum((float(a.get(k, 0.0)) - float(b.get(k, 0.0))) ** 2 for k in ("x", "y", "z")))


def _speed_for(args: dict[str, Any], manifest: dict[str, Any]) -> float:
    """The speed a GoTo duration is derived from: the commanded move_to.speed if
    present, else the declared max_velocity, always capped at max_velocity."""
    max_v = float(manifest.get("mobility", {}).get("max_velocity", 0.0))
    s = args.get("speed")
    if isinstance(s, (int, float)):
        v = float(s)
    elif isinstance(s, dict):
        v = float(s.get("value", 0.0)) or max_v
    else:
        v = max_v
    return min(v, max_v) if max_v else v


def _dispatch_line(
    member: str, verb: str, args: dict[str, Any], manifest: dict[str, Any], pos: dict[str, float]
) -> tuple[str, dict[str, float]]:
    """Render one primitive's Crazyswarm2 line and return the member's new position."""
    if verb == "take_off":
        h = args.get("altitude", 0.0)
        new = {"x": pos.get("x", 0.0), "y": pos.get("y", 0.0), "z": float(h)}
        line = f"  {member}: take_off(altitude={h}) -> /{member}/takeoff  (crazyflie_interfaces/srv/Takeoff: height={h})"
        return line, new
    if verb == "move_to":
        loc = args.get("location")
        goal = _pose(manifest, loc)
        dist = _distance(pos, goal)
        v = _speed_for(args, manifest)
        duration = dist / v if v else 0.0
        line = (
            f"  {member}: move_to({loc}) -> /{member}/go_to  "
            f"(crazyflie_interfaces/srv/GoTo: goal={_xyz(goal)}, "
            f"duration={duration:.2f}s = {dist:.2f} m / {v:g} m/s, within max_velocity {v:g})"
        )
        return line, dict(goal)
    if verb == "land":
        new = {"x": pos.get("x", 0.0), "y": pos.get("y", 0.0), "z": 0.0}
        return f"  {member}: land -> /{member}/land  (crazyflie_interfaces/srv/Land)", new
    return f"  {member}: {verb}(...) -> not mapped in this example", pos


def render_dispatch_plan(
    roster_doc: dict[str, Any],
    members: dict[str, dict[str, Any]],
    program_doc: dict[str, Any],
) -> str:
    """Validate the fleet program, then render the Crazyswarm2 dispatch plan.

    Raises ``ValueError`` if ``validate_fleet`` rejects (a deconfliction conflict,
    a member that can't satisfy a primitive, a barrier without ``peer_link``).
    No Crazyswarm2 command is emitted for a rejected program.
    """
    result = validate_fleet(roster_doc, members, program_doc, policy=None)
    if not result.accepted:
        codes = ", ".join(e.code_str for e in result.errors)
        raise ValueError(f"fleet program does not validate; no Crazyswarm2 command dispatched. Errors: {codes}")

    names = ", ".join(m["name"] for m in roster_doc.get("members", []))
    lines = [
        "URML -> Crazyswarm2 dispatch plan",
        f"fleet: {names} (each: Bitcraze Crazyflie nano-quadcopter)",
        "validate_fleet: ACCEPTED",
        "  (cross-robot static gate: the formation corners are deconflicted against each drone's",
        "   clearance volume; no command goes out for a rejected program)",
        "",
    ]
    # Track each member's position so a GoTo duration can be derived from the
    # distance to fly and the declared max_velocity (the point @whoenig raised).
    positions: dict[str, dict[str, float]] = {
        m["name"]: {"x": 0.0, "y": 0.0, "z": 0.0} for m in roster_doc.get("members", [])
    }
    phase = 0
    for step in program_doc.get("behavior", {}).get("steps", []):
        kind = step.get("type")
        if kind == "parallel":
            phase += 1
            lines.append(f"Phase {phase} (parallel, {step.get('complete_when', 'all')}):")
            for branch in step.get("branches", []):
                member = branch["member"]
                verb, args = next(iter((branch.get("body") or {}).items()))
                line, positions[member] = _dispatch_line(member, verb, args or {}, members[member], positions[member])
                lines.append(line)
        elif kind == "barrier":
            ms = ", ".join(step.get("members", []))
            lines.append(f"Barrier [{ms}]: rendezvous; the runtime holds the next phase until all reach completeState")
    return "\n".join(lines) + "\n"


def render_swarm_formation() -> str:
    return render_dispatch_plan(*_load_fleet())


def main() -> None:
    out = _HERE / "dispatch-plan.txt"
    out.write_text(render_swarm_formation(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
