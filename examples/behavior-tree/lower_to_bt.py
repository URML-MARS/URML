#!/usr/bin/env python3
"""Validate a URML program, then lower it to an AutoAPMS / BehaviorTree.CPP tree.

The worked example from the AutoAPMS engagement (AutoAPMS/auto-apms#22). The
maintainer (robin-mueller) proposed lowering a URML intent description onto a
behavior tree through a build-handler plugin (an `auto_apms_urml` compatibility
package) that validates and translates URML into the behavior-tree
representation, reusing AutoAPMS's execution layer.

This is the validate-then-lower half of that, hermetically. URML's Layer-3
composition maps onto BT control nodes (sequence -> Sequence), and each primitive
maps onto an action leaf the AutoAPMS execution layer would run. The program is
validated against the manifest first; an inadmissible program (an undeclared
location) is refused and never lowered, so an invalid intent cannot become an
executable tree.

It is hermetic (the validator only, no AutoAPMS / ROS) and deterministic, so the
committed `bt-report.txt` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.sax.saxutils import quoteattr

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "delivery.manifest.yaml"
PROGRAMS = _HERE / "programs.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _attrs(verb: str, args: dict[str, Any]) -> str:
    keep = {
        "move_to": ["location"],
        "detect": ["object"],
        "grasp": ["force"],
    }.get(verb, [])
    parts = [f"{k}={quoteattr(str(args[k]))}" for k in keep if k in args]
    return (" " + " ".join(parts)) if parts else ""


def lower_to_bt(label: str, program: dict[str, Any]) -> list[str]:
    """Lower a validated URML program to BehaviorTree.CPP-style XML lines."""
    steps = program["behavior"]["steps"]
    lines = ['<root BTCPP_format="4">', f'  <BehaviorTree ID={quoteattr(label)}>', "    <Sequence>"]
    for step in steps:
        verb, args = next(iter(step.items()))
        lines.append(f'      <Action ID={quoteattr(verb)}{_attrs(verb, args or {})}/>')
    lines += ["    </Sequence>", "  </BehaviorTree>", "</root>"]
    return lines


def render_report() -> str:
    manifest = _load(MANIFEST)
    programs = _load(PROGRAMS)["programs"]
    lines = [
        "URML program -> validate -> lower to an AutoAPMS behavior tree.",
        "An inadmissible program is refused before any tree is emitted.",
        f"robot: {manifest['robot_id']}",
        "",
    ]
    for p in programs:
        result = validate(p["program"], manifest, policy=None)
        if result.accepted:
            lines.append(f"[LOWERED]  {p['label']}")
            lines += lower_to_bt(p["label"], p["program"])
        else:
            codes = ", ".join(e.code_str for e in result.errors)
            lines.append(f"[REFUSED]  {p['label']}  ->  [{codes}]; not lowered.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "bt-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
