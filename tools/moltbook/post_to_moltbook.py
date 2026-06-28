#!/usr/bin/env python3
"""Post the URML agent's demonstration to Moltbook (RFC-0640, Move #62).

Operational glue, deliberately kept OUT of ``reference/``: Moltbook is a cloud
service, and ``CLAUDE.md`` prohibits cloud dependencies in the reference
runtimes. Nothing here is imported by the bridge, the validator, or any runtime;
this is a thin, standalone client.

Posture:

  * **Dry-run by default.** Without ``--post`` it prints the resolved post body
    and exits 0. It never touches the network unless you explicitly pass
    ``--post`` AND the credentials are present in the environment.
  * **Credentials come from the environment, never the repo:**
      - ``MOLTBOOK_API_TOKEN``  -- developer-API token for the verified agent.
      - ``MOLTBOOK_AGENT_ID``   -- the claimed agent's id.
      - ``MOLTBOOK_API_BASE``   -- API base URL (no default baked in; the
                                    developer API is early-access and its shape
                                    is not yet public).
  * **Standard library only.** The actual HTTP call uses ``urllib`` so the tool
    has no third-party dependency. The request shape below is a PLACEHOLDER to
    be confirmed against Moltbook's developer-API docs once access is granted;
    it is intentionally isolated in ``_submit()`` so it is the single thing to
    update.

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

DEFAULT_POST = Path(__file__).resolve().parent / "posts" / "demo-intro.md"

REQUIRED_ENV = ("MOLTBOOK_API_TOKEN", "MOLTBOOK_AGENT_ID", "MOLTBOOK_API_BASE")


def _parse_post(path: Path) -> tuple[str, str]:
    """Split a draft body file into (title, body).

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


def _missing_env() -> list[str]:
    return [name for name in REQUIRED_ENV if not os.environ.get(name)]


def _submit(title: str, body: str, submolt: str) -> str:
    """POST the body to Moltbook. Returns the created thread URL.

    PLACEHOLDER request shape. Confirm against Moltbook's developer-API docs
    before relying on it; this is the only function that should need changing
    when the real API surface is known.
    """
    base = os.environ["MOLTBOOK_API_BASE"].rstrip("/")
    token = os.environ["MOLTBOOK_API_TOKEN"]
    agent_id = os.environ["MOLTBOOK_AGENT_ID"]
    payload = json.dumps(
        {"agent_id": agent_id, "submolt": submolt, "title": title, "body": body}
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/posts",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - explicit https base expected
        data = json.loads(resp.read().decode("utf-8"))
    return str(data.get("url", "<no url returned>"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--post-file",
        type=Path,
        default=DEFAULT_POST,
        help="Draft body file (default: posts/demo-intro.md).",
    )
    parser.add_argument(
        "--submolt",
        default="robotics",
        help="Target submolt (default: robotics).",
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Actually submit. Without this flag the script is a dry run.",
    )
    args = parser.parse_args(argv)

    title, body = _parse_post(args.post_file)

    if not args.post:
        print(f"[dry-run] submolt: {args.submolt}")
        print(f"[dry-run] title:   {title}\n")
        print(body)
        print("\n[dry-run] no network call made. Pass --post to submit.")
        return 0

    missing = _missing_env()
    if missing:
        print(
            "Refusing to post: missing environment variable(s): "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    try:
        url = _submit(title, body, args.submolt)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Post failed: {exc}", file=sys.stderr)
        return 1

    print(f"Posted: {url}")
    print(
        "Now update examples/lighthouses/outreach-move62.yaml "
        "(sent_at / posted_url / last_touch + a posted comment) and refresh "
        "tools/outreach.db."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
