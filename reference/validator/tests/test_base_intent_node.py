"""The quadruped base-intent node example must be deterministic and true.

Mirrors the VLA / fieldbus / planning export guards: the generator is
deterministic, the committed ``base-intent-report.txt`` matches it, and the node
decides correctly (admissible base intents become a Twist; each base bound, when
exceeded, refuses the intent). The worked example for RFC-0518, surfaced by the
quadruped_ros2_control engagement (legubiao/quadruped_ros2_control#65).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "mobile-base"
GEN_PATH = EX / "validate_base_intents.py"
COMMITTED = EX / "base-intent-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("validate_base_intents", GEN_PATH)
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
        "examples/mobile-base/base-intent-report.txt is stale; "
        "run `python examples/mobile-base/validate_base_intents.py` and commit."
    )


def test_node_decides_correctly() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Two admissible intents become a Twist; four are refused, one per base bound.
    assert report.count("[DISPATCH]") == 2
    assert report.count("[REJECTED]") == 4
    assert "Twist(linear.x=1.0, angular.z=0.0)" in report
    for bound in (
        "max_velocity (2.5 > 1.5)",
        "max_angular_velocity (1.8 > 1.0)",
        "max_traversable_slope_deg (40.0 > 25.0)",
        "max_payload (20.0 > 10.0)",
    ):
        assert bound in report
    assert "No Twist sent." in report
