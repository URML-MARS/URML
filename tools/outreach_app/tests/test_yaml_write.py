"""Round-trip + formatting-fidelity tests for the YAML write path.

The dashboard's write surface (Add comment / Add directive / Mark done)
mutates `examples/lighthouses/outreach*.yaml` files in place. The
contract: only the targeted list grows or its status changes; no other
formatting in the file shifts. These tests assert that contract on a
temporary copy of a real ledger so we never depend on synthetic data.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from tools.outreach_app import yaml_write


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_LEDGER = REPO_ROOT / "examples" / "lighthouses" / "outreach-move3.yaml"


@pytest.fixture()
def temp_ledger(tmp_path, monkeypatch):
    """Copy a real ledger into a temp dir and rewire yaml_write to use it."""
    temp_dir = tmp_path / "lighthouses"
    temp_dir.mkdir()
    target = temp_dir / SOURCE_LEDGER.name
    shutil.copy(SOURCE_LEDGER, target)
    monkeypatch.setattr(yaml_write, "LEDGER_DIR", temp_dir)
    return target


def _load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _find(rows: list[dict], slug: str) -> dict:
    for r in rows:
        if r.get("slug") == slug:
            return r
    raise KeyError(slug)


def test_append_comment_adds_one_entry(temp_ledger):
    before = _load(temp_ledger)
    before_row = _find(before, "petoi-bittle")
    initial_comment_count = len(before_row.get("comments", []) or [])

    result = yaml_write.append_comment("outreach-move3.yaml", "petoi-bittle", "test comment")
    assert result["text"] == "test comment"

    after = _load(temp_ledger)
    after_row = _find(after, "petoi-bittle")
    assert len(after_row["comments"]) == initial_comment_count + 1
    assert after_row["comments"][-1]["text"] == "test comment"
    assert "date" in after_row["comments"][-1]


def test_append_directive_adds_pending_entry(temp_ledger):
    before = _load(temp_ledger)
    before_row = _find(before, "petoi-bittle")
    initial_count = len(before_row.get("claude_directives", []) or [])

    yaml_write.append_directive(
        "outreach-move3.yaml", "petoi-bittle", "do the thing", "pending",
    )

    after = _load(temp_ledger)
    after_row = _find(after, "petoi-bittle")
    assert len(after_row["claude_directives"]) == initial_count + 1
    entry = after_row["claude_directives"][-1]
    assert entry["text"] == "do the thing"
    assert entry["status"] == "pending"


def test_update_directive_status_toggles_in_place(temp_ledger):
    yaml_write.append_directive(
        "outreach-move3.yaml", "petoi-bittle", "x", "pending",
    )
    row_before = _find(_load(temp_ledger), "petoi-bittle")
    seq = len(row_before["claude_directives"]) - 1

    yaml_write.update_directive_status(
        "outreach-move3.yaml", "petoi-bittle", seq, "done",
    )

    row_after = _find(_load(temp_ledger), "petoi-bittle")
    assert row_after["claude_directives"][seq]["status"] == "done"


def test_append_preserves_other_rows_byte_for_byte(temp_ledger):
    """The critical formatting-fidelity check: a write to one row must
    not perturb any other row's serialization."""
    # Read the file as bytes, find the other-rows region (everything after
    # the petoi-bittle row), assert it stays identical after a write.
    original = temp_ledger.read_text(encoding="utf-8")

    yaml_write.append_comment("outreach-move3.yaml", "petoi-bittle", "test")
    mutated = temp_ledger.read_text(encoding="utf-8")

    # Locate "- slug: hiwonder" (the next row after petoi-bittle in this
    # ledger). Everything from there to EOF must be unchanged.
    marker = "- slug: hiwonder"
    assert marker in original
    assert marker in mutated
    assert original[original.index(marker):] == mutated[mutated.index(marker):], (
        "Writing to one row leaked formatting changes into a later row."
    )


def test_empty_text_raises(temp_ledger):
    with pytest.raises(ValueError):
        yaml_write.append_comment("outreach-move3.yaml", "petoi-bittle", "")
    with pytest.raises(ValueError):
        yaml_write.append_directive("outreach-move3.yaml", "petoi-bittle", "  ", "pending")


def test_invalid_directive_status_raises(temp_ledger):
    with pytest.raises(ValueError):
        yaml_write.append_directive(
            "outreach-move3.yaml", "petoi-bittle", "x", "definitely-not-a-status",
        )


def test_unknown_slug_raises(temp_ledger):
    with pytest.raises(KeyError):
        yaml_write.append_comment("outreach-move3.yaml", "no-such-slug", "x")
