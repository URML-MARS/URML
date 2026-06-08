#!/usr/bin/env python3
"""Export a validated URML navigation program to an ASAM OpenSCENARIO (.xosc) run.

This is the worked example from the esmini engagement (esmini/esmini#816). The
esmini maintainer (@eknabevcc) confirmed that OpenSCENARIO's road-user action
model (change speed, follow a route) lines up with URML's mobility layer, and
that the meaningful first cut is "a URML-governed ground agent driving its
validated navigation intent as the controlled entity under a scenario."

So this script does exactly that, and only that:

  1. It validates the URML program against its capability manifest first
     (URML's whole point: reject inadmissible intent before anything runs).
  2. It maps each validated `move_to` to an OpenSCENARIO event that acquires the
     waypoint's world position, at the manifest's declared cruise speed, chained
     in program order. The URML agent is the single controlled `ScenarioObject`.

What this is NOT: a co-simulation bridge. Driving the entity at runtime through
esmini's external-controller interface is the deeper integration and is left for
later. Generating the scenario from validated intent is the honest first cut, and
it is fully hermetic (pure stdlib XML, no esmini and no network needed to
produce the .xosc). Playing it needs esmini plus an OpenDRIVE road network; see
the README.

Deterministic by construction (fixed FileHeader date), so the committed
``husky-patrol.xosc`` can be byte-asserted against this generator in CI, the same
discipline the README hero SVG uses.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

# Fixed so the output is byte-deterministic (CI byte-asserts the committed file).
_FILEHEADER_DATE = "2026-01-01T00:00:00"
_OSC_REV = ("1", "2")  # OpenSCENARIO 1.2

_EXAMPLES = Path(__file__).resolve().parents[1]
DEFAULT_PROGRAM = _EXAMPLES / "mobile" / "husky-patrol.urml.yaml"
DEFAULT_MANIFEST = _EXAMPLES / "mobile" / "husky-patrol.manifest.yaml"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _iter_move_to(behavior: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a behavior tree to its ordered ``move_to`` steps."""
    out: list[dict[str, Any]] = []
    for step in behavior.get("steps", []):
        if not isinstance(step, dict):
            continue
        if "move_to" in step:
            out.append(step["move_to"] or {})
        # Recurse into nested composition nodes (sequence/branch/parallel/retry).
        for key in ("sequence", "branch", "parallel", "retry"):
            if isinstance(step.get(key), dict):
                out.extend(_iter_move_to(step[key]))
        if step.get("type") and "steps" in step:
            out.extend(_iter_move_to(step))
    return out


def _location_pose(manifest: dict[str, Any], name: str) -> dict[str, float]:
    for loc in manifest.get("declared_locations", []):
        if loc.get("name") == name:
            return loc.get("pose", {})
    raise KeyError(f"location {name!r} is not a declared_location in the manifest")


def _world_position(pose: dict[str, float]) -> ET.Element:
    el = ET.Element("WorldPosition")
    el.set("x", _num(pose.get("x", 0.0)))
    el.set("y", _num(pose.get("y", 0.0)))
    el.set("z", _num(pose.get("z", 0.0)))
    el.set("h", "0")
    return el


def _num(v: float) -> str:
    return f"{float(v):g}"


def _sim_time_trigger(name: str) -> ET.Element:
    """A trigger that fires once on the first simulation step."""
    st = ET.Element("StartTrigger")
    cg = ET.SubElement(st, "ConditionGroup")
    cond = ET.SubElement(cg, "Condition", name=name, delay="0", conditionEdge="none")
    bv = ET.SubElement(cond, "ByValueCondition")
    ET.SubElement(bv, "SimulationTimeCondition", value="0", rule="greaterThan")
    return st


def _after_event_trigger(name: str, prev_event: str) -> ET.Element:
    """A trigger that fires when the previous event completes (program 'then')."""
    st = ET.Element("StartTrigger")
    cg = ET.SubElement(st, "ConditionGroup")
    cond = ET.SubElement(cg, "Condition", name=name, delay="0", conditionEdge="none")
    bs = ET.SubElement(cond, "ByValueCondition")
    ET.SubElement(
        bs,
        "StoryboardElementStateCondition",
        storyboardElementType="event",
        storyboardElementRef=prev_event,
        state="completeState",
    )
    return st


def render_xosc(program: dict[str, Any], manifest: dict[str, Any]) -> str:
    """Validate the program, then render the OpenSCENARIO XML as a string.

    Raises ``ValueError`` if the URML program does not validate against the
    manifest. URML emits a scenario only for admissible intent.
    """
    result = validate(program, manifest, {}, policy=None)
    if not result.accepted:
        codes = ", ".join(e.code_str for e in result.errors)
        raise ValueError(f"URML program does not validate; refusing to emit a scenario. Errors: {codes}")

    behavior = program.get("behavior", {})
    moves = _iter_move_to(behavior)
    if not moves:
        raise ValueError("program has no move_to steps; nothing to map onto an OpenSCENARIO route")

    mobility = manifest.get("mobility", {}) or {}
    cruise = float(mobility.get("max_velocity", 1.0))
    robot_id = str(manifest.get("robot_id", "urml_agent"))

    root = ET.Element("OpenSCENARIO")
    ET.SubElement(
        root,
        "FileHeader",
        revMajor=_OSC_REV[0],
        revMinor=_OSC_REV[1],
        date=_FILEHEADER_DATE,
        description=f"URML-governed agent under an OpenSCENARIO run ({robot_id})",
        author="URML (urml.dev)",
    )
    ET.SubElement(root, "ParameterDeclarations")
    ET.SubElement(root, "CatalogLocations")
    road = ET.SubElement(root, "RoadNetwork")
    # esmini needs an OpenDRIVE network to play this; point it at any flat road.
    ET.SubElement(road, "LogicFile", filepath="straight_500m.xodr")

    # --- Entities: the single URML-governed controlled object ---------------
    entities = ET.SubElement(root, "Entities")
    obj = ET.SubElement(entities, "ScenarioObject", name="urml_agent")
    veh = ET.SubElement(obj, "Vehicle", name=robot_id, vehicleCategory="car")
    bb = ET.SubElement(veh, "BoundingBox")
    ET.SubElement(bb, "Center", x="0", y="0", z="0.2")
    ET.SubElement(bb, "Dimensions", width="0.67", length="0.99", height="0.39")
    ET.SubElement(
        veh, "Performance", maxSpeed=_num(cruise), maxDeceleration="3.0", maxAcceleration="2.0"
    )
    axles = ET.SubElement(veh, "Axles")
    ET.SubElement(
        axles, "FrontAxle", maxSteering="0.5", wheelDiameter="0.33", trackWidth="0.55",
        positionX="0.33", positionZ="0.165",
    )
    ET.SubElement(
        axles, "RearAxle", maxSteering="0.0", wheelDiameter="0.33", trackWidth="0.55",
        positionX="0.0", positionZ="0.165",
    )
    ET.SubElement(veh, "Properties")

    # --- Storyboard ---------------------------------------------------------
    sb = ET.SubElement(root, "Storyboard")
    init = ET.SubElement(sb, "Init")
    init_actions = ET.SubElement(init, "Actions")
    priv = ET.SubElement(init_actions, "Private", entityRef="urml_agent")
    # Start at the origin of the manifest's world frame, stationary, then bring
    # the agent up to its declared cruise speed.
    tp = ET.SubElement(priv, "PrivateAction")
    tpa = ET.SubElement(tp, "TeleportAction")
    pos = ET.SubElement(tpa, "Position")
    pos.append(_world_position({"x": 0.0, "y": 0.0, "z": 0.0}))
    spd = ET.SubElement(priv, "PrivateAction")
    la = ET.SubElement(spd, "LongitudinalAction")
    sa = ET.SubElement(la, "SpeedAction")
    ET.SubElement(sa, "SpeedActionDynamics", dynamicsShape="step", value="0", dynamicsDimension="time")
    sat = ET.SubElement(sa, "SpeedActionTarget")
    ET.SubElement(sat, "AbsoluteTargetSpeed", value=_num(cruise))

    story = ET.SubElement(sb, "Story", name="urml_navigation_story")
    act = ET.SubElement(story, "Act", name="urml_navigation_act")
    mg = ET.SubElement(act, "ManeuverGroup", maximumExecutionCount="1", name="urml_agent_group")
    actors = ET.SubElement(mg, "Actors", selectTriggeringEntities="false")
    ET.SubElement(actors, "EntityRef", entityRef="urml_agent")
    maneuver = ET.SubElement(mg, "Maneuver", name="urml_navigation")

    prev_event: str | None = None
    for i, move in enumerate(moves):
        loc = move.get("location")
        if loc is None:
            raise ValueError(f"move_to step {i} has no `location`; raw pose goals are out of scope for this example")
        pose = _location_pose(manifest, loc)
        ev_name = f"goto_{loc}"
        event = ET.SubElement(maneuver, "Event", name=ev_name, priority="overwrite")
        action = ET.SubElement(event, "Action", name=f"acquire_{loc}")
        pa = ET.SubElement(action, "PrivateAction")
        ra = ET.SubElement(pa, "RoutingAction")
        apa = ET.SubElement(ra, "AcquirePositionAction")
        apos = ET.SubElement(apa, "Position")
        apos.append(_world_position(pose))
        if prev_event is None:
            event.append(_sim_time_trigger(f"start_{ev_name}"))
        else:
            event.append(_after_event_trigger(f"start_{ev_name}", prev_event))
        prev_event = ev_name

    act.append(_sim_time_trigger("urml_act_start"))
    ET.SubElement(sb, "StopTrigger")

    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + body + "\n"


def render_husky_patrol() -> str:
    """Render the committed example (examples/mobile/husky-patrol)."""
    return render_xosc(_load(DEFAULT_PROGRAM), _load(DEFAULT_MANIFEST))


def main() -> None:
    out = _EXAMPLES / "scenario" / "husky-patrol.xosc"
    out.write_text(render_husky_patrol(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
