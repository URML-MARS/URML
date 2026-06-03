"""Read-only data layer over `tools/outreach.db`.

Every query function takes an optional `Filters` dataclass and returns
plain Python (lists of dicts, ints) so the UI layer stays simple. No
synthetic / mock rows: every value comes from the SQLite mirror, which
was built from the real YAML ledgers by
`tools/scripts/refresh_outreach_db.py`.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = REPO_ROOT / "tools" / "outreach.db"


@dataclass
class Filters:
    sectors: list[str] = field(default_factory=list)
    tiers: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)
    waves: list[str] = field(default_factory=list)
    search: str = ""

    def is_empty(self) -> bool:
        return not (
            self.sectors or self.tiers or self.countries
            or self.responses or self.waves or self.search
        )

    def where_clause(self, alias: str = "t") -> tuple[str, list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if self.sectors:
            placeholders = ",".join("?" * len(self.sectors))
            clauses.append(f"{alias}.sector IN ({placeholders})")
            params.extend(self.sectors)
        if self.tiers:
            placeholders = ",".join("?" * len(self.tiers))
            clauses.append(f"{alias}.tier IN ({placeholders})")
            params.extend(self.tiers)
        if self.countries:
            placeholders = ",".join("?" * len(self.countries))
            clauses.append(f"{alias}.country IN ({placeholders})")
            params.extend(self.countries)
        if self.responses:
            placeholders = ",".join("?" * len(self.responses))
            clauses.append(f"{alias}.response IN ({placeholders})")
            params.extend(self.responses)
        if self.waves:
            placeholders = ",".join("?" * len(self.waves))
            clauses.append(f"{alias}.wave IN ({placeholders})")
            params.extend(self.waves)
        if self.search:
            clauses.append(
                f"({alias}.slug LIKE ? OR {alias}.contact LIKE ? "
                f"OR {alias}.notes LIKE ? OR {alias}.next_action LIKE ?)"
            )
            needle = f"%{self.search}%"
            params.extend([needle, needle, needle, needle])
        sql = " WHERE " + " AND ".join(clauses) if clauses else ""
        return sql, params


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. Run `python tools/scripts/refresh_outreach_db.py` "
            f"to build the SQLite mirror from the YAML ledgers."
        )
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def top_line_numbers(db_path: Path | None = None) -> dict[str, int]:
    """Return the five KPI counts plus pending_directives."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT
                (SELECT COUNT(*) FROM targets)                                    AS total,
                (SELECT COUNT(*) FROM targets WHERE sent_at != '')                AS posted,
                (SELECT COUNT(*) FROM targets WHERE response = 'engaged')         AS engaged,
                (SELECT COUNT(*) FROM targets WHERE response IN ('wontfix','declined')) AS blockers,
                (SELECT COUNT(*) FROM targets WHERE is_stale = 1)                 AS stale,
                (SELECT COUNT(*) FROM claude_directives WHERE status = 'pending') AS pending_directives
            """
        )
        row = cur.fetchone()
    return {k: row[k] for k in row.keys()}


def funnel_stage_counts(db_path: Path | None = None) -> dict[str, int]:
    """Return the five conversion-funnel stages.

    Stages are mutually exclusive and sum to `total`:
      queued  = row has not been sent_at-set (sent_at == '')
      posted  = sent, no maintainer reply (response == 'none')
      acked   = response == 'acked'
      engaged = response == 'engaged'
      closed  = response in ('wontfix', 'declined')

    The conversion funnel chart on the Overview page reads from this
    helper; the KPI row also derives Posted / Engaged / Blockers from
    here so the two cannot drift.
    """
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT
                (SELECT COUNT(*) FROM targets)                                  AS total,
                (SELECT COUNT(*) FROM targets WHERE sent_at = '' OR sent_at IS NULL) AS queued,
                (SELECT COUNT(*) FROM targets WHERE sent_at != '' AND response = 'none')   AS posted,
                (SELECT COUNT(*) FROM targets WHERE response = 'acked')         AS acked,
                (SELECT COUNT(*) FROM targets WHERE response = 'engaged')       AS engaged,
                (SELECT COUNT(*) FROM targets WHERE response IN ('wontfix','declined')) AS closed
            """
        )
        row = cur.fetchone()
    return {k: row[k] for k in row.keys()}


def sector_distribution(filters: Filters | None = None, db_path: Path | None = None) -> list[dict]:
    """One row per sector with response breakdown.

    NULL / empty sectors are skipped: a value of `None` in the column
    means the migration has not run yet for that row, not "unclassified",
    so we suppress the bogus group rather than render a "null" bar.
    """
    filters = filters or Filters()
    where, params = filters.where_clause("targets")
    base_filter = "sector IS NOT NULL AND sector != ''"
    where_combined = (
        f"{where} AND {base_filter}" if where
        else f" WHERE {base_filter}"
    )
    with _connect(db_path) as conn:
        cur = conn.execute(
            f"""SELECT
                sector,
                COUNT(*) AS total,
                SUM(CASE WHEN sent_at != '' THEN 1 ELSE 0 END) AS posted,
                SUM(CASE WHEN response = 'engaged' THEN 1 ELSE 0 END) AS engaged,
                SUM(CASE WHEN response = 'wontfix' THEN 1 ELSE 0 END) AS wontfix,
                SUM(CASE WHEN response = 'declined' THEN 1 ELSE 0 END) AS declined,
                SUM(CASE WHEN response IN ('wontfix','declined') THEN 1 ELSE 0 END) AS blockers,
                SUM(CASE WHEN is_stale = 1 THEN 1 ELSE 0 END) AS stale
                FROM targets{where_combined}
                GROUP BY sector
                ORDER BY total DESC""",
            params,
        )
        return [dict(r) for r in cur.fetchall()]


def funnel_by_wave(db_path: Path | None = None) -> list[dict]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT move_num, total, posted, engaged, wontfix, declined, stale
               FROM waves
               ORDER BY move_num"""
        )
        return [dict(r) for r in cur.fetchall()]


def list_targets(
    filters: Filters | None = None,
    limit: int | None = None,
    db_path: Path | None = None,
) -> list[dict]:
    filters = filters or Filters()
    where, params = filters.where_clause("t")
    limit_clause = f" LIMIT {int(limit)}" if limit else ""
    with _connect(db_path) as conn:
        cur = conn.execute(
            f"""SELECT t.wave, t.slug, t.rfc, t.sector, t.country, t.tier,
                       t.response, t.sent_at, t.last_touch, t.posted_url,
                       t.contact, t.notes, t.next_action, t.is_stale,
                       t.comment_count, t.pending_directive_count,
                       t.move_num
                FROM targets t{where}
                ORDER BY COALESCE(t.last_touch, t.sent_at) DESC, t.slug ASC
                {limit_clause}""",
            params,
        )
        return [dict(r) for r in cur.fetchall()]


def kanban_columns(filters: Filters | None = None, db_path: Path | None = None) -> dict[str, list[dict]]:
    """Return rows split into the five kanban columns. Order preserved."""
    rows = list_targets(filters=filters, db_path=db_path)
    cols: dict[str, list[dict]] = {
        "Queued": [],
        "Posted": [],
        "Acked": [],
        "Engaged": [],
        "Closed": [],
    }
    for r in rows:
        sent = r["sent_at"] or ""
        resp = r["response"] or "none"
        if not sent:
            cols["Queued"].append(r)
        elif resp == "engaged":
            cols["Engaged"].append(r)
        elif resp == "acked":
            cols["Acked"].append(r)
        elif resp in ("wontfix", "declined"):
            cols["Closed"].append(r)
        else:  # response = 'none', sent_at set
            cols["Posted"].append(r)
    return cols


def get_target(wave: str, slug: str, db_path: Path | None = None) -> dict | None:
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT * FROM targets WHERE wave = ? AND slug = ?""",
            (wave, slug),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def list_comments(wave: str, slug: str, db_path: Path | None = None) -> list[dict]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT seq, date, text FROM comments
               WHERE wave = ? AND slug = ?
               ORDER BY date DESC, seq DESC""",
            (wave, slug),
        )
        return [dict(r) for r in cur.fetchall()]


def list_directives(
    wave: str,
    slug: str,
    db_path: Path | None = None,
) -> list[dict]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT seq, date, text, status FROM claude_directives
               WHERE wave = ? AND slug = ?
               ORDER BY date DESC, seq DESC""",
            (wave, slug),
        )
        return [dict(r) for r in cur.fetchall()]


def pending_directives_all(db_path: Path | None = None) -> list[dict]:
    """Every pending directive across every row, oldest first."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT d.wave, d.slug, d.seq, d.date, d.text, t.sector, t.response, t.rfc
               FROM claude_directives d
               JOIN targets t ON t.wave = d.wave AND t.slug = d.slug
               WHERE d.status = 'pending'
               ORDER BY d.date ASC"""
        )
        return [dict(r) for r in cur.fetchall()]


def history_directives_all(db_path: Path | None = None) -> list[dict]:
    """Every done / skip directive across every row, most recent first."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """SELECT d.wave, d.slug, d.seq, d.date, d.text, d.status,
                      t.sector, t.response, t.rfc
               FROM claude_directives d
               JOIN targets t ON t.wave = d.wave AND t.slug = d.slug
               WHERE d.status IN ('done', 'skip')
               ORDER BY d.date DESC, d.seq DESC"""
        )
        return [dict(r) for r in cur.fetchall()]


def recent_comments(days: int = 14, db_path: Path | None = None) -> list[dict]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            f"""SELECT c.wave, c.slug, c.date, c.text, t.sector, t.response
               FROM comments c
               JOIN targets t ON t.wave = c.wave AND t.slug = c.slug
               WHERE c.date >= date('now', '-{int(days)} day')
               ORDER BY c.date DESC, c.seq DESC"""
        )
        return [dict(r) for r in cur.fetchall()]


def distinct_values() -> dict[str, list[str]]:
    """For the sidebar filter chips."""
    with _connect() as conn:
        sectors = [r[0] for r in conn.execute("SELECT DISTINCT sector FROM targets WHERE sector IS NOT NULL ORDER BY sector")]
        tiers = [r[0] for r in conn.execute("SELECT DISTINCT tier FROM targets WHERE tier IS NOT NULL ORDER BY tier")]
        countries = [r[0] for r in conn.execute("SELECT DISTINCT country FROM targets WHERE country IS NOT NULL ORDER BY country")]
        responses = ["none", "acked", "engaged", "wontfix", "declined"]
        waves = [r[0] for r in conn.execute("SELECT DISTINCT wave FROM targets ORDER BY move_num")]
    return {
        "sectors": sectors,
        "tiers": tiers,
        "countries": countries,
        "responses": responses,
        "waves": waves,
    }
