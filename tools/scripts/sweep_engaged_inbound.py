#!/usr/bin/env python3
"""Sweep outreach threads for maintainer replies newer than last_touch.

Read-only triage. For every NON-TERMINAL outreach-ledger row (``response`` in
none / acked / engaged) fetch the latest comment on its ``posted_url`` (a GitHub
issue or discussion) and flag the thread when the latest comment is BOTH:

  * newer than the row's ``last_touch``, AND
  * not by our own account (``idoco2003``).

That combination is an unhandled inbound: someone replied after we last recorded
a touch, and nobody has acted on it. A month-old miss on IMRCLab/crazyswarm2#864
(a real correction from the maintainer that sat unseen because it landed right
after our own follow-up) is what motivated this.

**Coverage matters more than it looks.** The first version swept only
``engaged`` rows, and promptly missed two real maintainer replies:
Genesis-Embodied-AI/genesis-world#2881 (row was ``none``) and
ray-project/ray#64064 (row was ``acked``). A first reply on a ``none`` or
``acked`` thread is a *brand-new engagement*, which is the highest-value signal
there is, so those states are swept too and reported first. Terminal states
(``declined`` / ``wontfix``) are settled and skipped.

Notes on the two bugs that made the original ad-hoc sweep unreliable, both fixed:

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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

OUR_LOGIN = "idoco2003"
# Settled states we do not re-check; everything else is worth a look.
_NON_TERMINAL = {"none", "acked", "engaged"}
# Bots are not inbound. A stale-bot notice or an auto-close is dormancy, not a
# maintainer reply, and flagging them buries the real ones.
_BOT_LOGINS = {"github-actions", "dependabot", "codecov", "stale", "renovate"}


def _is_bot(login: str) -> bool:
    low = login.lower()
    return low.endswith("[bot]") or low.removesuffix("[bot]") in _BOT_LOGINS
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


def _target_rows() -> list[dict]:
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
            # Every NON-TERMINAL row, not just `engaged`. A first reply on a `none`
            # or `acked` thread is a brand-new engagement and the highest-value
            # signal there is; sweeping only `engaged` missed exactly that twice
            # (Genesis #2881 was `none`, ray/RLlib #64064 was `acked`, and both got
            # real maintainer replies this sweep never flagged). Terminal states
            # (declined / wontfix) are settled and deliberately skipped.
            if not isinstance(r, dict) or not r.get("posted_url"):
                continue
            if r.get("response") in _NON_TERMINAL:
                rows.append(r)
    return rows


def _check(r: dict) -> tuple[str, str, str, str, str, str] | None:
    """Return (state, slug, last_touch, when, who, url) when a thread has unhandled inbound."""
    slug = str(r.get("slug"))
    lt = str(r.get("last_touch") or "")
    url = str(r.get("posted_url"))
    state = str(r.get("response") or "")
    res = _latest_comment(url)
    if not res:
        return None
    who, when = res
    # Unhandled inbound: a newer comment, by a human other than us.
    if when and lt and when > lt and who and who != OUR_LOGIN and not _is_bot(who):
        return (state, slug, lt, when, who, url)
    return None


def main() -> None:
    rows = _target_rows()
    flagged: list[tuple[str, str, str, str, str, str]] = []
    # Concurrency: the non-terminal set is large (hundreds of rows), so serial gh
    # calls would take many minutes. These are read-only fetches; 8 at a time.
    with ThreadPoolExecutor(max_workers=8) as pool:
        for res in pool.map(_check, rows):
            if res:
                flagged.append(res)

    print(f"Swept {len(rows)} non-terminal threads (none / acked / engaged).\n")
    if not flagged:
        print("No unhandled inbound: every thread's newest comment is ours or already recorded.")
        return

    # A reply on a `none` / `acked` row is a NEW engagement: surface it first.
    order = {"none": 0, "acked": 1, "engaged": 2}
    flagged.sort(key=lambda x: (order.get(x[0], 9), x[3]), reverse=False)
    print(f"UNHANDLED INBOUND ({len(flagged)}): someone replied after our last_touch.\n")
    for state, slug, lt, when, who, url in flagged:
        tag = "NEW ENGAGEMENT" if state in ("none", "acked") else "engaged thread"
        print(f"  [{state:<8}] {slug:<24} last_touch={lt}  new={when} by @{who}   <- {tag}")
        print(f"    {url}")


if __name__ == "__main__":
    main()
