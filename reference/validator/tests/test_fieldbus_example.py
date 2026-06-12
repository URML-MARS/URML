"""The fieldbus operation-mode example must be deterministic and true.

Mirrors the VLA / esmini / ros2_kortex export guards: the generator is
deterministic, the committed ``operation-mode-report.txt`` matches it, and the
validator decides correctly (cyclic-only and coherent-acyclic declarations are
valid, an SDO timeout shorter than one control cycle is rejected). The worked
example for RFC-0469 (the acyclic operation-mode declaration), surfaced by the
ethercat_driver_ros2 engagement (RFC-0320).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "fieldbus"
GEN_PATH = EX / "check_operation_modes.py"
COMMITTED = EX / "operation-mode-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("check_operation_modes", GEN_PATH)
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
        "examples/fieldbus/operation-mode-report.txt is stale; "
        "run `python examples/fieldbus/check_operation_modes.py` and commit."
    )


def test_operation_modes_decide_correctly() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Cyclic-only and coherent-acyclic are valid; the too-short SDO timeout is not.
    assert report.count("[VALID]") == 2
    assert report.count("[REJECTED]") == 1
    assert "capability.acyclic_timeout_shorter_than_cycle" in report
    # Both regimes are shown distinctly: a cyclic watchdog and an acyclic timeout.
    assert "watchdog" in report
    assert "timeout" in report
