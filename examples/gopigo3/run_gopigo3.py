#!/usr/bin/env python3
"""Run validated URML programs on a basic GoPiGo3, hermetically (Discussion #523).

This is the end-to-end the GoPiGo3 user asked for: an English-shaped intent,
validated against the GoPiGo3 manifest, then executed through GoPiGo3Adapter onto
the wheels, with no ROS. It binds to the real ``easygopigo3`` when the GoPiGo3
software is installed (and drives the wheels), and falls back to a fake when it is
not (no robot, deterministic). The same file works both ways, no edits. Installing
the GoPiGo3 software is the platform's job, per Dexter Industries' Installation FAQ:
https://github.com/DexterInd/GoPiGo3/blob/main/Installation_FAQ.md

Two programs:
  1. The exact thing @slowrunner translated: announce "Driving forward 1 meter",
     then drive 1 m.
  2. A short patrol: turn, drive, turn, drive, announce done, report.

Each is validated (validate before actuate), then executed through the real
GoPiGo3Adapter. The report shows the easygopigo3 calls the adapter made
(``drive_cm`` / ``turn_degrees``) and the spoken lines. Deterministic, so the
committed ``gopigo3-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "gopigo3.manifest.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------
# The example runs with no robot by falling back to a fake `easygopigo3` when the
# real Dexter Industries library is not installed. No code edits are needed either
# way: on a GoPiGo3 with the GoPiGo3 software installed, the real library is used
# and the wheels move; anywhere else, the fake stands in and records the calls.
# --------------------------------------------------------------------------


class _FakeEasyGoPiGo3:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def drive_cm(self, dist: float, blocking: bool = True) -> None:
        self.calls.append(f"drive_cm({dist:.1f})")

    def turn_degrees(self, deg: float, blocking: bool = True) -> None:
        self.calls.append(f"turn_degrees({deg:.1f})")

    def orbit(self, degrees: float, radius_cm: float) -> None:
        self.calls.append(f"orbit({degrees:.1f}, {radius_cm:.1f})")

    def stop(self) -> None:
        self.calls.append("stop()")


def _ensure_easygopigo3() -> str:
    """Make `easygopigo3` importable, real if present, fake otherwise.

    Returns "real" or "fake". Idempotent: a second call sees the choice already
    made. Installing the real GoPiGo3 software is the platform's job (see Dexter
    Industries' Installation FAQ), not URML's; this only decides which backend
    the example binds to.
    """
    existing = sys.modules.get("easygopigo3")
    if existing is not None:
        return "fake" if getattr(existing, "_URML_FAKE", False) else "real"
    try:
        import easygopigo3  # noqa: F401  (real Dexter Industries library)
        return "real"
    except ImportError:
        mod = ModuleType("easygopigo3")
        mod.EasyGoPiGo3 = _FakeEasyGoPiGo3  # type: ignore[attr-defined]
        mod._URML_FAKE = True  # type: ignore[attr-defined]
        sys.modules["easygopigo3"] = mod
        return "fake"


def _announce_and_drive() -> dict[str, Any]:
    """'Announce \"Driving forward 1 meter\" and then execute the action.'"""
    return {
        "profile": ["educational"],
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"speak": {"utterance": "Driving forward 1 meter"}},
                {"drive": {"distance": 1.0}},
            ],
        },
    }


def _patrol() -> dict[str, Any]:
    return {
        "profile": ["educational"],
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"turn": {"angle": 90}},
                {"drive": {"distance": 0.5}},
                {"turn": {"angle": -90}},
                {"drive": {"distance": 0.5}},
                {"speak": {"utterance": "Patrol complete"}},
                {"report": {"to": "run_log", "facts": {"patrol": "done"}, "status": "success"}},
            ],
        },
    }


def _run(lines: list[str], label: str, program: dict[str, Any], manifest: dict[str, Any]) -> None:
    # Import here so the fake easygopigo3 is already installed.
    from urml_validator import validate
    from urml_ros2_runtime.runtime import URMLRuntime

    from gopigo3_adapter import GoPiGo3Adapter

    result = validate(program, manifest, profiles=["educational"], policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] {label}")
    if not result.accepted:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in result.errors})))
        lines.append("")
        return

    spoken: list[str] = []
    adapter = GoPiGo3Adapter(speak=spoken.append)
    runtime = URMLRuntime(adapter)
    run = runtime.execute(program, manifest, profiles=("educational",))

    lines.append(f"   executed {run.steps_executed} steps, success={run.success}")
    lines.append("   wheel + speech calls, in order:")
    for entry in adapter.call_log:
        method = entry["method"]
        if method in ("drive_by", "turn_by"):
            lines.append(f"     {method:12} -> easygopigo3.{entry['hw']}")
        elif method == "emit_speech":
            lines.append(f"     {method:12} -> espeak {entry['utterance']!r}")
        else:
            lines.append(f"     {method}")
    lines.append("")


def render_report() -> str:
    manifest = _load(MANIFEST)
    _ensure_easygopigo3()

    lines = [
        "URML on a basic GoPiGo3 (Raspberry Pi, easygopigo3, no ROS) - Discussion #523.",
        "English-shaped intent, validated against the GoPiGo3 manifest, then executed",
        "onto the wheels. Frameless robot, so motion is `drive` / `turn` by amount (RFC-0630).",
        f"robot: {manifest['robot_id']}   drive_type: {manifest['mobility']['drive_type']}"
        f"   max drive: {manifest['mobility']['max_relative_distance']} m",
        "",
    ]
    _run(lines, "announce, then drive 1 m (the translated command from #497/#523)", _announce_and_drive(), manifest)
    _run(lines, "short patrol: turn, drive, turn, drive, announce, report", _patrol(), manifest)

    lines.append("On a GoPiGo3 with the GoPiGo3 software installed (see Dexter Industries'")
    lines.append("Installation FAQ), the real easygopigo3 is used automatically and these same")
    lines.append("validated programs drive the wheels. No code changes are needed.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    sys.path.insert(0, str(_HERE))
    backend = _ensure_easygopigo3()
    print(f"[gopigo3 example] using the {backend} easygopigo3 backend", file=sys.stderr)
    out = _HERE / "gopigo3-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
