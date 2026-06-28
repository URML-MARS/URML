#!/usr/bin/env python3
"""Register and post the URML agent on Moltbook (RFC-0640, Move #62).

Operational glue, deliberately kept OUT of ``reference/``: Moltbook is a cloud
service, and ``CLAUDE.md`` prohibits cloud dependencies in the reference
runtimes. Nothing here is imported by the bridge, the validator, or any runtime;
this is a thin, standalone client.

The request shapes below match Moltbook's official agent skill document
(https://www.moltbook.com/skill.md), verified 2026-06-28. The agent API is
self-serve: registration returns an api_key plus a claim_url for the one-time
human (X-tweet) verification. The "Apply for Early Access" developer program is
a separate thing (third-party *app* identity verification) and is not needed to
post.

Posture:

  * **Dry-run by default for posting.** ``post`` without ``--post`` prints the
    resolved body and exits 0; it never touches the network unless you pass
    ``--post`` AND ``MOLTBOOK_API_KEY`` is set.
  * **Credentials come from the environment, never the repo:**
      - ``MOLTBOOK_API_KEY``  -- the agent's key (``moltbook_...``), from
                                 ``register``. Required only to actually post.
  * **Standard library only.** HTTP uses ``urllib``; no third-party dependency.
  * **Key hygiene.** The API base is pinned to ``https://www.moltbook.com``;
    the key is only ever sent there, per Moltbook's security rule.

Flow:
  1. ``python post_to_moltbook.py register --name URML --description "..."``
     -> prints api_key + claim_url. Save the key; open claim_url and post the
     X claim tweet to verify the agent (founder identity).
  2. ``export MOLTBOOK_API_KEY=moltbook_...``
  3. ``python post_to_moltbook.py post --post --submolt robotics``

This script does not edit the ledger. After a real post lands, update
``examples/lighthouses/outreach-move62.yaml`` (set ``sent_at`` / ``posted_url``
/ ``last_touch``, add a posted comment, flip the directive to ``done``) and
refresh ``tools/outreach.db`` by hand, per the standing ledger discipline.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://www.moltbook.com/api/v1"  # pinned; the key is sent only here
DEFAULT_POST = Path(__file__).resolve().parent / "posts" / "demo-intro.md"

# Moltbook post limits, from the official skill doc (verified 2026-06-28).
TITLE_MAX = 300
CONTENT_MAX = 40_000


def _parse_post(path: Path) -> tuple[str, str]:
    """Split a draft body file into (title, content).

    Convention (see ``posts/demo-intro.md``): a ``# Title`` section then a
    ``# Body`` section. HTML comments at the top are ignored.
    """
    text = path.read_text(encoding="utf-8")
    title, body, bucket = "", [], None
    for line in text.splitlines():
        if line.strip() == "# Title":
            bucket = "title"
            continue
        if line.strip() == "# Body":
            bucket = "body"
            continue
        if line.lstrip().startswith("<!--") or line.lstrip().startswith("-->"):
            continue
        if bucket == "title" and line.strip():
            title = line.strip()
        elif bucket == "body":
            body.append(line)
    return title, "\n".join(body).strip()


def _request(method: str, path: str, payload: dict, api_key: str | None) -> dict:
    """Issue a JSON request to the pinned Moltbook API base. Returns parsed JSON."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method=method,
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - https base pinned above
        return json.loads(resp.read().decode("utf-8"))


def cmd_register(args: argparse.Namespace) -> int:
    """POST /agents/register -> api_key + claim_url + verification code."""
    try:
        data = _request(
            "POST",
            "/agents/register",
            {"name": args.name, "description": args.description},
            api_key=None,
        )
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Registration failed: {exc}", file=sys.stderr)
        return 1
    api_key = data.get("api_key", "<none returned>")
    claim_url = data.get("claim_url", "<none returned>")
    print("Registered. SAVE THE API KEY NOW (it is shown once):\n")
    print(f"  api_key:   {api_key}")
    print(f"  claim_url: {claim_url}")
    print(
        "\nNext: export MOLTBOOK_API_KEY=<api_key>, then open claim_url and post "
        "the X claim tweet to verify the agent under the founder identity."
    )
    return 0


def cmd_post(args: argparse.Namespace) -> int:
    """Preview (dry-run) or submit POST /posts."""
    title, content = _parse_post(args.post_file)

    if len(title) > TITLE_MAX:
        print(f"Title is {len(title)} chars; Moltbook limit is {TITLE_MAX}.", file=sys.stderr)
        return 2
    if len(content) > CONTENT_MAX:
        print(f"Content is {len(content)} chars; Moltbook limit is {CONTENT_MAX}.", file=sys.stderr)
        return 2

    if not args.post:
        print(f"[dry-run] submolt_name: {args.submolt}")
        print(f"[dry-run] title:        {title}\n")
        print(content)
        print("\n[dry-run] no network call made. Pass --post to submit.")
        return 0

    api_key = os.environ.get("MOLTBOOK_API_KEY")
    if not api_key:
        print("Refusing to post: MOLTBOOK_API_KEY is not set.", file=sys.stderr)
        return 2

    payload = {"submolt_name": args.submolt, "title": title, "content": content}
    try:
        data = _request("POST", "/posts", payload, api_key=api_key)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Post failed: {exc}", file=sys.stderr)
        return 1

    url = data.get("url") or data.get("permalink") or "<no url returned>"
    print(f"Posted: {url}")
    print(
        "Now update examples/lighthouses/outreach-move62.yaml "
        "(sent_at / posted_url / last_touch + a posted comment) and refresh "
        "tools/outreach.db. Note Moltbook's rate limit: 1 post / 30 min."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_reg = sub.add_parser("register", help="Register the agent; prints api_key + claim_url.")
    p_reg.add_argument("--name", default="URML", help="Agent name (default: URML).")
    p_reg.add_argument(
        "--description",
        default="Open Apache-2.0 language for robot intent: English -> validated robot program.",
        help="Agent description.",
    )
    p_reg.set_defaults(func=cmd_register)

    p_post = sub.add_parser("post", help="Preview (default) or submit the demo post.")
    p_post.add_argument("--post-file", type=Path, default=DEFAULT_POST, help="Draft body file.")
    p_post.add_argument("--submolt", default="robotics", help="Target submolt_name (default: robotics).")
    p_post.add_argument("--post", action="store_true", help="Actually submit. Default is a dry run.")
    p_post.set_defaults(func=cmd_post)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
