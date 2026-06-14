#!/usr/bin/env python3
"""URML validated-intent audit records as a robotics time series (for ReductStore).

The worked example from the ReductStore engagement
(reductstore/reductstore#1434), where the maintainer (atimin) confirmed
ReductStore can store URML's audit messages. This shows the concrete shape:
every validated dispatch produces one structured audit record, and that record is
a natural entry in a time series.

URML validates each intent against the capability manifest and the safety
envelope before anything actuates. Whether the intent is dispatched or refused,
the validator's verdict is the audit event worth keeping: the intent, the
primitives it used, the verdict, and (if refused) the failing validation pass and
the exact error codes. A refused intent is as important to record as a dispatched
one. Stored over time, these records are a robotics time series: queryable by
verdict, by primitive, by window.

This script runs a short stream of intents through the validator, builds one
audit record per intent, and prints both the audit log and the ReductStore write
plan (bucket / entry / labels / body). It is hermetic (the validator only, no
server, no robot) and deterministic (synthetic timestamps), so the committed
`audit-records.txt` is byte-asserted in CI. The live reduct-py write is shown in
the README as the integration pattern.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "delivery.manifest.yaml"
ENVELOPE = _HERE / "safety-envelope.yaml"
INTENTS = _HERE / "intents.yaml"

# Synthetic, fixed timestamps keep the output deterministic (ReductStore uses
# Unix microseconds). A real node would stamp each record at dispatch time.
_BASE_TS_US = 1_700_000_000_000_000
_STEP_US = 1_000_000  # 1 second between intents

_PASS = {
    "argument": "Pass 1 (argument typing)",
    "capability": "Pass 2 (capability)",
    "envelope": "Pass 3 (safety envelope)",
    "binding": "Pass 4 (variable bindings)",
    "policy": "Pass 5 (compliance policy)",
}


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _primitives(program: dict[str, Any]) -> list[str]:
    return [next(iter(step)) for step in program.get("behavior", {}).get("steps", [])]


def _failing_pass(codes: list[str]) -> str | None:
    for c in codes:
        ns = c.split(".", 1)[0]
        if ns in _PASS:
            return _PASS[ns]
    return None


def build_records(manifest: dict[str, Any], envelope: dict[str, Any], intents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for i, intent in enumerate(intents):
        result = validate(intent["program"], manifest, envelope, policy=None)
        codes = [e.code_str for e in result.errors]
        records.append(
            {
                "ts": _BASE_TS_US + i * _STEP_US,
                "robot_id": manifest["robot_id"],
                "intent": intent["label"],
                "primitives": _primitives(intent["program"]),
                "verdict": "dispatched" if result.accepted else "refused",
                "failing_pass": None if result.accepted else _failing_pass(codes),
                "codes": codes,
            }
        )
    return records


def render_report() -> str:
    manifest = _load(MANIFEST)
    envelope = _load(ENVELOPE)
    intents = _load(INTENTS)["intents"]
    records = build_records(manifest, envelope, intents)

    lines = [
        "URML validated-intent audit records as a time series.",
        "Each validated dispatch -> one audit record; refused intents are recorded too.",
        f"robot: {manifest['robot_id']}  |  envelope: {envelope['deployment_id']}",
        "",
        "# Audit log",
        "",
    ]
    for r in records:
        tag = "DISPATCHED" if r["verdict"] == "dispatched" else "REFUSED"
        prim = ",".join(r["primitives"])
        if r["verdict"] == "dispatched":
            lines.append(f"[{tag}] {r['intent']}  primitives={prim}")
        else:
            lines.append(
                f"[{tag}]   {r['intent']}  primitives={prim}  "
                f"{r['failing_pass']}  codes={','.join(r['codes'])}"
            )

    lines += [
        "",
        "# ReductStore write plan  (bucket=urml_audit, entry=" + manifest["robot_id"] + ")",
        "",
    ]
    for r in records:
        labels = {"verdict": r["verdict"], "intent": r["intent"]}
        body = json.dumps(r, sort_keys=True, separators=(",", ":"))
        lines.append(f"ts={r['ts']}  labels={json.dumps(labels, sort_keys=True, separators=(',', ':'))}")
        lines.append(f"   body={body}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "audit-records.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
