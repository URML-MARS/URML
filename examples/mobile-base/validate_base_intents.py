#!/usr/bin/env python3
"""The intermediary URML node for quadruped_ros2_control: validate intent, emit Twist.

The worked example from the quadruped_ros2_control engagement
(legubiao/quadruped_ros2_control#65). The maintainer described the lowest-effort,
non-intrusive integration: an intermediary URML node that validates incoming
intent against the base manifest, then translates valid intents into standard
Twist commands for the existing controller, with no modification to the
ros2_control stack. He also noted the gap it fills: the controllers have no
unified, declarative capability validation, so an invalid velocity command may
fail silently or destabilise the platform.

This script is that node, hermetically. It reads the base manifest
(`quadruped-base.manifest.yaml`) through URML's capability-manifest schema, reads
its RFC-0518 base-level bounds (linear / angular velocity, accelerations,
traversable slope, payload), and validates each base intent
(`base-intents.yaml`) against them. An admissible intent is translated to a Twist
(linear.x, angular.z); an inadmissible one is refused with the specific bound it
broke, before anything reaches the controller. URML never touches the whole-body
internals (legs, CoM, MPC/RL) the stack keeps private; it gates the public
base-velocity interface.

It is deterministic and validator-only (no ROS, no robot), so the committed
`base-intent-report.txt` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator.schemas.manifest import CapabilityManifest

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "quadruped-base.manifest.yaml"
INTENTS = _HERE / "base-intents.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def check_intent(mob: Any, intent: dict[str, Any]) -> list[str]:
    """Return the list of base bounds the intent violates (empty == admissible)."""
    checks = [
        ("linear_velocity", "max_velocity", "max_velocity"),
        ("angular_velocity", "max_angular_velocity", "max_angular_velocity"),
        ("linear_acceleration", "max_linear_acceleration", "max_linear_acceleration"),
        ("terrain_slope_deg", "max_traversable_slope_deg", "max_traversable_slope_deg"),
        ("payload_kg", "max_payload", "max_payload"),
    ]
    violations: list[str] = []
    for intent_key, bound_attr, label in checks:
        requested = intent.get(intent_key)
        bound = getattr(mob, bound_attr, None)
        if requested is not None and bound is not None and requested > bound:
            violations.append(f"{label} ({requested} > {bound})")
    return violations


def render_report() -> str:
    manifest = CapabilityManifest.model_validate(_load(MANIFEST))
    mob = manifest.mobility
    intents = _load(INTENTS)["intents"]

    lines = [
        "URML intermediary node for quadruped_ros2_control: validate base intent, emit Twist.",
        "The whole-body internals stay private; URML gates the public base-velocity interface.",
        f"base: {manifest.robot_id}  |  drive_type: {mob.drive_type}",
        "",
    ]
    for intent in intents:
        violations = check_intent(mob, intent)
        if not violations:
            vx = float(intent.get("linear_velocity", 0.0))
            wz = float(intent.get("angular_velocity", 0.0))
            lines.append(f"[DISPATCH] {intent['label']}")
            lines.append(f"   -> Twist(linear.x={vx}, angular.z={wz}); sent to the controller.")
        else:
            lines.append(f"[REJECTED] {intent['label']}")
            lines.append(f"   -> refused at the base manifest [{', '.join(violations)}]. No Twist sent.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "base-intent-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
