"""The GoPiGo3 worked example must be deterministic and true.

Mirrors the other example guards: the generator is deterministic, the committed
``gopigo3-report.txt`` matches it, and the example shows the end-to-end
@slowrunner asked for on Discussion #523 (a validated URML program driving a basic
GoPiGo3 through GoPiGo3Adapter, no ROS). Hermetic: the example injects a fake
``easygopigo3`` so no robot and no library are needed.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "gopigo3"
GEN_PATH = EX / "run_gopigo3.py"
COMMITTED = EX / "gopigo3-report.txt"


def _load_gen():
    # The runner imports `gopigo3_adapter` by name, so its dir must be importable.
    if str(EX) not in sys.path:
        sys.path.insert(0, str(EX))
    spec = importlib.util.spec_from_file_location("run_gopigo3", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_report() == gen.render_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_report(), (
        "examples/gopigo3/gopigo3-report.txt is stale; "
        "run `python examples/gopigo3/run_gopigo3.py` and commit."
    )


def test_validated_intent_lowers_to_wheel_calls() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Both programs validate before actuating.
    assert "[VALID] announce, then drive 1 m" in report
    assert "[REJECTED]" not in report
    # `drive` lowered to the easygopigo3 call; `speak` to espeak.
    assert "drive_by     -> easygopigo3.drive_cm(100.0)" in report
    assert "emit_speech  -> espeak 'Driving forward 1 meter'" in report
    assert "turn_by      -> easygopigo3.turn_degrees(90.0)" in report


def test_arc_drive_lowers_distance_to_orbit_radius() -> None:
    """RFC-0630: `drive.distance` is the path length swept over `arc`, so the arc
    radius is distance / arc-in-radians, not distance itself (Discussion #572).

    "Orbit 180 degrees with a 5 cm radius" is a 0.157 m arc (pi x 0.05), and must
    lower to easygopigo3.orbit(180, 5.0). Regression for the bug where `distance`
    was passed straight in as the orbit radius.
    """
    if str(EX) not in sys.path:
        sys.path.insert(0, str(EX))
    from gopigo3_adapter import GoPiGo3Adapter

    class _FakeBot:
        def __init__(self) -> None:
            self.calls: list[tuple[float, float]] = []

        def orbit(self, degrees: float, radius_cm: float) -> None:
            self.calls.append((round(degrees, 1), round(radius_cm, 1)))

    adapter = GoPiGo3Adapter()
    adapter._gpg = _FakeBot()  # bypass the lazy easygopigo3 import (hermetic)
    adapter.drive_by(distance=math.pi * 0.05, arc=180.0)  # 5 cm radius, half circle
    assert adapter._gpg.calls == [(180.0, 5.0)]
    assert adapter.call_log[-1]["hw"] == "orbit(180.0, 5.0)"


def test_radius_form_lowers_to_orbit_without_arithmetic(tmp_path) -> None:
    """RFC-0665: the radius form makes the #572 case correct end-to-end.

    "Orbit 180 degrees with a 5 cm radius" is written `drive: {radius: 0.05, arc:
    180}` with no arc-length arithmetic. The runtime resolves it to the arc length
    (0.05 x pi) and the adapter recovers the 5 cm radius, so it lowers to
    easygopigo3.orbit(180, 5.0). Under the arc-length form a model that doubled the
    arithmetic drove a 10 cm arc; the radius form removes that failure mode.
    """
    gen = _load_gen()
    prog = tmp_path / "orbit.urml.yaml"
    prog.write_text(
        "profile: [educational]\n"
        "behavior:\n"
        "  type: sequence\n"
        "  steps:\n"
        "  - drive: { radius: 0.05, arc: 180 }\n",
        encoding="utf-8",
    )
    report = gen.run_program_file(str(prog), prefer_real=False)
    assert "[VALID] program file: orbit.urml.yaml" in report
    assert "drive_by     -> easygopigo3.orbit(180.0, 5.0)" in report
    assert "Dry run" in report


def test_default_is_a_dry_run_that_cannot_move_a_robot() -> None:
    """Safety: bare invocation must never bind the real backend (Discussion #542).

    A demo in a validate-before-actuate project must not surprise-drive a robot.
    The default backend is the fake, the real library is never imported, and the
    report says it is a dry run.
    """
    gen = _load_gen()
    gen.render_report()  # default: prefer_real=False
    mod = sys.modules.get("easygopigo3")
    assert mod is not None and getattr(mod, "_URML_FAKE", False), (
        "render_report() must install the fake easygopigo3 by default, never the real one"
    )
    assert gen._ensure_easygopigo3() == "fake"
    assert "dry run" in gen.render_report()


def test_help_flag_does_not_execute() -> None:
    """`-h` must print help and exit, not run the programs (the #542 footgun)."""
    import pytest

    gen = _load_gen()
    with pytest.raises(SystemExit):
        gen.main(["-h"])


def test_run_program_file(tmp_path) -> None:
    """`-f` runs a user's own translated URML program (Discussion #523)."""
    gen = _load_gen()
    prog = tmp_path / "drive10.urml.yaml"
    prog.write_text(
        "profile: [educational]\n"
        "behavior:\n"
        "  type: sequence\n"
        "  steps:\n"
        "  - speak: { utterance: Driving forward 10 centimeters }\n"
        "  - drive: { distance: 0.1 }\n",
        encoding="utf-8",
    )
    report = gen.run_program_file(str(prog), prefer_real=False)
    assert "[VALID] program file: drive10.urml.yaml" in report
    assert "drive_by     -> easygopigo3.drive_cm(10.0)" in report
    assert "Dry run" in report
    # The report records which URML versions ran it (Discussion #523), auto-derived.
    assert "running on urml-validator" in report
    # A missing file reports cleanly, never raises.
    assert "[ERROR] no such program file" in gen.run_program_file(str(tmp_path / "nope.yaml"))


def test_version_line_is_auto_derived() -> None:
    """`--version` exits cleanly; the string is read from package metadata, not hand-edited (#523)."""
    import pytest

    gen = _load_gen()
    line = gen._version_line()
    assert "urml-validator" in line and "urml-ros2-runtime" in line
    with pytest.raises(SystemExit):
        gen.main(["--version"])


def test_tts_engine_class_selects_speech_backend() -> None:
    """RFC-0589: the manifest's tts_engine_class maps to a backend via a dispatch dict.

    An explicit `speak=` always wins; an omitted one resolves the declared class
    through `_TTS_ENGINES`, defaulting to espeak and falling back to espeak for a
    class this adapter does not register (never crashing on the declaration).
    """
    if str(EX) not in sys.path:
        sys.path.insert(0, str(EX))
    from gopigo3_adapter import GoPiGo3Adapter, _espeak

    assert GoPiGo3Adapter()._speak is _espeak
    assert GoPiGo3Adapter(tts_engine_class="espeak")._speak is _espeak
    # A class this adapter has no backend for falls back to espeak, not an error.
    assert GoPiGo3Adapter(tts_engine_class="piper")._speak is _espeak

    def my_sink(_utterance: str) -> None:
        return None

    # An explicit speak= always wins over the declared class.
    assert GoPiGo3Adapter(speak=my_sink, tts_engine_class="espeak")._speak is my_sink


def test_espeak_prefers_espeak_ng_then_falls_back(monkeypatch) -> None:
    """RFC-0589 Q1: the default backend uses espeak-ng when present, else espeak,
    and always passes the utterance as a list arg (no shell, no injection)."""
    if str(EX) not in sys.path:
        sys.path.insert(0, str(EX))
    import gopigo3_adapter

    calls: list[list[str]] = []

    class _R:
        returncode = 0

    def _fake_run(argv, *args, **kwargs):  # tolerate stdout=/check= etc.
        calls.append(argv)
        return _R()

    monkeypatch.setattr(gopigo3_adapter.subprocess, "run", _fake_run)

    monkeypatch.setattr(
        gopigo3_adapter.shutil, "which", lambda name: "/usr/bin/espeak-ng" if name == "espeak-ng" else None
    )
    gopigo3_adapter._espeak("hello world")
    assert calls[-1] == ["espeak-ng", "hello world"]  # list form, espeak-ng chosen

    monkeypatch.setattr(gopigo3_adapter.shutil, "which", lambda name: None)
    gopigo3_adapter._espeak("hello world")
    assert calls[-1] == ["espeak", "hello world"]  # falls back to espeak


def test_speech_is_gated_by_execute(tmp_path, monkeypatch) -> None:
    """RFC-0589 Q2: speech is an actuation, gated like the wheels. A dry run captures
    it (never audible); only --execute routes it to the real espeak backend."""
    gen = _load_gen()
    if str(EX) not in sys.path:
        sys.path.insert(0, str(EX))
    import gopigo3_adapter

    emitted: list[str] = []
    monkeypatch.setitem(gopigo3_adapter._TTS_ENGINES, "espeak", emitted.append)

    prog = tmp_path / "say.urml.yaml"
    prog.write_text(
        "profile: [educational]\n"
        "behavior:\n"
        "  type: sequence\n"
        "  steps:\n"
        "  - speak: { utterance: hello }\n",
        encoding="utf-8",
    )

    # Dry run: the real speech backend must NOT be invoked.
    gen.run_program_file(str(prog), prefer_real=False)
    assert emitted == []
    # Execute: speech routes to the (here, recorded) real backend.
    gen.run_program_file(str(prog), prefer_real=True)
    assert emitted == ["hello"]
