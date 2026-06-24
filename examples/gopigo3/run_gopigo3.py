#!/usr/bin/env python3
"""Run validated URML programs on a basic GoPiGo3, hermetically (Discussion #523).

This is the end-to-end the GoPiGo3 user asked for: an English-shaped intent,
validated against the GoPiGo3 manifest, then executed through GoPiGo3Adapter onto
the wheels, with no ROS. It runs here against a fake ``easygopigo3`` (no robot, no
GPU, deterministic), and unchanged on a real GoPiGo3 once you ``pip install
gopigo3 easygopigo3`` and remove the fake injection.

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
# A fake easygopigo3 so the example runs with no robot. EasyGoPiGo3 records the
# wheel calls the adapter makes; on a real GoPiGo3 this whole block goes away.
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


def _install_fake_easygopigo3(sink: dict[str, Any]) -> None:
    mod = ModuleType("easygopigo3")

    def _factory() -> _FakeEasyGoPiGo3:
        bot = _FakeEasyGoPiGo3()
        sink["bot"] = bot
        return bot

    mod.EasyGoPiGo3 = _factory  # type: ignore[attr-defined]
    sys.modules["easygopigo3"] = mod


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
    sink: dict[str, Any] = {}
    _install_fake_easygopigo3(sink)

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

    lines.append("On a real GoPiGo3: `pip install gopigo3 easygopigo3`, delete the fake")
    lines.append("injection in run_gopigo3.py, and the same validated programs drive the wheels.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "gopigo3-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.path.insert(0, str(_HERE))
    main()
