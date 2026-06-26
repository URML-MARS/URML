#!/usr/bin/env python3
"""URML on a TurtleBot 4 (ROS 2, Nav2), validated then executed (Discussion #526).

@slowrunner asked how a ROS 2 robot maps onto URML, since his Dave is a ROS bot
and his WaLI is a TurtleBot4 clone. The answer is `move_to`: a mapped robot knows
where it is, so it navigates to a named pose, and the ROS 2 runtime lowers that to
a Nav2 NavigateToPose goal. (The frameless GoPiGo3, by contrast, drives by amount
with `drive` / `turn`.)

This script validates a short errand against the TurtleBot4 manifest and executes
it hermetically through MockROSAdapter (no ROS, no robot). On a real TB4 the same
validated program runs through the ROS 2 `RclpyAdapter`, which lowers `move_to`
onto Nav2 and `capture` onto the camera.

It is deterministic, so the committed ``turtlebot4-report.txt`` is byte-asserted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate
from urml_ros2_runtime.runtime import URMLRuntime
from urml_ros2_runtime.substrate.mock import MockROSAdapter

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "turtlebot4.manifest.yaml"
_PROFILES = ("home",)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _errand() -> dict[str, Any]:
    """Go to the kitchen, take a photo, report. A mapped-robot errand."""
    return {
        "profile": ["home"],
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"move_to": {"location": "kitchen"}},
                {"capture": {"media": "photo", "store_as": "shot"}},
                {"report": {"to": "run_log", "facts": {"arrived": "kitchen"}, "status": "success"}},
            ],
        },
    }


def render_report() -> str:
    manifest = _load(MANIFEST)
    program = _errand()

    lines = [
        "URML on a TurtleBot 4 (ROS 2, Nav2) - Discussion #526.",
        "A mapped robot, so motion is `move_to` a named pose, which the ROS 2 runtime",
        "lowers to a Nav2 NavigateToPose goal (a frameless GoPiGo3 uses drive/turn instead).",
        f"robot: {manifest['robot_id']}   drive_type: {manifest['mobility']['drive_type']}"
        f"   places: {', '.join(loc['name'] for loc in manifest['declared_locations'])}",
        "",
        "# 1. Validate the errand against the manifest (validate before actuate)",
        "",
    ]
    result = validate(program, manifest, profiles=_PROFILES, policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] move_to kitchen, capture a photo, report.")
    if not result.accepted:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in result.errors})))
    lines.append("")

    # Execute through the mock substrate (hermetic). On a real TB4 this is the
    # rclpy RclpyAdapter driving Nav2 + the camera.
    lines += ["# 2. Execute through the substrate (here a hermetic mock)", ""]
    adapter = MockROSAdapter()
    run = URMLRuntime(adapter).execute(program, manifest, profiles=_PROFILES)
    for entry in adapter.call_log:
        method = entry["method"]
        if method == "send_navigation_goal":
            lines.append(f"  move_to {entry['location']:<12} -> send_navigation_goal(location={entry['location']!r})  [Nav2 NavigateToPose]")
        elif method == "capture_media":
            lines.append(f"  capture {'photo':<12} -> capture_media(media='photo')")
        elif method == "emit_report":
            lines.append(f"  report  {'':<12} -> emit_report(to='run_log')")
        else:
            lines.append(f"  {method}")
    lines.append("")
    lines.append(f"  executed {run.steps_executed} steps, success={run.success}")
    lines.append("")

    # The boundary slowrunner raised: what stays out of the language.
    lines += [
        "# Where the Nav2 knobs live (substrate-neutrality)",
        "",
        "  The URML program is just: move_to { location: kitchen }.",
        "  A real Nav2 deployment also tunes goal tolerance, a rotation-shim trigger",
        "  angle, pause-for-moving-obstacles, and replan-vs-plan-once. Those are",
        "  Nav2 concepts: they live in the ROS 2 adapter's deployment config, not in",
        "  the URML program, so the same move_to still runs on a GoPiGo3 or a drone.",
        "  Navigation telemetry (duration, recoveries) comes back in the run report;",
        "  a neutral shape for that is scoped in RFC-0638.",
    ]
    assert result.accepted and run.success
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "turtlebot4-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
