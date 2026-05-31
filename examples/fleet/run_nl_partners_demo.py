#!/usr/bin/env python3
"""Capstone: one English sentence moves the engaged-partners fleet, in sync (RFC-0286).

The full loop, end to end and hermetic:

    English sentence
        -> FleetBridge.translate   (LLM -> validated multi-robot program)
        -> FleetRuntime.execute     (the four robots dispatched concurrently)

Run it:  python run_nl_partners_demo.py

For hermetic, deterministic CI this uses EchoProvider — a stand-in that returns the
target fleet program instead of calling a model. Swap in AnthropicProvider /
OpenAIProvider (or any LLMProvider) and the same FleetBridge turns a free-form
sentence into the program for real. Either way the program is validated across the
four real partner manifests before any actuator is touched.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from urml_validator import FleetRoster
from urml_llm_bridge import EchoProvider, FleetBridge
from urml_ros2_runtime import FleetRuntime, FleetRuntimeResult, MockROSAdapter

HERE = Path(__file__).resolve().parent
_MANIFEST_DIR = HERE.parents[1] / "reference" / "validator" / "tests" / "fixtures" / "manifests"
FLEET_FILE = HERE / "engaged_partners.fleet.yaml"

SENTENCE = (
    "Have Marty, Petoi, and the CircuitPython board take their marks, then once "
    "everyone is ready take a synchronized sensor reading, and finally stand them "
    "down while the Kawasaki arm homes itself."
)


def _load_fleet() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    roster_doc, program_doc = yaml.safe_load_all(FLEET_FILE.read_text(encoding="utf-8"))
    roster = FleetRoster.model_validate(roster_doc)
    members = {
        m.name: yaml.safe_load((_MANIFEST_DIR / f"{m.manifest}.yaml").read_text(encoding="utf-8"))
        for m in roster.members
    }
    return roster_doc, members, program_doc


def main(verbose: bool = True) -> FleetRuntimeResult:
    """Translate one sentence into a fleet program and execute it concurrently."""
    roster_doc, members, target_program = _load_fleet()

    # 1. Natural language -> validated multi-robot program. EchoProvider stands in
    #    for the LLM (deterministic CI); a real provider drops in unchanged.
    provider = EchoProvider(scripted=[json.dumps(target_program)])
    bridge = FleetBridge(
        provider=provider, roster=roster_doc, member_manifests=members, policy=None
    )
    translation = bridge.translate(SENTENCE)
    if verbose:
        print(f'sentence: "{SENTENCE}"')
        print(f"FleetBridge.translate -> accepted={translation.accepted}")
    assert translation.program is not None

    # 2. Execute the four robots CONCURRENTLY (RFC-0286 concurrent runtime).
    adapters = {name: MockROSAdapter() for name in members}
    result = FleetRuntime(adapters).execute(roster_doc, members, translation.program, policy=None)
    if verbose:
        print(f"FleetRuntime.execute -> success={result.success}, steps={result.steps_executed}")
        for member in sorted(result.per_member_audit):
            methods = [c.get("method") for c in result.per_member_audit[member]]
            print(f"  {member}: {' -> '.join(methods)}")
    return result


if __name__ == "__main__":
    main()
