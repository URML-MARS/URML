"""The TurtleBot 4 worked example must be deterministic and true.

Mirrors the other example guards: the generator is deterministic, the committed
``turtlebot4-report.txt`` matches it, and the example shows the answer to
Discussion #526 (a mapped ROS 2 robot uses move_to a named pose, lowered to a Nav2
goal, with Nav2 knobs staying in adapter config). Hermetic: validator + mock
substrate, no ROS, no robot.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "turtlebot4"
GEN_PATH = EX / "run_turtlebot4.py"
COMMITTED = EX / "turtlebot4-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_turtlebot4", GEN_PATH)
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
        "examples/turtlebot4/turtlebot4-report.txt is stale; "
        "run `python examples/turtlebot4/run_turtlebot4.py` and commit."
    )


def test_move_to_lowers_to_a_nav_goal() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "[VALID] move_to kitchen" in report
    assert "[REJECTED]" not in report
    # move_to lowers to a navigation goal (Nav2 on a real TB4).
    assert "send_navigation_goal(location='kitchen')  [Nav2 NavigateToPose]" in report
    assert "executed 3 steps, success=True" in report
    # The substrate-neutral point: Nav2 knobs stay in adapter config.
    assert "live in the ROS 2 adapter's deployment config" in report
