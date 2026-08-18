#!/usr/bin/env python3
"""A URDF's own limits, read out and used as a capability-manifest source.

For clemense/yourdfpy#69 (the liburdf JSON-emission thread). A URDF already
carries, per joint, the numbers a validate-before-actuate check needs: effort,
velocity, and position limits. This example reads a real URDF with the standard
library, takes the gripper finger joint's effort limit as a grasp-force cap,
builds a URML capability manifest around it, and then validates a grasp against
that cap: one inside the limit is admissible, one over it is refused before the
gripper ever closes.

The point is the mapping, not a parser: a URDF gives you kinematics and limits,
not deployment context (frames, object classes, provenance). So the effort/
velocity/position limits come from the URDF, and the rest of the manifest is
authored. A tool like liburdf that emits those limits as JSON with explicit units
would make the limit half of this automatic, for any validate-before-actuate
layer, not just URML.

Hermetic and deterministic (stdlib XML + the validator, no ROS, no robot), so the
committed ``urdf-to-manifest-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from urml_validator import validate

_HERE = Path(__file__).resolve().parent
URDF = _HERE / "simple_arm.urdf"
_PROFILES = ("industrial",)

_OK_FORCE_N = 60.0
_OVER_FORCE_N = 250.0


def parse_joint_limits(urdf_path: Path) -> list[dict[str, Any]]:
    """Read every joint's <limit> out of a URDF (stdlib only)."""
    root = ET.parse(urdf_path).getroot()
    joints: list[dict[str, Any]] = []
    for joint in root.findall("joint"):
        limit = joint.find("limit")
        if limit is None:
            continue
        joints.append(
            {
                "name": joint.get("name"),
                "type": joint.get("type"),
                "effort": float(limit.get("effort")),
                "velocity": float(limit.get("velocity")),
                "lower": float(limit.get("lower")),
                "upper": float(limit.get("upper")),
            }
        )
    return joints


def _gripper_joint(joints: list[dict[str, Any]]) -> dict[str, Any]:
    """The parallel-jaw finger: the prismatic joint whose effort is the grasp-force cap."""
    prismatic = [j for j in joints if j["type"] == "prismatic"]
    assert len(prismatic) == 1, "expected exactly one prismatic finger joint in the URDF"
    return prismatic[0]


def manifest_from_urdf(force_cap_n: float) -> dict[str, Any]:
    """Build a capability manifest whose gripper force cap is the URDF effort limit."""
    return {
        "manifest_version": "0.1",
        "robot_id": "urdf_arm_cell",
        "description": "A single arm + parallel-jaw gripper; the gripper force cap is sourced from a URDF.",
        "frames": [{"name": "cell", "parent": None}, {"name": "base_link", "parent": "cell"}],
        "declared_locations": [
            {"name": "parts_bin", "pose": {"x": 0.40, "y": -0.20, "z": 0.08}, "frame": "cell", "description": "Source bin."},
            {"name": "assembly_fixture", "pose": {"x": -0.30, "y": 0.20, "z": 0.10}, "frame": "cell", "description": "Destination."},
        ],
        "mobility": {"drive_type": "manipulator_base", "max_velocity": 0.25, "station_keeping": True},
        "manipulation": {
            "arm_count": 1,
            "grippers": [
                {
                    "name": "parallel_jaw",
                    "kind": "servo_electric",
                    "force_min_n": 0.0,
                    "force_max_n": force_cap_n,
                    "accepted_classes": ["small_part"],
                    "movable": True,
                }
            ],
            "reachable_workspace_m": 0.75,
        },
        "perception": {
            "cameras": [
                {
                    "name": "wrist_rgb",
                    "movable": True,
                    "supports_photo": True,
                    "supports_video": False,
                    "supports_stream": False,
                    "max_resolution": "1080p",
                }
            ],
            "object_vocabulary": ["small_part"],
        },
        "docking_stations": [],
        "outputs": {"named_endpoints": ["run_log"]},
        "provenance": {
            "manifest_attestation": "self_declared",
            "components": [
                {
                    "id": "arm_driver",
                    "role": "critical",
                    "vendor": "research_lab",
                    "country_of_origin": "US",
                    "country_of_final_assembly": "US",
                }
            ],
        },
    }


def _grasp_program(force_n: float) -> dict[str, Any]:
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"detect": {"object": "small_part", "store_as": "part"}},
                {"grasp": {"target": "$part", "force": {"newtons": force_n}}},
                {"release": {"mode": "place", "at": "assembly_fixture"}},
            ],
        },
    }


def render_report() -> str:
    joints = parse_joint_limits(URDF)
    gripper = _gripper_joint(joints)
    force_cap = gripper["effort"]
    manifest = manifest_from_urdf(force_cap)

    lines = [
        "URML: a URDF's own limits, read out and used as a capability-manifest source.",
        "A URDF already carries per-joint effort / velocity / position limits. This reads",
        "simple_arm.urdf, takes the gripper finger joint's effort limit as a grasp-force",
        "cap, and validates a grasp against it. For clemense/yourdfpy#69.",
        "",
        "# 1. What the URDF declares (read with the standard library)",
        "",
        "  joint                type       effort   velocity   lower    upper",
    ]
    for j in joints:
        lines.append(
            f"  {j['name']:<19} {j['type']:<10} {j['effort']:>6.1f}   {j['velocity']:>6.2f}   "
            f"{j['lower']:>6.3f}   {j['upper']:>6.3f}"
        )
    lines += [
        "",
        "# 2. The mapping",
        "",
        f"  gripper finger joint {gripper['name']!r} effort limit = {force_cap:.1f}",
        f"    -> manipulation.grippers[0].force_max_n = {force_cap:.1f} N",
        "  (Effort/velocity/position come from the URDF; frames, object classes, and",
        "   provenance are deployment context the URDF does not carry, so they are authored.)",
        "",
        "# 3. A grasp checked against the URDF-sourced force cap",
        "",
    ]

    ok = validate(_grasp_program(_OK_FORCE_N), manifest, profiles=_PROFILES, policy=None)
    ok_verdict = "VALID" if ok.accepted else "REJECTED"
    lines.append(f"[{ok_verdict}] grasp small_part at {_OK_FORCE_N} N  (|{_OK_FORCE_N}| <= {force_cap:.1f})")
    if ok.accepted:
        lines.append(f"   Admissible: within the URDF-sourced {force_cap:.1f} N cap. Dispatch may proceed.")
    else:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in ok.errors})))
    lines.append("")

    over = validate(_grasp_program(_OVER_FORCE_N), manifest, profiles=_PROFILES, policy=None)
    over_verdict = "VALID" if over.accepted else "REJECTED"
    codes = sorted({e.code_str for e in over.errors})
    msgs = {e.code_str: e.message for e in over.errors}
    lines.append(f"[{over_verdict}] grasp small_part at {_OVER_FORCE_N} N  (|{_OVER_FORCE_N}| > {force_cap:.1f})")
    lines.append("   -> " + ", ".join(codes))
    if "envelope.force_exceeded" in msgs:
        lines.append(f"   envelope.force_exceeded: {msgs['envelope.force_exceeded']}")
    lines.append("   Refused before the gripper closes, on the limit the URDF itself declared.")
    lines += [
        "",
        "# Honest altitude",
        "",
        "URML reads the URDF's limits and checks a command against them; it does no",
        "kinematics, no motion planning, and no control. A URDF-to-JSON emission that",
        "preserves these limits with explicit units (the liburdf direction) would make the",
        "limit half of this mapping automatic for any validate-before-actuate layer.",
    ]

    assert ok.accepted, "a grasp within the URDF-sourced force cap should validate"
    assert not over.accepted, "a grasp over the URDF-sourced force cap should be rejected"
    assert "envelope.force_exceeded" in codes, "the over-force grasp should carry envelope.force_exceeded"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "urdf-to-manifest-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
