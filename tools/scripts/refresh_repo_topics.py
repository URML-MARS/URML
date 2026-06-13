#!/usr/bin/env python3
"""Fetch GitHub Topics for every contact repo in `tools/outreach.db`.

Reads each `targets.contact` field, extracts the leading `OWNER/REPO`
when present, asks the GitHub API for that repo's Topics (via the
`gh` CLI so existing user auth carries through), and writes two new
tables into the same SQLite mirror:

    target_repos      (wave, slug, repo_path)             [1:1 with targets that have a repo]
    repo_topics       (repo_path, topic)                  [many topics per repo]
    repo_topic_fetch  (repo_path, fetched_at, status)     [audit + skip cache]

Idempotent. Re-running only fetches repos that are not in
`repo_topic_fetch` (or that recorded an error last time), so the
GitHub API budget stays small over time.

Usage:
    python tools/scripts/refresh_repo_topics.py            # only new repos
    python tools/scripts/refresh_repo_topics.py --force    # re-fetch all

Notes on quotas: authenticated `gh` calls have a 5000/hour limit;
this script makes one call per unique repo (typically far fewer than
the number of targets, since many targets share a vendor org).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = REPO_ROOT / "tools" / "outreach.db"

# Match a leading owner/repo at the very start of `contact`. The contact
# field looks like "PX4/PX4-Autopilot (BSD-3-Clause, ...)" or
# "realsenseai/librealsense (Apache-2.0, ...)". We allow dots and
# hyphens in owner / repo names per GitHub's allowed character set.
REPO_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*)\b")


def _extract_repo_path(contact: str | None) -> str | None:
    if not contact:
        return None
    m = REPO_RE.match(contact.strip())
    return m.group(1) if m else None


def _build_target_repos(conn: sqlite3.Connection) -> int:
    """Populate target_repos from the targets table. Idempotent: drops + recreates."""
    conn.execute("DROP TABLE IF EXISTS target_repos")
    conn.execute(
        """CREATE TABLE target_repos (
            wave TEXT NOT NULL,
            slug TEXT NOT NULL,
            repo_path TEXT NOT NULL,
            PRIMARY KEY (wave, slug)
        )"""
    )
    conn.execute("CREATE INDEX idx_target_repos_path ON target_repos(repo_path)")
    rows = conn.execute(
        "SELECT wave, slug, contact FROM targets WHERE contact IS NOT NULL AND contact != ''"
    ).fetchall()
    count = 0
    for wave, slug, contact in rows:
        repo = _extract_repo_path(contact)
        if repo:
            conn.execute(
                "INSERT OR REPLACE INTO target_repos (wave, slug, repo_path) VALUES (?, ?, ?)",
                (wave, slug, repo),
            )
            count += 1
    conn.commit()
    return count


def _ensure_topic_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS repo_topics (
            repo_path TEXT NOT NULL,
            topic TEXT NOT NULL,
            PRIMARY KEY (repo_path, topic)
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS repo_topic_fetch (
            repo_path TEXT PRIMARY KEY,
            fetched_at TEXT NOT NULL,
            status TEXT NOT NULL,
            topic_count INTEGER NOT NULL DEFAULT 0
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_repo_topics_topic ON repo_topics(topic)")
    conn.commit()


def _fetch_topics(repo_path: str) -> tuple[list[str], str]:
    """Call `gh api repos/OWNER/REPO --jq .topics`. Returns (topics, status)."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_path}", "--jq", ".topics"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return [], "gh-not-installed"
    except subprocess.TimeoutExpired:
        return [], "timeout"

    if result.returncode != 0:
        err = (result.stderr or "").strip().splitlines()
        snippet = err[-1] if err else "unknown"
        if "404" in snippet or "Not Found" in snippet:
            return [], "404"
        if "403" in snippet or "rate limit" in snippet.lower():
            return [], "rate-limit"
        return [], f"error: {snippet[:80]}"

    raw = result.stdout.strip()
    if not raw:
        return [], "ok"  # repo exists but no topics
    try:
        topics = json.loads(raw)
        if not isinstance(topics, list):
            return [], "bad-shape"
        return [str(t) for t in topics], "ok"
    except json.JSONDecodeError:
        return [], "bad-json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite mirror path")
    ap.add_argument("--force", action="store_true",
                    help="Re-fetch every repo (default: skip already-fetched).")
    ap.add_argument("--limit", type=int, default=0,
                    help="Stop after N new fetches (0 = unlimited).")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"error: {db_path} does not exist. Run refresh_outreach_db.py first.",
              file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    try:
        # 1. Rebuild target_repos from current targets.contact column.
        target_repo_count = _build_target_repos(conn)
        _ensure_topic_tables(conn)

        # 2. Find unique repo paths.
        unique_repos = [
            r[0] for r in conn.execute("SELECT DISTINCT repo_path FROM target_repos")
        ]
        print(
            f"target_repos: {target_repo_count} targets with a repo_path "
            f"across {len(unique_repos)} unique repos",
            file=sys.stderr,
        )

        # 3. Filter to repos that need fetching.
        if args.force:
            to_fetch = unique_repos
        else:
            already = {
                r[0]
                for r in conn.execute(
                    "SELECT repo_path FROM repo_topic_fetch WHERE status = 'ok'"
                )
            }
            to_fetch = [r for r in unique_repos if r not in already]
        print(f"to fetch: {len(to_fetch)} (skipping {len(unique_repos) - len(to_fetch)})",
              file=sys.stderr)

        # 4. Fetch and store.
        fetched = ok = errored = 0
        for repo in to_fetch:
            if args.limit and fetched >= args.limit:
                break
            topics, status = _fetch_topics(repo)
            conn.execute("DELETE FROM repo_topics WHERE repo_path = ?", (repo,))
            for t in topics:
                conn.execute(
                    "INSERT OR IGNORE INTO repo_topics (repo_path, topic) VALUES (?, ?)",
                    (repo, t),
                )
            conn.execute(
                """INSERT OR REPLACE INTO repo_topic_fetch
                   (repo_path, fetched_at, status, topic_count) VALUES (?, ?, ?, ?)""",
                (repo, datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 status, len(topics)),
            )
            conn.commit()
            fetched += 1
            if status == "ok":
                ok += 1
            else:
                errored += 1
            if fetched % 20 == 0:
                print(f"  ...fetched {fetched}/{len(to_fetch)} (ok={ok}, err={errored})",
                      file=sys.stderr)
            if status == "rate-limit":
                print("rate limit hit; stopping.", file=sys.stderr)
                break

        # 5. Summary
        total_topics = conn.execute("SELECT COUNT(*) FROM repo_topics").fetchone()[0]
        distinct_topics = conn.execute(
            "SELECT COUNT(DISTINCT topic) FROM repo_topics"
        ).fetchone()[0]
        print(
            f"done. fetched={fetched} ok={ok} errored={errored}. "
            f"repo_topics has {total_topics} rows across {distinct_topics} distinct topics.",
            file=sys.stderr,
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
