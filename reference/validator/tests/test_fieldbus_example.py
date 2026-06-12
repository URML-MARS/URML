"""The fieldbus declaration example must be deterministic and true.

Mirrors the VLA / esmini / ros2_kortex export guards: the generator is
deterministic, the committed ``operation-mode-report.txt`` matches it, and the
validator decides correctly across all three fieldbus blocks surfaced by the
ethercat_driver_ros2 engagement (RFC-0320): operation mode (RFC-0016 cyclic /
RFC-0469 acyclic), clock / time synchronization (RFC-0477), and ordered
bring-up / recovery (RFC-0478).
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


def test_fieldbus_blocks_decide_correctly() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Four coherent declarations are valid; three incoherent ones are rejected,
    # one per fieldbus block (operation mode, clock, bring-up ordering).
    assert report.count("[VALID]") == 4
    assert report.count("[REJECTED]") == 3
    assert "capability.acyclic_timeout_shorter_than_cycle" in report  # RFC-0469
    assert "capability.clock_sync_protocol_required" in report  # RFC-0477
    assert "capability.bringup_dependency_cycle" in report  # RFC-0478
    # The three blocks are shown distinctly.
    assert "Operation mode" in report
    assert "Clock / time synchronization" in report
    assert "Ordered bring-up / recovery" in report
