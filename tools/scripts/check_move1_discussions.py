#!/usr/bin/env python3
"""Check the five Move #1 GitHub Discussion threads for vendor activity.

The Move #1 outreach ledger (examples/lighthouses/outreach.yaml) has five rows
whose threads are GitHub Discussions, not Issues:

  yaskawa    Yaskawa-Global/motoros2 #495
  ur         UniversalRobots/Universal_Robots_ROS2_Driver #1799
  kuka       kroshu/kuka_drivers #342
  staubli    ros-industrial/staubli_val3_driver #57
  mitsubishi Mitsubishi-Electric-Asia/melfa_ros2_driver #25

GitHub Discussions have no REST API; they are GraphQL-only. In a cloud-hosted
scheduled session the MCP GitHub App token cannot run discussion queries and
WebFetch returns 404. This script is the fix: it queries GitHub GraphQL directly
using a personal access token supplied via the environment.

Usage:
    GITHUB_TOKEN=<pat> python tools/scripts/check_move1_discussions.py

Required PAT scopes: public_repo, read:discussion  (classic token)
or: repo (fine-grained token scoped to the target orgs)

Output: one section per slug, listing non-idoco2003 comments and reactions,
followed by a brief drift summary keyed to the ledger's response enum.
Always exits 0; errors on individual slugs are printed inline.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

OUR_LOGIN = "idoco2003"
GRAPHQL_URL = "https://api.github.com/graphql"

# Discussion coordinates for the five Move #1 slugs.
DISCUSSIONS: list[dict[str, Any]] = [
    {"slug": "yaskawa",    "owner": "Yaskawa-Global",               "repo": "motoros2",                        "number": 495},
    {"slug": "ur",         "owner": "UniversalRobots",              "repo": "Universal_Robots_ROS2_Driver",    "number": 1799},
    {"slug": "kuka",       "owner": "kroshu",                       "repo": "kuka_drivers",                    "number": 342},
    {"slug": "staubli",    "owner": "ros-industrial",               "repo": "staubli_val3_driver",             "number": 57},
    {"slug": "mitsubishi", "owner": "Mitsubishi-Electric-Asia",     "repo": "melfa_ros2_driver",               "number": 25},
]

_QUERY_TEMPLATE = """
{
  repository(owner: "%s", name: "%s") {
    discussion(number: %d) {
      title
      closed
      reactions { totalCount }
      comments(first: 100) {
        nodes {
          author { login }
          createdAt
          body
          reactions { totalCount }
          replies(first: 50) {
            nodes {
              author { login }
              createdAt
              body
            }
          }
        }
      }
    }
  }
}
"""


def _graphql(token: str, query: str) -> dict[str, Any]:
    payload = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _check_discussion(token: str, d: dict[str, Any]) -> None:
    slug = d["slug"]
    owner, repo, number = d["owner"], d["repo"], d["number"]
    url = f"https://github.com/{owner}/{repo}/discussions/{number}"
    print(f"\n{'='*60}")
    print(f"slug: {slug}  —  {url}")

    query = _QUERY_TEMPLATE % (owner, repo, number)
    try:
        result = _graphql(token, query)
    except urllib.error.HTTPError as e:
        print(f"  ERROR: HTTP {e.code} from GitHub GraphQL — {e.reason}")
        return
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    errors = result.get("errors")
    if errors:
        print(f"  ERROR: GraphQL errors: {errors}")
        return

    disc = (result.get("data") or {}).get("repository", {}).get("discussion")
    if not disc:
        print("  ERROR: discussion not found (private or deleted)")
        return

    state = "closed" if disc.get("closed") else "open"
    total_reactions = (disc.get("reactions") or {}).get("totalCount", 0)
    print(f"  state: {state}  |  discussion-level reactions: {total_reactions}")

    # Collect all non-us comments (top-level + replies).
    vendor_comments: list[dict[str, Any]] = []
    for c in (disc.get("comments") or {}).get("nodes") or []:
        login = ((c.get("author") or {}).get("login") or "").lower()
        if login and login != OUR_LOGIN:
            vendor_comments.append({
                "login": login,
                "date": (c.get("createdAt") or "")[:10],
                "body": (c.get("body") or "")[:240],
                "reactions": (c.get("reactions") or {}).get("totalCount", 0),
            })
        for r in (c.get("replies") or {}).get("nodes") or []:
            rlogin = ((r.get("author") or {}).get("login") or "").lower()
            if rlogin and rlogin != OUR_LOGIN:
                vendor_comments.append({
                    "login": rlogin,
                    "date": (r.get("createdAt") or "")[:10],
                    "body": (r.get("body") or "")[:240],
                    "reactions": 0,
                })

    if not vendor_comments and total_reactions == 0:
        print("  No vendor activity detected.")
        return

    print(f"  Vendor comments ({len(vendor_comments)}):")
    for vc in vendor_comments:
        print(f"    [{vc['date']}] @{vc['login']}  reactions={vc['reactions']}")
        print(f"      {vc['body']!r}")

    # Drift hint (conservative — caller decides what to write to the ledger).
    if vendor_comments:
        most_recent = max(vendor_comments, key=lambda x: x["date"])
        body_len = len(most_recent["body"])
        hint = "engaged" if body_len > 120 else "acked"
        print(f"  DRIFT HINT: response -> {hint}  (most recent: {most_recent['date']} by @{most_recent['login']})")
    elif total_reactions > 0:
        print(f"  DRIFT HINT: response -> acked  (reactions only, no comments)")


SNAPSHOT_BRANCH = "meta/move1-discussions-snapshot"
SNAPSHOT_FILE = ".move1-discussions-snapshot/discussions.json"


def _load_from_snapshot() -> dict[str, Any] | None:
    """Fetch the snapshot branch and return parsed discussions.json, or None on failure.

    The GitHub Actions workflow move1-discussions-snapshot.yml pushes a daily
    snapshot to SNAPSHOT_BRANCH. Cloud-hosted sessions cannot reach the GitHub
    API directly (the proxy blocks it), but git transport works, so we fetch
    the branch and read the JSON from the worktree.
    """
    repo_root = Path(__file__).resolve().parents[2]
    try:
        subprocess.run(
            ["git", "fetch", "origin", SNAPSHOT_BRANCH],
            check=True,
            capture_output=True,
            cwd=repo_root,
        )
        blob = subprocess.run(
            ["git", "show", f"FETCH_HEAD:{SNAPSHOT_FILE}"],
            check=True,
            capture_output=True,
            cwd=repo_root,
        ).stdout
        return json.loads(blob)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError):
        return None


def _check_discussion_from_snapshot(slug: str, data: dict[str, Any]) -> None:
    disc = data.get("discussion")
    url = next(
        (f"https://github.com/{d['owner']}/{d['repo']}/discussions/{d['number']}"
         for d in DISCUSSIONS if d["slug"] == slug),
        slug,
    )
    print(f"\n{'='*60}")
    print(f"slug: {slug}  —  {url}  [from snapshot]")
    if not disc:
        print("  ERROR: discussion not found in snapshot")
        return

    state = "closed" if disc.get("closed") else "open"
    total_reactions = (disc.get("reactions") or {}).get("totalCount", 0)
    print(f"  state: {state}  |  discussion-level reactions: {total_reactions}")

    vendor_comments: list[dict[str, Any]] = []
    for c in (disc.get("comments") or {}).get("nodes") or []:
        login = ((c.get("author") or {}).get("login") or "").lower()
        if login and login != OUR_LOGIN:
            vendor_comments.append({
                "login": login,
                "date": (c.get("createdAt") or "")[:10],
                "body": (c.get("body") or "")[:240],
                "reactions": (c.get("reactions") or {}).get("totalCount", 0),
            })
        for r in (c.get("replies") or {}).get("nodes") or []:
            rlogin = ((r.get("author") or {}).get("login") or "").lower()
            if rlogin and rlogin != OUR_LOGIN:
                vendor_comments.append({
                    "login": rlogin,
                    "date": (r.get("createdAt") or "")[:10],
                    "body": (r.get("body") or "")[:240],
                    "reactions": 0,
                })

    if not vendor_comments and total_reactions == 0:
        print("  No vendor activity detected.")
        return

    print(f"  Vendor comments ({len(vendor_comments)}):")
    for vc in vendor_comments:
        print(f"    [{vc['date']}] @{vc['login']}  reactions={vc['reactions']}")
        print(f"      {vc['body']!r}")

    if vendor_comments:
        most_recent = max(vendor_comments, key=lambda x: x["date"])
        body_len = len(most_recent["body"])
        hint = "engaged" if body_len > 120 else "acked"
        print(f"  DRIFT HINT: response -> {hint}  (most recent: {most_recent['date']} by @{most_recent['login']})")
    elif total_reactions > 0:
        print(f"  DRIFT HINT: response -> acked  (reactions only, no comments)")


def main() -> None:
    print("Move #1 Discussion drift check")

    # Prefer the snapshot branch: no PAT needed, works in cloud sessions where
    # the proxy blocks direct GitHub API access. Falls back to direct GraphQL
    # when a PAT is available (useful for local runs or fresh data).
    snapshot = _load_from_snapshot()
    if snapshot:
        data = (snapshot.get("data") or snapshot)
        print(f"Checking {len(DISCUSSIONS)} discussion threads from snapshot branch {SNAPSHOT_BRANCH!r}.")
        for d in DISCUSSIONS:
            slug_data = data.get(d["slug"]) or {}
            _check_discussion_from_snapshot(d["slug"], slug_data)
        print(f"\n{'='*60}")
        print("Done. Update examples/lighthouses/outreach.yaml manually for any drift rows above.")
        return

    # No snapshot available — fall back to direct GraphQL (requires PAT).
    # Prefer GITHUB_PAT over GITHUB_TOKEN; the App token in cloud sessions
    # lacks the read:discussion scope and will return 403.
    token = os.environ.get("GITHUB_PAT") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print(
            "ERROR: snapshot branch not available and no GITHUB_PAT set.\n"
            "  Option A: set GITHUB_PAT to a classic PAT with public_repo + read:discussion scopes.\n"
            "  Option B: wait for the move1-discussions-snapshot.yml Actions workflow to run once.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Snapshot branch not available; querying {len(DISCUSSIONS)} threads via GitHub GraphQL.")

    for d in DISCUSSIONS:
        _check_discussion(token, d)

    print(f"\n{'='*60}")
    print("Done. Update examples/lighthouses/outreach.yaml manually for any drift rows above.")


if __name__ == "__main__":
    main()
