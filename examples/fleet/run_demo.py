#!/usr/bin/env python3
"""Run the courier-to-arm fleet handoff hermetically (RFC-0286).

Pure Python, stdlib + the urml packages only. No ROS, no cloud, any OS. This is
the multi-robot analogue of the single-robot red-mug demo: it loads one fleet
mission file (a roster + a program), statically validates it across both
members' manifests, then executes it against one MockROSAdapter per member and
prints each robot's audit trail.

    python run_demo.py

The pipeline is the headline path, one rung up from a single robot:

    load roster + program  ->  validate_fleet  ->  FleetRuntime.execute
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import FleetRoster, validate_fleet
from urml_ros2_runtime import FleetRuntime, FleetRuntimeResult, MockROSAdapter

HERE = Path(__file__).resolve().parent
FLEET_FILE = HERE / "courier_handoff.fleet.yaml"


def load_fleet() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    """Load the two-document fleet file and resolve each member's manifest.

    Returns ``(roster_doc, member_manifests, program_doc)`` where
    ``member_manifests`` is ``{member_handle -> manifest dict}``, resolved by
    reading the sibling ``<manifest>.manifest.yaml`` named by each roster member.
    """
    roster_doc, program_doc = yaml.safe_load_all(FLEET_FILE.read_text(encoding="utf-8"))
    roster = FleetRoster.model_validate(roster_doc)
    members: dict[str, dict[str, Any]] = {}
    for member in roster.members:
        manifest_path = HERE / f"{member.manifest}.manifest.yaml"
        members[member.name] = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return roster_doc, members, program_doc


def main(verbose: bool = True) -> FleetRuntimeResult:
    """Validate then execute the fleet handoff. Returns the runtime result."""
    roster_doc, members, program_doc = load_fleet()

    # 1. Static cross-robot validation (demos run --no-policy; the language is
    #    on stage, compliance one flag away — see CLAUDE.md headline-path posture).
    result = validate_fleet(roster_doc, members, program_doc, policy=None)
    if verbose:
        names = ", ".join(sorted(members))
        print(f"fleet: {names}")
        print(f"validate_fleet -> accepted={result.accepted}")
    if not result.accepted:
        for err in result.errors:
            print(f"  REJECTED [{err.code_str}] {err.message}")
        raise SystemExit(1)

    # 2. Hermetic execution: one MockROSAdapter per member, fully offline.
    adapters = {name: MockROSAdapter() for name in members}
    exec_result = FleetRuntime(adapters).execute(roster_doc, members, program_doc)

    if verbose:
        print(f"execute -> success={exec_result.success}, steps={exec_result.steps_executed}")
        for member in sorted(exec_result.per_member_audit):
            methods = [call.get("method") for call in exec_result.per_member_audit[member]]
            print(f"  {member}: {' -> '.join(methods)}")
    return exec_result


if __name__ == "__main__":
    main()
