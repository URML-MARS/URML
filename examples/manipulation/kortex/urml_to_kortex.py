#!/usr/bin/env python3
"""Map a validated URML manipulation program onto the ros2_kortex ROS 2 surface.

The worked example from the Kinova engagement (Kinovarobotics/ros2_kortex#413).
@aalmrad asked for "a concrete example of URML interacting with the ros2_kortex
driver and how the validated-intent workflow maps onto the existing ROS 2
interfaces." So this does exactly that, and only that:

  1. It validates the URML manipulation program against the Kinova Gen3
     capability manifest first. URML's whole point is the static gate: an
     inadmissible program (a grasp force above the gripper's rating, an
     undeclared gripper, an object the gripper cannot take) is rejected here,
     and no ROS 2 action goal is ever dispatched.

  2. For each validated primitive it emits the concrete ros2_kortex interface
     it dispatches to, with the goal fields that come from the program and the
     manifest. The mapping uses the real ros2_kortex controllers:

       move_to  -> MoveIt 2 (kortex_moveit_config) plans to the declared pose,
                   executed via the joint_trajectory_controller's
                   follow_joint_trajectory action (control_msgs/FollowJointTrajectory)
       grasp    -> robotiq_gripper_controller/gripper_cmd
                   (control_msgs/action/GripperCommand): close at a bounded effort
       release  -> robotiq_gripper_controller/gripper_cmd: open at zero effort
       detect   -> perception (the wrist_rgb camera); not a Kortex motion action

What this is NOT: a live ROS 2 node. Generating the dispatch plan is hermetic
(pure stdlib + the URML validator, no ROS 2 and no Kinova hardware). Running it
on a real Gen3 needs ros2_kortex + MoveIt 2; the inverse kinematics and
trajectory planning are substrate-side. URML declares the goal pose and the
force bound; ros2_kortex and its controllers execute.

Deterministic by construction, so the committed ``dispatch-plan.txt`` is
byte-asserted against this generator in CI (the README hero / esmini discipline).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
DEFAULT_PROGRAM = _HERE / "pick-place.urml.yaml"
DEFAULT_MANIFEST = _HERE / "kinova-gen3.manifest.yaml"

_JTC = "joint_trajectory_controller/follow_joint_trajectory (control_msgs/action/FollowJointTrajectory)"
_GRIPPER = "robotiq_gripper_controller/gripper_cmd (control_msgs/action/GripperCommand)"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _location_pose(manifest: dict[str, Any], name: str) -> dict[str, float]:
    for loc in manifest.get("declared_locations", []):
        if loc.get("name") == name:
            return loc.get("pose", {})
    raise KeyError(f"location {name!r} is not a declared_location in the manifest")


def _gripper(manifest: dict[str, Any]) -> dict[str, Any]:
    grippers = ((manifest.get("manipulation") or {}).get("grippers")) or []
    if not grippers:
        raise KeyError("manifest declares no gripper")
    return grippers[0]


def _pose_str(pose: dict[str, float]) -> str:
    return "{" + ", ".join(f"{k}={float(v):g}" for k, v in pose.items()) + "}"


def _force_str(force: Any, gripper: dict[str, Any]) -> str:
    lo = float(gripper.get("force_min_n", 0.0))
    hi = float(gripper.get("force_max_n", 0.0))
    if isinstance(force, (int, float)):
        return f"{float(force):g} N (within the gripper's [{lo:g}, {hi:g}] N rating)"
    level = str(force) if force is not None else "default"
    return f"{level!r}, resolved substrate-side within the gripper's [{lo:g}, {hi:g}] N rating"


def _steps(behavior: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for step in behavior.get("steps", []):
        if isinstance(step, dict):
            out.append(step)
    return out


def render_dispatch_plan(program: dict[str, Any], manifest: dict[str, Any]) -> str:
    """Validate the program, then render the ros2_kortex dispatch plan.

    Raises ``ValueError`` if the URML program does not validate against the
    manifest. No Kortex goal is dispatched for inadmissible intent.
    """
    result = validate(program, manifest, {}, policy=None)
    if not result.accepted:
        codes = ", ".join(e.code_str for e in result.errors)
        raise ValueError(f"URML program does not validate; no Kortex goal dispatched. Errors: {codes}")

    robot = str(manifest.get("robot_id", "kinova_cobot_cell"))
    desc = str(manifest.get("description", "")).strip()
    gripper = _gripper(manifest)
    lines: list[str] = [
        "URML -> ros2_kortex dispatch plan",
        f"robot: {robot} ({desc})",
        "validation: ACCEPTED against kinova-gen3.manifest.yaml",
        "  (static gate: an inadmissible program is rejected here; no Kortex goal is dispatched)",
        "",
    ]

    n = 0
    for step in _steps(program.get("behavior", {})):
        verb, args = next(iter(step.items()))
        args = args or {}
        n += 1
        if verb == "move_to":
            loc = args.get("location")
            pose = _location_pose(manifest, loc) if loc is not None else {}
            carry = f", carrying {args['carrying']}" if args.get("carrying") else ""
            lines.append(f"{n}. move_to(location={loc}{carry})")
            lines.append(f"   -> MoveIt 2 (kortex_moveit_config) plans to pose {_pose_str(pose)} in frame "
                         f"{_frame(manifest, loc)!r},")
            lines.append(f"      executed via {_JTC}")
        elif verb == "detect":
            lines.append(f"{n}. detect(object={args.get('object')}, store_as={args.get('store_as')})")
            lines.append("   -> perception: the wrist_rgb camera + a vision pipeline; not a Kortex motion action")
            lines.append("      (URML binds the detected object for the downstream grasp)")
        elif verb == "grasp":
            lines.append(f"{n}. grasp(target={args.get('target')}, force={args.get('force')})")
            lines.append(f"   -> {_GRIPPER}:")
            lines.append(f"      command.position=closed, command.max_effort={_force_str(args.get('force'), gripper)}")
        elif verb == "release":
            lines.append(f"{n}. release(mode={args.get('mode')}, at={args.get('at')})")
            lines.append(f"   -> {_GRIPPER}: command.position=open, command.max_effort=0")
            lines.append("      (the placement pose is reached by the preceding move_to)")
        else:
            lines.append(f"{n}. {verb}(...)")
            lines.append("   -> not mapped in this navigation/manipulation example")
    return "\n".join(lines) + "\n"


def _frame(manifest: dict[str, Any], name: str | None) -> str:
    for loc in manifest.get("declared_locations", []):
        if loc.get("name") == name:
            return str(loc.get("frame", "base_link"))
    return "base_link"


def render_pick_place() -> str:
    return render_dispatch_plan(_load(DEFAULT_PROGRAM), _load(DEFAULT_MANIFEST))


def main() -> None:
    out = _HERE / "dispatch-plan.txt"
    out.write_text(render_pick_place(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
