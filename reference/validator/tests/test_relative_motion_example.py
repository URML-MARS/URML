"""The RFC-0630 relative-motion example must be deterministic and true.

Mirrors the fieldbus / opcua example guards: the generator is deterministic, the
committed ``relative-motion-report.txt`` matches it, and the validator decides
the four cases correctly (one valid square, three distinct gate rejections).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "educational" / "relative-motion"
GEN_PATH = EX / "check_relative_motion.py"
COMMITTED = EX / "relative-motion-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("check_relative_motion", GEN_PATH)
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
        "examples/educational/relative-motion/relative-motion-report.txt is stale; "
        "run `python examples/educational/relative-motion/check_relative_motion.py` and commit."
    )


def test_gate_decides_correctly() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert report.count("[VALID]") == 1
    assert report.count("[REJECTED]") == 3
    assert "capability.relative_motion_requires_educational" in report
    assert "capability.relative_motion_unsupported" in report
    assert "capability.relative_distance_exceeded" in report
