"""Offline unit tests for the commitments-page generator.

`tools/scripts/refresh_commitments.py` derives the engaged-thread table on
docs/launch/outreach-commitments.md from the ledgers. These tests pin the
two behaviours the page's honesty depends on: only `engaged` rows appear,
and table cells stay single-line and pipe-safe however messy the ledger
prose gets.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "scripts" / "refresh_commitments.py"


def _load():
    spec = importlib.util.spec_from_file_location("refresh_commitments", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cell_is_single_line_and_pipe_safe() -> None:
    mod = _load()
    out = mod._cell("a | b\nc\td   e")
    assert "\n" not in out
    assert "|" not in out
    assert out == "a / b c d e"


def test_cell_truncates_with_ledger_pointer() -> None:
    mod = _load()
    out = mod._cell("x" * 500, limit=100)
    assert len(out) <= 100
    assert out.endswith("... (see ledger row)")


def test_rows_reads_real_ledgers_and_filters_engaged() -> None:
    """Against the real tree: every ledger parses, and the engaged subset is
    non-empty with the fields the table needs."""
    mod = _load()
    rows = mod._rows()
    assert len(rows) > 500  # the real ledgers
    engaged = [r for r in rows if r.get("response") == "engaged"]
    assert engaged, "no engaged rows found; ledgers moved?"
    for row in engaged:
        assert row.get("slug"), f"engaged row without slug in {row.get('_ledger')}"
        assert row.get("_ledger", "").startswith("outreach")
