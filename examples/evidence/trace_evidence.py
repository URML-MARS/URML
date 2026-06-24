#!/usr/bin/env python3
"""Per-capability evidence traceability, end to end (RFC-0631).

The worked example from NVIDIA Isaac's review on isaac-sim/IsaacSim#649: a
manifest capability claim should record how it was established (derived from the
USD asset, declared by an integrator, verified by a smoke test, or inferred by a
model), not be a hand-typed unverifiable assertion.

This script shows the two halves of that, hermetically (validator only, no
runtime):

1. Evidence is advisory. The same manifest validates with no policy: every claim
   carries an `evidence` tag, but the tag changes no outcome on its own.
2. A deployment opts in. An evidence policy (evidence-policy.yaml) turns the tags
   into a gate: a gripper's force range and the mobility envelope must be
   `derived` or `verified`, a sensor's range at least `derived`, and a camera
   below that bar is flagged. The hand-declared bumper is refused; the
   LLM-inferred camera is warned about; the USD-derived and smoke-verified
   claims pass.

It is deterministic, so the committed ``evidence-report.txt`` is byte-asserted
in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "usd-derived.manifest.yaml"
POLICY = _HERE / "evidence-policy.yaml"

# Source strength, weakest to strongest, for the printed table.
_RANK = {"inferred": 0, "declared": 1, "derived": 2, "verified": 3}


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program() -> dict[str, Any]:
    """A minimal valid program. The example is about the manifest's evidence, so
    the program only needs to be admissible; a single report suffices."""
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"report": {"to": "log", "facts": {"check": "evidence"}, "status": "success"}},
            ],
        },
    }


def _evidence_rows(manifest: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    """(capability, source, ref, note) for each curated, evidenced capability."""
    rows: list[tuple[str, str, str, str]] = []

    def add(label: str, ev: dict[str, Any] | None) -> None:
        if ev is None:
            rows.append((label, "(none)", "", ""))
            return
        ref = ev.get("ref")
        ref_s = f"{ref['kind']}:{ref['value']}" if ref else ""
        rows.append((label, ev["source"], ref_s, ev.get("note", "")))

    if (mob := manifest.get("mobility")) is not None:
        add("mobility", mob.get("evidence"))
    for g in manifest.get("manipulation", {}).get("grippers", []):
        add(f"gripper {g['name']}", g.get("evidence"))
    for c in manifest.get("perception", {}).get("cameras", []):
        add(f"camera {c['name']}", c.get("evidence"))
    for s in manifest.get("perception", {}).get("sensors", []):
        add(f"sensor {s['name']}", s.get("evidence"))
    return rows


def render_report() -> str:
    manifest = _load(MANIFEST)
    policy = _load(POLICY)
    program = _program()

    lines: list[str] = [
        "Per-capability evidence traceability (RFC-0631).",
        "Each capability claim records how it was established, so a reviewer or an",
        "opt-in policy can tell a USD-derived contract from a hand-typed assertion.",
        f"robot: {manifest['robot_id']}",
        "",
        "# The evidence on each capability (source order: inferred < declared < derived < verified)",
        "",
    ]
    rows = _evidence_rows(manifest)
    wlabel = max(len(r[0]) for r in rows)
    wsrc = max(len(r[1]) for r in rows)
    for label, source, ref, note in rows:
        suffix = f"  {ref}" if ref else ""
        suffix += f"  // {note}" if note else ""
        lines.append(f"  {label.ljust(wlabel)}  {source.ljust(wsrc)}{suffix}")
    lines.append("")

    # 1. No policy: evidence is advisory and changes nothing.
    lines += [
        "# 1. Without a policy, evidence is advisory (validate before actuate is unaffected)",
        "",
    ]
    r_advisory = validate(program, manifest, profiles=["industrial"], policy=None)
    verdict = "VALID" if r_advisory.accepted else "REJECTED"
    lines.append(f"[{verdict}] the manifest validates; the evidence tags are pure traceability here.")
    lines.append("")

    # 2. Opt-in policy: the tags become a gate.
    lines += [
        "# 2. With evidence-policy.yaml, safety-relevant claims must be traceable",
        "",
        "    gripper force + mobility envelope: must be derived/verified (else error)",
        "    sensor range:                     must be derived/verified (else error)",
        "    camera claims:                    below derived is flagged (warning)",
        "",
    ]
    r_policy = validate(program, manifest, profiles=["industrial"], policy=policy)
    verdict = "VALID" if r_policy.accepted else "REJECTED"
    lines.append(f"[{verdict}] under the evidence policy.")
    lines.append("")
    lines.append("  errors:")
    ev_errors = [e for e in r_policy.errors if e.code_str == "policy.evidence_insufficient"]
    if ev_errors:
        for e in ev_errors:
            d = e.detail
            lines.append(
                f"    - {d['capability_kind']} {d['capability_label']!r}: "
                f"source {d['actual_source'] or 'none'} < required {d['required_min_source']}"
            )
    else:
        lines.append("    (none)")
    lines.append("  warnings:")
    ev_warnings = [w for w in r_policy.warnings if w.code_str == "policy.evidence_insufficient"]
    if ev_warnings:
        for w in ev_warnings:
            d = w.detail
            lines.append(
                f"    - {d['capability_kind']} {d['capability_label']!r}: "
                f"source {d['actual_source'] or 'none'} < required {d['required_min_source']}"
            )
    else:
        lines.append("    (none)")
    lines.append("")
    lines.append(
        "The USD-derived gripper/mobility and the smoke-verified lidar pass; the"
    )
    lines.append(
        "hand-declared bumper is refused; the LLM-inferred camera claim is flagged."
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    report = render_report()
    (_HERE / "evidence-report.txt").write_text(report, encoding="utf-8")
    print(report, end="")
