#!/usr/bin/env python3
"""Sweep engaged outreach threads for maintainer replies newer than last_touch.

Read-only triage. For every outreach-ledger row with ``response: engaged``, fetch
the latest comment on its ``posted_url`` (a GitHub issue or discussion) and flag
the thread when the latest comment is BOTH:

  * newer than the row's ``last_touch``, AND
  * not by our own account (``idoco2003``).

That combination is an unhandled inbound: a maintainer replied after we last
recorded a touch, and nobody has acted on it. A month-old miss on
IMRCLab/crazyswarm2#864 (a real correction from the maintainer that sat unseen
because it landed right after our own follow-up) is what motivated this.

Notes on the two bugs that made the original ad-hoc sweep unreliable, both fixed
here:

  * ``gh issue view --json comments`` exposes the author as ``author.login``, not
    ``user.login``. The wrong key silently returned null, so every author looked
    unknown and every thread got flagged.
  * ``gh`` output must be decoded as UTF-8. Em-dashes and other non-Latin-1
    characters in comment bodies otherwise crash the Windows console codepage
    (cp1255 here) mid-read and drop the author.

Usage:
    python tools/scripts/sweep_engaged_inbound.py

Requires the ``gh`` CLI, authenticated. Nothing is posted or written; the script
only prints a report and always exits 0. Feed the flagged threads back into the
normal loop (read, classify, reply/build, update the ledger).
"""

from __future__ import annotations

import glob
import json
import re
import subprocess
from pathlib import Path

import yaml

OUR_LOGIN = "idoco2003"
_URL_RE = re.compile(r"github\.com/(?:orgs/)?([^/]+)/([^/]+)/(issues|discussions)/(\d+)")


def _gh(args: list[str]) -> str:
    """Run gh and return stdout, decoded UTF-8 with replacement (never crashes)."""
    try:
        r = subprocess.run(
            ["gh", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=40
        )
        return r.stdout
    except Exception:
        return ""


def _latest_comment(url: str) -> tuple[str, str] | None:
    """Return (author_login, created_date) of the latest comment, or None."""
    m = _URL_RE.search(url or "")
    if not m:
        return None
    owner, repo, kind, num = m.groups()
    if kind == "issues":
        out = _gh(["issue", "view", num, "-R", f"{owner}/{repo}", "--json", "comments"])
        try:
            cs = (json.loads(out) or {}).get("comments") or []
        except json.JSONDecodeError:
            return None
        if not cs:
            return None
        last = cs[-1]
        who = ((last.get("author") or {}).get("login")) or ""
        return who, (last.get("createdAt") or "")[:10]
    # discussion
    q = (
        f'{{repository(owner:"{owner}",name:"{repo}"){{discussion(number:{num})'
        f"{{comments(last:1){{nodes{{author{{login}} createdAt}}}}}}}}}}"
    )
    out = _gh(["api", "graphql", "-f", "query=" + q])
    try:
        nodes = json.loads(out)["data"]["repository"]["discussion"]["comments"]["nodes"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    if not nodes:
        return None
    n = nodes[0]
    who = ((n.get("author") or {}).get("login")) or ""
    return who, (n.get("createdAt") or "")[:10]


def _engaged_rows() -> list[dict]:
    rows: list[dict] = []
    here = Path(__file__).resolve().parents[2]
    for f in glob.glob(str(here / "examples" / "lighthouses" / "outreach*.yaml")):
        try:
            d = yaml.safe_load(Path(f).read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        items = d if isinstance(d, list) else (d.get("targets") if isinstance(d, dict) else None)
        if not isinstance(items, list):
            continue
        for r in items:
            if isinstance(r, dict) and r.get("response") == "engaged" and r.get("posted_url"):
                rows.append(r)
    return rows


def main() -> None:
    rows = _engaged_rows()
    flagged: list[tuple[str, str, str, str, str]] = []
    for r in rows:
        slug = str(r.get("slug"))
        lt = str(r.get("last_touch") or "")
        url = str(r.get("posted_url"))
        res = _latest_comment(url)
        if not res:
            continue
        who, when = res
        # Unhandled inbound: a newer comment, by someone other than us.
        if when and lt and when > lt and who and who != OUR_LOGIN:
            flagged.append((slug, lt, when, who, url))

    print(f"Swept {len(rows)} engaged threads.\n")
    if not flagged:
        print("No unhandled inbound: every engaged thread's newest comment is ours or already recorded.")
        return
    print(f"UNHANDLED INBOUND ({len(flagged)}): a maintainer replied after our last_touch.\n")
    for slug, lt, when, who, url in sorted(flagged, key=lambda x: x[2], reverse=True):
        print(f"  {slug:<24} last_touch={lt}  new={when} by @{who}")
        print(f"    {url}")


if __name__ == "__main__":
    main()
