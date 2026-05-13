"""Collect community metrics for the URML repository.

Pulls forks/stars/traffic/issue/PR/RFC numbers from the GitHub REST API and
produces two outputs:

- `metrics-YYYY-MM-full.json`  — the full data dump (private; uploaded as a
                                  workflow artifact, never committed).
- `metrics-YYYY-MM.md`         — a curated Markdown draft (public; opened as
                                  a PR for the maintainer to edit + merge).

Uses `gh api` as the HTTP transport so authentication is handled by either the
workflow's `GITHUB_TOKEN` (in CI) or the maintainer's `gh auth login` (locally).
No third-party Python dependencies.

Usage:
    python .github/scripts/collect_metrics.py \
        --repo URML-MARS/URML \
        --month 2026-05 \
        --output-dir docs/community

    # Default month is the previous calendar month (UTC).
    # Pass --dry-run to print the JSON to stdout instead of writing files.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


def gh_api(path: str, *, paginate: bool = False) -> Any:
    """Call `gh api <path>` and return the parsed JSON.

    With paginate=True, concatenates pages into a single list.
    """
    cmd = ["gh", "api", path]
    if paginate:
        cmd.append("--paginate")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"gh api {path} failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    if not paginate:
        return json.loads(result.stdout)
    # --paginate emits multiple JSON arrays separated by newlines when the
    # endpoint returns arrays; concatenate them.
    out: list[Any] = []
    decoder = json.JSONDecoder()
    text = result.stdout.strip()
    idx = 0
    while idx < len(text):
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text):
            break
        value, end = decoder.raw_decode(text, idx)
        if isinstance(value, list):
            out.extend(value)
        else:
            out.append(value)
        idx = end
    return out


@dataclass
class Period:
    """The reporting window: an inclusive calendar month in UTC."""

    year: int
    month: int

    @property
    def start(self) -> datetime:
        return datetime(self.year, self.month, 1, tzinfo=timezone.utc)

    @property
    def end(self) -> datetime:
        if self.month == 12:
            return datetime(self.year + 1, 1, 1, tzinfo=timezone.utc)
        return datetime(self.year, self.month + 1, 1, tzinfo=timezone.utc)

    @property
    def label(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"

    @classmethod
    def previous_month(cls) -> "Period":
        now = datetime.now(timezone.utc)
        first_of_this_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        last_month_end = first_of_this_month - timedelta(days=1)
        return cls(last_month_end.year, last_month_end.month)

    @classmethod
    def parse(cls, s: str) -> "Period":
        y, m = s.split("-")
        return cls(int(y), int(m))


@dataclass
class Metrics:
    repo: str
    period: str
    repo_stats: dict[str, int] = field(default_factory=dict)
    traffic: dict[str, Any] = field(default_factory=dict)
    issues: dict[str, Any] = field(default_factory=dict)
    pulls: dict[str, Any] = field(default_factory=dict)
    new_contributors: list[str] = field(default_factory=list)
    rfc_activity: dict[str, Any] = field(default_factory=dict)


def collect_repo_stats(repo: str) -> dict[str, int]:
    data = gh_api(f"/repos/{repo}")
    return {
        "stars": int(data["stargazers_count"]),
        "forks": int(data["forks_count"]),
        "watchers": int(data["subscribers_count"]),
        "open_issues": int(data["open_issues_count"]),
        "network_size": int(data.get("network_count", 0)),
    }


def collect_traffic(repo: str) -> dict[str, Any]:
    """Traffic API returns rolling 14-day windows — not month-aligned.

    The numbers are reported as-of-now, not for the period. We label them
    accordingly in the output.
    """
    clones = gh_api(f"/repos/{repo}/traffic/clones")
    views = gh_api(f"/repos/{repo}/traffic/views")
    referrers = gh_api(f"/repos/{repo}/traffic/popular/referrers")
    paths = gh_api(f"/repos/{repo}/traffic/popular/paths")
    return {
        "window_days": 14,
        "clones": {"count": clones["count"], "uniques": clones["uniques"]},
        "views": {"count": views["count"], "uniques": views["uniques"]},
        "top_referrers": referrers[:10],
        "top_paths": paths[:10],
    }


def _is_bot(login: str | None) -> bool:
    if not login:
        return True
    return login.endswith("[bot]") or login in {"github-actions", "dependabot"}


def _first_response_hours(
    repo: str, item_number: int, author_login: str | None, created_at: datetime
) -> float | None:
    """Return hours from item creation to first non-author, non-bot comment.

    Returns None if no qualifying comment exists.
    """
    comments = gh_api(
        f"/repos/{repo}/issues/{item_number}/comments?per_page=100", paginate=True
    )
    for c in comments:
        login = (c.get("user") or {}).get("login")
        if login == author_login or _is_bot(login):
            continue
        ts = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
        return (ts - created_at).total_seconds() / 3600.0
    return None


def _collect_items(repo: str, period: Period, *, kind: str) -> dict[str, Any]:
    """Collect issues OR pull requests opened in the period.

    GitHub returns PRs through the issues endpoint too; filter by the
    `pull_request` field.
    """
    want_pr = kind == "pulls"
    # Fetch generously then filter — the issues search API is rate-limited
    # more aggressively than the list endpoint, and Phase 0 volume is low
    # enough that a per_page=100 walk is cheap.
    raw = gh_api(
        f"/repos/{repo}/issues?state=all&since={period.start.isoformat()}"
        f"&per_page=100",
        paginate=True,
    )
    opened, closed_in_period, response_hours = 0, 0, []
    merged = 0
    for item in raw:
        is_pr = "pull_request" in item
        if want_pr != is_pr:
            continue
        created = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        if period.start <= created < period.end:
            opened += 1
            hrs = _first_response_hours(
                repo,
                item["number"],
                (item.get("user") or {}).get("login"),
                created,
            )
            if hrs is not None:
                response_hours.append(hrs)
        if item.get("closed_at"):
            closed = datetime.fromisoformat(item["closed_at"].replace("Z", "+00:00"))
            if period.start <= closed < period.end:
                closed_in_period += 1
                if is_pr and item["pull_request"].get("merged_at"):
                    merged += 1

    median_hrs = statistics.median(response_hours) if response_hours else None
    return {
        "opened": opened,
        "closed": closed_in_period,
        **({"merged": merged} if want_pr else {}),
        "first_response_hours_p50": median_hrs,
        "first_response_count": len(response_hours),
    }


def collect_issues(repo: str, period: Period) -> dict[str, Any]:
    return _collect_items(repo, period, kind="issues")


def collect_pulls(repo: str, period: Period) -> dict[str, Any]:
    return _collect_items(repo, period, kind="pulls")


def collect_new_contributors(repo: str, period: Period) -> list[str]:
    """Logins of contributors whose first commit lands in the period.

    Uses /repos/{repo}/commits with `since` and `until` to bound the search;
    cross-references against contributors before the period.
    """
    commits = gh_api(
        f"/repos/{repo}/commits?since={period.start.isoformat()}"
        f"&until={period.end.isoformat()}&per_page=100",
        paginate=True,
    )
    seen_in_period: set[str] = set()
    for c in commits:
        author = (c.get("author") or {}).get("login")
        if author and not _is_bot(author):
            seen_in_period.add(author)

    if not seen_in_period:
        return []

    before = gh_api(
        f"/repos/{repo}/commits?until={period.start.isoformat()}&per_page=100",
        paginate=True,
    )
    seen_before: set[str] = set()
    for c in before:
        author = (c.get("author") or {}).get("login")
        if author:
            seen_before.add(author)

    return sorted(seen_in_period - seen_before)


def collect_rfc_activity(repo: str, period: Period) -> dict[str, Any]:
    """Count commits in the period that touch docs/rfcs/."""
    commits = gh_api(
        f"/repos/{repo}/commits?path=docs/rfcs&since={period.start.isoformat()}"
        f"&until={period.end.isoformat()}&per_page=100",
        paginate=True,
    )
    return {
        "commits_touching_rfcs": len(commits),
        "commit_subjects": [
            c["commit"]["message"].split("\n", 1)[0] for c in commits
        ][:10],
    }


def collect_all(repo: str, period: Period) -> Metrics:
    return Metrics(
        repo=repo,
        period=period.label,
        repo_stats=collect_repo_stats(repo),
        traffic=collect_traffic(repo),
        issues=collect_issues(repo, period),
        pulls=collect_pulls(repo, period),
        new_contributors=collect_new_contributors(repo, period),
        rfc_activity=collect_rfc_activity(repo, period),
    )


def _fmt_hours(h: float | None) -> str:
    if h is None:
        return "—"
    if h < 24:
        return f"{h:.1f} h"
    return f"{h / 24:.1f} d"


def render_markdown(m: Metrics) -> str:
    lines: list[str] = []
    lines.append(f"# URML community metrics — {m.period}")
    lines.append("")
    lines.append(
        "_Auto-generated by `.github/scripts/collect_metrics.py`. "
        "The maintainer edits this draft before merging — narrative and "
        "context belong here, not in the raw numbers._"
    )
    lines.append("")

    lines.append("## Headline")
    lines.append("")
    s = m.repo_stats
    lines.append(
        f"- **Stars:** {s['stars']} · **Forks:** {s['forks']} · "
        f"**Watchers:** {s['watchers']}"
    )
    lines.append(f"- **Open issues / PRs:** {s['open_issues']}")
    lines.append("")

    lines.append(f"## Traffic (last {m.traffic['window_days']} days, GitHub Insights)")
    lines.append("")
    lines.append(
        f"- **Clones:** {m.traffic['clones']['count']} "
        f"({m.traffic['clones']['uniques']} unique)"
    )
    lines.append(
        f"- **Views:** {m.traffic['views']['count']} "
        f"({m.traffic['views']['uniques']} unique)"
    )
    if m.traffic["top_referrers"]:
        lines.append("- **Top referrers:** " + ", ".join(
            f"{r['referrer']} ({r['uniques']})" for r in m.traffic["top_referrers"][:5]
        ))
    lines.append("")

    lines.append("## Issues")
    lines.append("")
    i = m.issues
    lines.append(
        f"- Opened: **{i['opened']}** · Closed: **{i['closed']}**"
    )
    lines.append(
        f"- Median time-to-first-response: **{_fmt_hours(i['first_response_hours_p50'])}** "
        f"(n={i['first_response_count']})"
    )
    lines.append("")

    lines.append("## Pull requests")
    lines.append("")
    p = m.pulls
    lines.append(
        f"- Opened: **{p['opened']}** · Merged: **{p.get('merged', 0)}** · "
        f"Closed-without-merge: **{p['closed'] - p.get('merged', 0)}**"
    )
    lines.append(
        f"- Median time-to-first-review: **{_fmt_hours(p['first_response_hours_p50'])}** "
        f"(n={p['first_response_count']})"
    )
    lines.append("")

    lines.append("## RFC activity")
    lines.append("")
    r = m.rfc_activity
    lines.append(f"- Commits touching `docs/rfcs/`: **{r['commits_touching_rfcs']}**")
    if r["commit_subjects"]:
        for subject in r["commit_subjects"]:
            lines.append(f"  - {subject}")
    lines.append("")

    lines.append("## New contributors")
    lines.append("")
    if m.new_contributors:
        for login in m.new_contributors:
            lines.append(f"- @{login}")
    else:
        lines.append("_None this period._")
    lines.append("")

    lines.append("## Narrative")
    lines.append("")
    lines.append("_Maintainer fills in: what happened this month? Any RFCs opened/closed? "
                 "Notable conversations? Asks for the community?_")
    lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repo, e.g. URML-MARS/URML")
    parser.add_argument(
        "--month",
        help="Reporting month as YYYY-MM (default: previous calendar month, UTC)",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/community",
        help="Directory for the rendered Markdown output (default: docs/community)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print outputs to stdout instead of writing files.",
    )
    args = parser.parse_args(argv)

    period = Period.parse(args.month) if args.month else Period.previous_month()
    metrics = collect_all(args.repo, period)
    full_json = json.dumps(metrics.__dict__, indent=2, sort_keys=True)
    md = render_markdown(metrics)

    if args.dry_run:
        print("=== JSON ===")
        print(full_json)
        print("\n=== MARKDOWN ===")
        print(md)
        return 0

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    full_path = out_dir / f"metrics-{period.label}-full.json"
    md_path = out_dir / f"metrics-{period.label}.md"
    full_path.write_text(full_json + "\n", encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    print(f"Wrote {full_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
