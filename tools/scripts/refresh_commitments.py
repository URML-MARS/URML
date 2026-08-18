"""Regenerate the engaged-thread table for docs/launch/outreach-commitments.md.

The commitments page rotted because it was hand-enumerated: by 2026-08 it
covered 7 of 70 engaged threads and was 12 weeks stale. This script derives
the full engaged-thread table from the ledgers so the page can never again
silently under-report what URML owes people.

Same posture as refresh_audit.py: read-only, deterministic, prints a
paste-ready markdown block plus data-quality warnings. It does NOT edit the
page; the maintainer reads, sanity-checks, and transcribes. The hand-written
per-thread commitment checklists on the page remain hand-written (a promise
is prose, not a ledger field); this table is the index that keeps them
honest.

Usage:

    python tools/scripts/refresh_commitments.py
"""

from __future__ import annotations

import glob
import os.path
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def _rows() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(glob.glob(str(REPO / "examples" / "lighthouses" / "outreach*.yaml"))):
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict):
            data = data.get("targets", [])
        for row in data or []:
            if isinstance(row, dict):
                row["_ledger"] = os.path.basename(path)
                rows.append(row)
    return rows


def _cell(text: str, limit: int = 220) -> str:
    """One table cell: pipe-safe, single-line, truncated with a ledger pointer."""
    flat = " ".join(str(text).split()).replace("|", "/")
    if len(flat) <= limit:
        return flat
    return flat[: limit - 22].rstrip() + " ... (see ledger row)"


def main() -> int:
    engaged = [r for r in _rows() if r.get("response") == "engaged"]
    engaged.sort(key=lambda r: str(r.get("last_touch", "")), reverse=True)

    warnings: list[str] = []
    for row in engaged:
        for field in ("next_action", "notes"):
            if not str(row.get(field, "")).strip():
                warnings.append(f"  {row['_ledger']} :: {row.get('slug')}: empty `{field}`")

    print(f"Engaged threads: {len(engaged)} (derived from the ledgers, newest touch first)\n")
    if warnings:
        print("DATA-QUALITY WARNINGS (fix the ledger, then re-run):")
        print("\n".join(warnings) + "\n")

    print("================ paste-ready markdown for outreach-commitments.md ================\n")
    print("| # | Thread | Sector | Last touch | Standing state (from the ledger's `next_action`) |")
    print("|---:|---|---|---|---|")
    for i, row in enumerate(engaged, 1):
        slug = row.get("slug", "?")
        url = row.get("posted_url", "")
        thread = f"[{slug}]({url})" if url else slug
        print(
            f"| {i} | {thread} | {row.get('sector', '?')} | "
            f"{row.get('last_touch', '?')} | {_cell(row.get('next_action', ''))} |"
        )
    print(
        "\n===================================================================================\n"
        "Now: transcribe into docs/launch/outreach-commitments.md (the generated-table\n"
        "section), review the hand-written checklists above it, and check off or add\n"
        "promises. Do not auto-edit."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
