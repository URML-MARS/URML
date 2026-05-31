"""Schema-v2 conformance test for every outreach ledger row.

`examples/lighthouses/outreach*.yaml` rows must carry five structured
fields added by RFC-0275: `tier`, `country`, `sector`, `comments`,
`claude_directives`. This test asserts the shape and the enum
membership. It complements (does not replace) the existing
`test_outreach_ledger.py`, which still enforces Move-1 parity with
`demo.py::LIGHTHOUSES`.

Scope:

  * Runs against every `examples/lighthouses/outreach*.yaml` (Move-1
    plus Move-2-through-Move-18).
  * Per row, asserts the 5 schema-v2 fields are present, that the
    enum-valued ones are in their respective enums, and that the
    workspace lists (`comments`, `claude_directives`) match the
    documented shape.

The migration script `tools/scripts/migrate_outreach_schema_v2.py`
backfills the 5 fields mechanically; this test is the gate that
prevents drift back into free-text.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = REPO_ROOT / "examples" / "lighthouses"

VALID_TIER = {"A", "B", "C"}

VALID_SECTOR = {
    "robot-platform",
    "component-vendor",
    "substrate-runtime",
    "protocol-substrate",
    "middleware",
    "simulator",
    "perception",
    "ai-language",
    "framework-skill",
    "governance-body",
    "conceptual-peer",
    "education-toolchain",
    "medical",
    "agriculture",
    "delivery",
}

VALID_DIRECTIVE_STATUS = {"pending", "done", "skip"}

# ISO 3166-1 alpha-2 plus the INTL sentinel for multi-national foundations.
COUNTRY_RE = re.compile(r"^(?:[A-Z]{2}|INTL)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _ledger_paths() -> list[Path]:
    paths = sorted(LEDGER_DIR.glob("outreach*.yaml"))
    assert paths, f"no outreach*.yaml files found under {LEDGER_DIR}"
    return paths


def _load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        rows = yaml.safe_load(fh)
    assert isinstance(rows, list), f"{path.name} must be a YAML list"
    return rows


def _ids(paths: list[Path]) -> list[str]:
    return [p.name for p in paths]


@pytest.fixture(scope="module")
def ledger_paths() -> list[Path]:
    return _ledger_paths()


@pytest.mark.parametrize("path", _ledger_paths(), ids=_ids(_ledger_paths()))
def test_every_row_has_schema_v2_fields(path: Path) -> None:
    rows = _load(path)
    required = {"tier", "country", "sector", "comments", "claude_directives"}
    for row in rows:
        slug = row.get("slug", "?")
        missing = required - row.keys()
        assert not missing, (
            f"{path.name}::{slug}: missing schema-v2 fields {sorted(missing)!r}"
        )


@pytest.mark.parametrize("path", _ledger_paths(), ids=_ids(_ledger_paths()))
def test_tier_is_in_enum(path: Path) -> None:
    for row in _load(path):
        slug = row.get("slug", "?")
        tier = row.get("tier")
        assert tier in VALID_TIER, (
            f"{path.name}::{slug}: tier={tier!r} is not one of {sorted(VALID_TIER)!r}"
        )


@pytest.mark.parametrize("path", _ledger_paths(), ids=_ids(_ledger_paths()))
def test_country_matches_iso_alpha2_or_intl(path: Path) -> None:
    for row in _load(path):
        slug = row.get("slug", "?")
        country = row.get("country")
        assert isinstance(country, str) and COUNTRY_RE.match(country), (
            f"{path.name}::{slug}: country={country!r} is not ISO alpha-2 "
            f"or the INTL sentinel"
        )


@pytest.mark.parametrize("path", _ledger_paths(), ids=_ids(_ledger_paths()))
def test_sector_is_in_enum(path: Path) -> None:
    for row in _load(path):
        slug = row.get("slug", "?")
        sector = row.get("sector")
        assert sector in VALID_SECTOR, (
            f"{path.name}::{slug}: sector={sector!r} is not in the closed enum "
            f"{sorted(VALID_SECTOR)!r}"
        )


@pytest.mark.parametrize("path", _ledger_paths(), ids=_ids(_ledger_paths()))
def test_comments_list_shape(path: Path) -> None:
    for row in _load(path):
        slug = row.get("slug", "?")
        comments = row.get("comments")
        assert isinstance(comments, list), (
            f"{path.name}::{slug}: comments must be a list, got {type(comments).__name__}"
        )
        for i, c in enumerate(comments):
            assert isinstance(c, dict), (
                f"{path.name}::{slug}: comments[{i}] must be a dict"
            )
            assert "date" in c and "text" in c, (
                f"{path.name}::{slug}: comments[{i}] missing date/text keys"
            )
            assert isinstance(c["date"], str) and DATE_RE.match(c["date"]), (
                f"{path.name}::{slug}: comments[{i}].date={c['date']!r} "
                f"is not YYYY-MM-DD"
            )
            assert isinstance(c["text"], str) and c["text"], (
                f"{path.name}::{slug}: comments[{i}].text must be a non-empty string"
            )


@pytest.mark.parametrize("path", _ledger_paths(), ids=_ids(_ledger_paths()))
def test_claude_directives_list_shape(path: Path) -> None:
    for row in _load(path):
        slug = row.get("slug", "?")
        directives = row.get("claude_directives")
        assert isinstance(directives, list), (
            f"{path.name}::{slug}: claude_directives must be a list, "
            f"got {type(directives).__name__}"
        )
        for i, d in enumerate(directives):
            assert isinstance(d, dict), (
                f"{path.name}::{slug}: claude_directives[{i}] must be a dict"
            )
            for k in ("date", "text", "status"):
                assert k in d, (
                    f"{path.name}::{slug}: claude_directives[{i}] missing {k!r}"
                )
            assert isinstance(d["date"], str) and DATE_RE.match(d["date"]), (
                f"{path.name}::{slug}: claude_directives[{i}].date={d['date']!r} "
                f"is not YYYY-MM-DD"
            )
            assert isinstance(d["text"], str) and d["text"], (
                f"{path.name}::{slug}: claude_directives[{i}].text must be "
                f"a non-empty string"
            )
            assert d["status"] in VALID_DIRECTIVE_STATUS, (
                f"{path.name}::{slug}: claude_directives[{i}].status="
                f"{d['status']!r} is not one of {sorted(VALID_DIRECTIVE_STATUS)!r}"
            )


def test_no_ledger_is_silently_skipped(ledger_paths: list[Path]) -> None:
    """A defensive cross-check: enumerate the ledger files for visibility.

    If a new outreach-moveNN.yaml lands and someone forgets to wire it into
    a parametrized test, this fixture still touches it.
    """
    assert len(ledger_paths) >= 18, (
        f"expected at least 18 outreach ledger files; found {len(ledger_paths)}"
    )
