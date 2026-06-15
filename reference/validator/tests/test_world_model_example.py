"""The world-model example (RFC-0615) must be deterministic and true.

Mirrors the other example guards: deterministic generator, committed
``world-model-report.txt`` matches, and the validator decides correctly (a known
room and a detectable object are accepted; an undeclared room and an object not
in the vocabulary are refused). From the linorobot2 / Dallas PRG feedback.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "world-model"
GEN_PATH = EX / "check_world_model.py"
COMMITTED = EX / "world-model-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("check_world_model", GEN_PATH)
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
        "examples/world-model/world-model-report.txt is stale; "
        "run `python examples/world-model/check_world_model.py` and commit."
    )


def test_world_model_decides_correctly() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert report.count("[ACCEPT]") == 2
    assert report.count("[REFUSE]") == 2
    assert "capability.missing_location" in report      # undeclared room
    assert "capability.missing_object_class" in report  # object not in vocabulary
    assert "known rooms: kitchen, living_room" in report
