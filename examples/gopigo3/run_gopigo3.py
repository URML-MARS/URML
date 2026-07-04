#!/usr/bin/env python3
"""Run validated URML programs on a basic GoPiGo3 (Discussion #523).

An English-shaped intent, validated against the GoPiGo3 manifest, then shown as
the wheel/speech calls it lowers to, with no ROS.

**Safe by default: bare invocation never moves a robot.** Running this with no
arguments (or ``-h``) is a DRY RUN against a fake backend: it validates the
programs and prints the planned ``drive_cm`` / ``turn_degrees`` / speech calls,
and writes the report. Nothing actuates. Pass ``--execute`` to drive a connected
GoPiGo3 for real, after a clear warning. This split exists because URML is a
validate-before-actuate project; a demo should not surprise-drive a robot (with
thanks to @slowrunner, whose GoPiGo3 took off across the room when he typed
``-h`` out of habit, Discussion #542).

Run your own program with ``-f prog.urml.yaml`` (the ``--out`` of
``urml translate``); with no ``-f`` it runs two built-in demos:
  1. The exact thing @slowrunner translated: announce "Driving forward 1 meter",
     then drive 1 m.
  2. A short patrol: turn, drive, turn, drive, announce done, report.
``-m`` / ``--mock`` forces the fake backend even with ``--execute``, to preview a
program without moving the robot (Discussion #523).

Installing the GoPiGo3 software is the platform's job, per Dexter Industries'
Installation FAQ: https://github.com/DexterInd/GoPiGo3/blob/main/Installation_FAQ.md
The dry run is deterministic, so the committed ``gopigo3-report.txt`` is
byte-asserted in CI.
"""

from __future__ import annotations

import argparse
import sys
from importlib import metadata
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "gopigo3.manifest.yaml"

# The example travels with URML, so its "version" is the versions of the URML
# packages that run it, read from installed package metadata. Nothing to hand-edit
# (Discussion #523): pip records the version, this just reports it.
_URML_PACKAGES = ("urml-validator", "urml-ros2-runtime")


def _version_line() -> str:
    parts = []
    for pkg in _URML_PACKAGES:
        try:
            parts.append(f"{pkg} {metadata.version(pkg)}")
        except metadata.PackageNotFoundError:
            parts.append(f"{pkg} (not installed)")
    return "gopigo3 example, running on " + ", ".join(parts)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------
# Backend selection. The default (dry run) installs a fake `easygopigo3` and never
# touches the real library, so a bare run cannot move a robot. Only `--execute`
# asks for the real library (falling back to the fake if it is absent). No code
# edits are needed either way; the choice is a flag, not a deletion.
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


def _install_fake() -> str:
    mod = ModuleType("easygopigo3")
    mod.EasyGoPiGo3 = _FakeEasyGoPiGo3  # type: ignore[attr-defined]
    mod._URML_FAKE = True  # type: ignore[attr-defined]
    sys.modules["easygopigo3"] = mod
    return "fake"


def _ensure_easygopigo3(prefer_real: bool = False) -> str:
    """Make `easygopigo3` importable and return which backend is in use.

    Default (``prefer_real=False``): install the fake and never import the real
    library, so nothing can drive a robot. ``prefer_real=True`` (only set by
    ``--execute``): use the real library if present, else fall back to the fake.
    Idempotent: a second call returns the backend already chosen. Installing the
    real GoPiGo3 software is the platform's job, not URML's.
    """
    existing = sys.modules.get("easygopigo3")
    if existing is not None:
        return "fake" if getattr(existing, "_URML_FAKE", False) else "real"
    if prefer_real:
        try:
            import easygopigo3  # noqa: F401  (real Dexter Industries library)
            return "real"
        except ImportError:
            return _install_fake()
    return _install_fake()


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


def _profiles_of(program: dict[str, Any]) -> tuple[str, ...]:
    """The program's declared profiles (a `urml translate` output carries them)."""
    prof = program.get("profile") or ["educational"]
    return (prof,) if isinstance(prof, str) else tuple(prof)


def _run(lines: list[str], label: str, program: dict[str, Any], manifest: dict[str, Any]) -> None:
    # Import here so the fake easygopigo3 is already installed.
    from urml_validator import validate
    from urml_ros2_runtime.runtime import URMLRuntime

    from gopigo3_adapter import GoPiGo3Adapter

    profiles = _profiles_of(program)
    result = validate(program, manifest, profiles=profiles, policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] {label}")
    if not result.accepted:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in result.errors})))
        lines.append("")
        return

    spoken: list[str] = []
    # adapter = GoPiGo3Adapter(speak=spoken.append)
    adapter = GoPiGo3Adapter(speak=None)
    runtime = URMLRuntime(adapter)
    run = runtime.execute(program, manifest, profiles=profiles)

    lines.append(f"   executed {run.steps_executed} steps, success={run.success}")
    lines.append("   wheel + speech calls, in order:")
    for entry in adapter.call_log:
        method = entry["method"]
        if method in ("drive_by", "turn_by"):
            lines.append(f"     {method:12} -> easygopigo3.{entry['hw']}")
        elif method == "emit_speech":
            lines.append(f"     {method:12} -> espeak-ng {entry['utterance']!r}")
        else:
            lines.append(f"     {method}")
    lines.append("")


def render_report(prefer_real: bool = False) -> str:
    manifest = _load(MANIFEST)
    _ensure_easygopigo3(prefer_real)

    lines = [
        "URML on a basic GoPiGo3 (Raspberry Pi, easygopigo3, no ROS) - Discussion #523.",
        "English-shaped intent, validated against the GoPiGo3 manifest, then lowered",
        "to wheel/speech calls. Frameless robot, so motion is `drive` / `turn` by amount (RFC-0630).",
        f"robot: {manifest['robot_id']}   drive_type: {manifest['mobility']['drive_type']}"
        f"   max drive: {manifest['mobility']['max_relative_distance']} m",
        "",
    ]
    _run(lines, "announce, then drive 1 m (the translated command from #497/#523)", _announce_and_drive(), manifest)
    _run(lines, "short patrol: turn, drive, turn, drive, announce, report", _patrol(), manifest)

    lines.append("This is a dry run: the calls above were validated and planned, not actuated.")
    lines.append("On a GoPiGo3 with the GoPiGo3 software installed (see Dexter Industries'")
    lines.append("Installation FAQ), run with --execute to drive the wheels for real.")
    return "\n".join(lines).rstrip() + "\n"


def run_program_file(path: str, prefer_real: bool = False) -> str:
    """Validate and run a single URML program loaded from a YAML file.

    The file is what `urml translate ... --out prog.urml.yaml` writes: a validated
    URML program. This is @slowrunner's workflow (Discussion #523): translate an
    English sentence on a capable box, copy the YAML to the Pi, run it here. Dry
    run unless ``prefer_real`` (driven by --execute without --mock).
    """
    manifest = _load(MANIFEST)
    _ensure_easygopigo3(prefer_real)
    p = Path(path)
    name = p.name
    lines = [
        f"URML on a basic GoPiGo3 - running {name} (Discussion #523).",
        _version_line(),
        f"robot: {manifest['robot_id']}   drive_type: {manifest['mobility']['drive_type']}"
        f"   max drive: {manifest['mobility']['max_relative_distance']} m",
        "",
    ]
    if not p.is_file():
        lines.append(f"[ERROR] no such program file: {path}")
        return "\n".join(lines) + "\n"
    program = _load(p)
    _run(lines, f"program file: {name}", program, manifest)
    if not prefer_real:
        lines.append("Dry run: validated and planned, not actuated. Pass --execute (without -m) to drive the robot.")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="run_gopigo3.py",
        description=(
            "Validate URML against the GoPiGo3 manifest and show the wheel/speech "
            "calls it lowers to. With -f, run your own translated URML program; "
            "without it, run the two built-in demos. DRY RUN by default (a fake "
            "backend, no movement). Pass --execute to drive a connected GoPiGo3 "
            "for real; -m forces the fake even with --execute."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=_version_line(),
        help="Print the URML package versions this example runs on, and exit.",
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="URML_FILE",
        help=(
            "Run a validated URML program from a YAML file (the --out of "
            "`urml translate`) instead of the two built-in demos."
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Drive a connected GoPiGo3 for real (uses the installed easygopigo3). "
            "Without this flag the script never moves a robot, so it is safe to run "
            "by habit or with -h."
        ),
    )
    parser.add_argument(
        "-m",
        "--mock",
        action="store_true",
        help=(
            "Force the fake backend even with --execute, to simulate a run without "
            "moving a robot. Useful to preview a program before running it for real."
        ),
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(_HERE))
    print(f"[gopigo3 example] {_version_line()}", file=sys.stderr)
    prefer_real = args.execute and not args.mock
    if prefer_real:
        print(
            "[gopigo3 example] --execute: this WILL move a connected GoPiGo3. "
            "Clear space around the robot.",
            file=sys.stderr,
        )
    backend = _ensure_easygopigo3(prefer_real=prefer_real)
    mode = "executing on hardware" if (prefer_real and backend == "real") else "dry run, no movement"
    print(f"[gopigo3 example] backend: {backend} ({mode})", file=sys.stderr)

    if args.file:
        # A user's own program: print to stdout, do not overwrite the committed report.
        print(run_program_file(args.file, prefer_real=prefer_real), end="")
        return
    out = _HERE / "gopigo3-report.txt"
    out.write_text(render_report(prefer_real=prefer_real), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
