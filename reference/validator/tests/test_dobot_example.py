"""The Dobot Magician pick-and-place example must be deterministic and true.

Mirrors the fieldbus / opcua / relative-motion example guards: the generator is
deterministic, the committed ``pick-place-report.txt`` matches it, and the
validator decides the four cases correctly (one valid pick-and-place, three
distinct capability rejections). From the magician_ros2 engagement (#11).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "dobot-magician"
GEN_PATH = EX / "check_pick_place.py"
COMMITTED = EX / "pick-place-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("check_pick_place", GEN_PATH)
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
        "examples/dobot-magician/pick-place-report.txt is stale; "
        "run `python examples/dobot-magician/check_pick_place.py` and commit."
    )


def test_gate_decides_correctly() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert report.count("[VALID]") == 1
    assert report.count("[REJECTED]") == 3
    assert "capability.missing_object_class" in report
    assert "capability.missing_location" in report
    assert "capability.missing_gripper" in report
