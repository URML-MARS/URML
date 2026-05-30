#!/usr/bin/env python3
"""Regenerate `tools/.outreach.db` from every outreach ledger YAML.

Per RFC-0275 (outreach ledger schema v2). YAML is the source of truth;
the SQLite mirror is a derived view, regenerated on demand, and never
committed. Datasette browses the mirror via `make outreach-browse`.

Tables built:

    waves               One row per outreach-moveN.yaml (plus Move-1).
    targets             One row per ledger entry, with the structured
                        schema-v2 columns plus computed staleness flags
                        and per-row workspace counts.
    comments            Long-form table of every `{date, text}` comment.
    claude_directives   Long-form table of every `{date, text, status}`
                        directive. Status indexed for the "what is
                        pending for Claude" canned query.

Stale-thread rule: `sent_at != ''` AND today minus `sent_at` >= 28 days
AND `response == 'none'`. Indexed for the radar canned query.

Usage:
    python tools/scripts/refresh_outreach_db.py [--db PATH]

Default DB path is `tools/.outreach.db` (gitignored). The script is
deterministic: same inputs in the YAML files produce byte-identical
SQLite output.
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = REPO_ROOT / "examples" / "lighthouses"
DEFAULT_DB = REPO_ROOT / "tools" / "outreach.db"

WAVE_MOVE_NUM = re.compile(r"outreach-move(\d+)\.yaml")
STALE_DAYS = 28


SCHEMA = """
CREATE TABLE waves (
    wave              TEXT PRIMARY KEY,
    move_num          INTEGER NOT NULL,
    total             INTEGER NOT NULL,
    posted            INTEGER NOT NULL,
    engaged           INTEGER NOT NULL,
    wontfix           INTEGER NOT NULL,
    declined          INTEGER NOT NULL,
    acked             INTEGER NOT NULL,
    none_response     INTEGER NOT NULL,
    stale             INTEGER NOT NULL
);

CREATE TABLE targets (
    wave                       TEXT NOT NULL,
    slug                       TEXT NOT NULL,
    rfc                        INTEGER,
    sent_at                    TEXT,
    posted_url                 TEXT,
    channel                    TEXT,
    contact                    TEXT,
    last_touch                 TEXT,
    response                   TEXT,
    tier                       TEXT,
    country                    TEXT,
    sector                     TEXT,
    next_action                TEXT,
    notes                      TEXT,
    days_since_sent            INTEGER,
    days_since_touch           INTEGER,
    is_stale                   INTEGER NOT NULL,
    comment_count              INTEGER NOT NULL,
    pending_directive_count    INTEGER NOT NULL,
    move_num                   INTEGER,
    PRIMARY KEY (wave, slug),
    FOREIGN KEY (wave) REFERENCES waves(wave)
);

CREATE TABLE comments (
    wave     TEXT NOT NULL,
    slug     TEXT NOT NULL,
    seq      INTEGER NOT NULL,
    date     TEXT NOT NULL,
    text     TEXT NOT NULL,
    PRIMARY KEY (wave, slug, seq),
    FOREIGN KEY (wave, slug) REFERENCES targets(wave, slug)
);

CREATE TABLE claude_directives (
    wave     TEXT NOT NULL,
    slug     TEXT NOT NULL,
    seq      INTEGER NOT NULL,
    date     TEXT NOT NULL,
    text     TEXT NOT NULL,
    status   TEXT NOT NULL,
    PRIMARY KEY (wave, slug, seq),
    FOREIGN KEY (wave, slug) REFERENCES targets(wave, slug)
);

CREATE INDEX idx_targets_response ON targets(response);
CREATE INDEX idx_targets_tier ON targets(tier);
CREATE INDEX idx_targets_sector ON targets(sector);
CREATE INDEX idx_targets_country ON targets(country);
CREATE INDEX idx_targets_stale ON targets(is_stale);
CREATE INDEX idx_directives_status ON claude_directives(status);
"""


def _parse_date(s: object) -> date | None:
    if not s or not isinstance(s, str):
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _move_num_for(wave_file: str) -> int:
    if wave_file == "outreach.yaml":
        return 1
    m = WAVE_MOVE_NUM.match(wave_file)
    return int(m.group(1)) if m else -1


def _ledger_paths() -> list[Path]:
    return sorted(LEDGER_DIR.glob("outreach*.yaml"))


def _load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path.name}: top level is not a YAML list")
    return data


def build(db_path: Path, today: date | None = None) -> dict:
    """Build the SQLite mirror. Returns a summary dict for the caller to print."""
    today = today or date.today()
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        total_rows = 0
        wave_rows = []
        for path in _ledger_paths():
            wave = path.name
            move_num = _move_num_for(wave)
            rows = _load_rows(path)
            wave_counter = {"posted": 0, "engaged": 0, "wontfix": 0,
                            "declined": 0, "acked": 0, "none": 0, "stale": 0}
            for row in rows:
                slug = row.get("slug")
                if not slug:
                    continue

                sent_at_str = row.get("sent_at") or ""
                last_touch_str = row.get("last_touch") or ""
                if not isinstance(last_touch_str, str):
                    last_touch_str = str(last_touch_str)
                if not isinstance(sent_at_str, str):
                    sent_at_str = str(sent_at_str)

                sent_at = _parse_date(sent_at_str)
                last_touch = _parse_date(last_touch_str)

                response = row.get("response") or "none"
                days_since_sent = (today - sent_at).days if sent_at else None
                days_since_touch = (today - last_touch).days if last_touch else None
                is_stale = int(
                    sent_at is not None
                    and days_since_sent is not None
                    and days_since_sent >= STALE_DAYS
                    and response == "none"
                )

                comments = row.get("comments") or []
                if not isinstance(comments, list):
                    comments = []
                directives = row.get("claude_directives") or []
                if not isinstance(directives, list):
                    directives = []

                pending_directives = [
                    d for d in directives
                    if isinstance(d, dict) and d.get("status") == "pending"
                ]

                conn.execute(
                    """INSERT INTO targets (
                        wave, slug, rfc, sent_at, posted_url, channel,
                        contact, last_touch, response, tier, country, sector,
                        next_action, notes, days_since_sent, days_since_touch,
                        is_stale, comment_count, pending_directive_count,
                        move_num
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        wave, slug, row.get("rfc"), sent_at_str,
                        row.get("posted_url") or "", row.get("channel") or "",
                        row.get("contact") or "", last_touch_str, response,
                        row.get("tier"), row.get("country"), row.get("sector"),
                        row.get("next_action") or "", row.get("notes") or "",
                        days_since_sent, days_since_touch, is_stale,
                        len(comments), len(pending_directives), move_num,
                    ),
                )

                for i, c in enumerate(comments):
                    if not isinstance(c, dict):
                        continue
                    conn.execute(
                        "INSERT INTO comments (wave, slug, seq, date, text) VALUES (?,?,?,?,?)",
                        (wave, slug, i, c.get("date", ""), c.get("text", "")),
                    )
                for i, d in enumerate(directives):
                    if not isinstance(d, dict):
                        continue
                    conn.execute(
                        """INSERT INTO claude_directives
                           (wave, slug, seq, date, text, status)
                           VALUES (?,?,?,?,?,?)""",
                        (wave, slug, i, d.get("date", ""),
                         d.get("text", ""), d.get("status", "")),
                    )

                # Wave counters
                if sent_at_str:
                    wave_counter["posted"] += 1
                if is_stale:
                    wave_counter["stale"] += 1
                if response in wave_counter:
                    wave_counter[response] += 1
                total_rows += 1

            wave_rows.append((
                wave, move_num, len(rows),
                wave_counter["posted"], wave_counter["engaged"],
                wave_counter["wontfix"], wave_counter["declined"],
                wave_counter["acked"], wave_counter["none"],
                wave_counter["stale"],
            ))

        conn.executemany(
            """INSERT INTO waves (
                wave, move_num, total, posted, engaged, wontfix,
                declined, acked, none_response, stale
            ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            wave_rows,
        )
        conn.commit()
        cur = conn.execute("SELECT COUNT(*) FROM targets")
        target_count = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT COUNT(*) FROM targets WHERE response = 'engaged'"
        )
        engaged = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT COUNT(*) FROM targets WHERE is_stale = 1"
        )
        stale = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT COUNT(*) FROM claude_directives WHERE status = 'pending'"
        )
        pending_directives = cur.fetchone()[0]
        return {
            "db_path": str(db_path),
            "waves": len(wave_rows),
            "targets": target_count,
            "engaged": engaged,
            "stale": stale,
            "pending_directives": pending_directives,
        }
    finally:
        conn.close()


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--db", default=str(DEFAULT_DB),
        help=f"Output SQLite path. Default: {DEFAULT_DB}",
    )
    args = ap.parse_args(argv)
    summary = build(Path(args.db))
    print(
        f"Built {summary['db_path']}\n"
        f"  waves: {summary['waves']}\n"
        f"  targets: {summary['targets']}\n"
        f"  engaged: {summary['engaged']}\n"
        f"  stale (sent_at >= {STALE_DAYS}d, response=none): {summary['stale']}\n"
        f"  pending claude_directives: {summary['pending_directives']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
