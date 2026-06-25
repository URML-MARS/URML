"""The GoPiGo3 worked example must be deterministic and true.

Mirrors the other example guards: the generator is deterministic, the committed
``gopigo3-report.txt`` matches it, and the example shows the end-to-end
@slowrunner asked for on Discussion #523 (a validated URML program driving a basic
GoPiGo3 through GoPiGo3Adapter, no ROS). Hermetic: the example injects a fake
``easygopigo3`` so no robot and no library are needed.
"""

from __future__ import annotations

import importlib.util
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
