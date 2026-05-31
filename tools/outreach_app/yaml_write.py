"""Atomic YAML writes back to `examples/lighthouses/outreach*.yaml`.

Used by the row detail drawer when the maintainer adds a comment or
directive, and by the directives page when they click "Mark done"
or "Mark skip". Uses `ruamel.yaml` round-trip mode so existing
formatting and inline comments are preserved (so `git diff` shows
only the actual change, not formatting churn).

Every write is atomic: load the file, mutate the in-memory dict,
write to a tempfile in the same directory, rename over the original.
"""

from __future__ import annotations

import datetime as _dt
import os
import tempfile
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = REPO_ROOT / "examples" / "lighthouses"

VALID_DIRECTIVE_STATUS = {"pending", "done", "skip"}


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    y.indent(mapping=2, sequence=2, offset=0)
    return y


def _ledger_path(wave: str) -> Path:
    path = LEDGER_DIR / wave
    if not path.exists():
        raise FileNotFoundError(f"Ledger file not found: {path}")
    return path


def _today() -> str:
    return _dt.date.today().isoformat()


def _load(path: Path):
    yaml = _yaml()
    return yaml, yaml.load(path.read_text(encoding="utf-8"))


def _atomic_write(path: Path, yaml: YAML, data) -> None:
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            yaml.dump(data, f)
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def _find_row(data, slug: str) -> CommentedMap | None:
    if not isinstance(data, CommentedSeq):
        return None
    for row in data:
        if isinstance(row, CommentedMap) and row.get("slug") == slug:
            return row
    return None


def append_comment(wave: str, slug: str, text: str) -> dict:
    """Append `{date: today, text: text}` to `comments` on the named row.

    Returns the new comment dict. Raises if the row or ledger is not found.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Comment text must be non-empty.")
    path = _ledger_path(wave)
    yaml, data = _load(path)
    row = _find_row(data, slug)
    if row is None:
        raise KeyError(f"Slug {slug!r} not found in {wave}")
    if "comments" not in row or not isinstance(row.get("comments"), list):
        row["comments"] = CommentedSeq()
    entry = CommentedMap()
    entry["date"] = _today()
    entry["text"] = text
    row["comments"].append(entry)
    _atomic_write(path, yaml, data)
    return {"date": entry["date"], "text": entry["text"]}


def append_directive(wave: str, slug: str, text: str, status: str = "pending") -> dict:
    """Append `{date, text, status}` to `claude_directives` on the named row."""
    text = (text or "").strip()
    if not text:
        raise ValueError("Directive text must be non-empty.")
    if status not in VALID_DIRECTIVE_STATUS:
        raise ValueError(
            f"status must be one of {sorted(VALID_DIRECTIVE_STATUS)}, got {status!r}"
        )
    path = _ledger_path(wave)
    yaml, data = _load(path)
    row = _find_row(data, slug)
    if row is None:
        raise KeyError(f"Slug {slug!r} not found in {wave}")
    if "claude_directives" not in row or not isinstance(row.get("claude_directives"), list):
        row["claude_directives"] = CommentedSeq()
    entry = CommentedMap()
    entry["date"] = _today()
    entry["text"] = text
    entry["status"] = status
    row["claude_directives"].append(entry)
    _atomic_write(path, yaml, data)
    return {"date": entry["date"], "text": entry["text"], "status": status}


def update_directive_status(wave: str, slug: str, seq: int, new_status: str) -> None:
    """Set status on the directive at index `seq` of the named row's list."""
    if new_status not in VALID_DIRECTIVE_STATUS:
        raise ValueError(
            f"status must be one of {sorted(VALID_DIRECTIVE_STATUS)}, got {new_status!r}"
        )
    path = _ledger_path(wave)
    yaml, data = _load(path)
    row = _find_row(data, slug)
    if row is None:
        raise KeyError(f"Slug {slug!r} not found in {wave}")
    directives = row.get("claude_directives") or []
    if not isinstance(directives, list) or seq < 0 or seq >= len(directives):
        raise IndexError(
            f"Directive index {seq} out of range for {slug} in {wave} "
            f"(have {len(directives)})"
        )
    directive = directives[seq]
    if not isinstance(directive, dict):
        raise TypeError(f"Directive at index {seq} is not a dict")
    directive["status"] = new_status
    _atomic_write(path, yaml, data)
