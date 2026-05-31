#!/usr/bin/env python3
"""Run the engaged-partners fleet roll-call hermetically (RFC-0286).

Four real partner robots — Robotical Marty, Petoi Bittle, Adafruit CircuitPython,
and a Kawasaki arm — named as one fleet and synchronized in a single program. The
mission is validated against each robot's REAL capability manifest, then executed
against one MockROSAdapter per member so it runs offline, any OS, no ROS, no cloud.

    python run_partners_demo.py

On real hardware, swap each MockROSAdapter for the robot's real adapter
(RoboticalMartyAdapter / PetoiAdapter / CircuitPythonAdapter / KawasakiAdapter) —
they all satisfy the same ROSAdapter Protocol the FleetRuntime dispatches over.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import FleetRoster, validate_fleet
from urml_ros2_runtime import FleetRuntime, FleetRuntimeResult, MockROSAdapter

HERE = Path(__file__).resolve().parent
_REPO_ROOT = HERE.parents[1]
# The engaged-partner robots are real fixtures, not generic demo manifests.
_MANIFEST_DIR = _REPO_ROOT / "reference" / "validator" / "tests" / "fixtures" / "manifests"
FLEET_FILE = HERE / "engaged_partners.fleet.yaml"


def load_fleet() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    """Load the mission and resolve each member's real manifest from the fixtures."""
    roster_doc, program_doc = yaml.safe_load_all(FLEET_FILE.read_text(encoding="utf-8"))
    roster = FleetRoster.model_validate(roster_doc)
    members: dict[str, dict[str, Any]] = {}
    for member in roster.members:
        manifest_path = _MANIFEST_DIR / f"{member.manifest}.yaml"
        members[member.name] = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return roster_doc, members, program_doc


def main(verbose: bool = True) -> FleetRuntimeResult:
    """Validate then execute the engaged-partners roll-call. Returns the result."""
    roster_doc, members, program_doc = load_fleet()

    # --no-policy posture: the language is on stage; Petoi's CN origin is an
    # operator-context policy decision (RFC-0004), out of scope for the demo.
    result = validate_fleet(roster_doc, members, program_doc, policy=None)
    if verbose:
        print(f"fleet: {', '.join(sorted(members))}")
        print(f"validate_fleet -> accepted={result.accepted}")
    if not result.accepted:
        for err in result.errors:
            print(f"  REJECTED [{err.code_str}] {err.message}")
        raise SystemExit(1)

    adapters = {name: MockROSAdapter() for name in members}
    exec_result = FleetRuntime(adapters).execute(roster_doc, members, program_doc, policy=None)

    if verbose:
        print(f"execute -> success={exec_result.success}, steps={exec_result.steps_executed}")
        for member in sorted(exec_result.per_member_audit):
            methods = [call.get("method") for call in exec_result.per_member_audit[member]]
            print(f"  {member}: {' -> '.join(methods)}")
    return exec_result


if __name__ == "__main__":
    main()
