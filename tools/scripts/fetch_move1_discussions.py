#!/usr/bin/env python3
"""Fetch the five Move #1 vendor discussion threads via GitHub GraphQL.

Usage (on a GitHub Actions runner with GITHUB_TOKEN set):
    python tools/scripts/fetch_move1_discussions.py /tmp/discussions.json

Writes the raw GraphQL response JSON to the given path.
Exits 1 on GraphQL errors.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
{
  yaskawa: repository(owner:"Yaskawa-Global", name:"motoros2") {
    discussion(number:495) {
      title closed
      reactions { totalCount }
      comments(first:100) { nodes {
        author { login } createdAt body
        reactions { totalCount }
        replies(first:50) { nodes { author { login } createdAt body } }
      }}
    }
  }
  ur: repository(owner:"UniversalRobots", name:"Universal_Robots_ROS2_Driver") {
    discussion(number:1799) {
      title closed
      reactions { totalCount }
      comments(first:100) { nodes {
        author { login } createdAt body
        reactions { totalCount }
        replies(first:50) { nodes { author { login } createdAt body } }
      }}
    }
  }
  kuka: repository(owner:"kroshu", name:"kuka_drivers") {
    discussion(number:342) {
      title closed
      reactions { totalCount }
      comments(first:100) { nodes {
        author { login } createdAt body
        reactions { totalCount }
        replies(first:50) { nodes { author { login } createdAt body } }
      }}
    }
  }
  staubli: repository(owner:"ros-industrial", name:"staubli_val3_driver") {
    discussion(number:57) {
      title closed
      reactions { totalCount }
      comments(first:100) { nodes {
        author { login } createdAt body
        reactions { totalCount }
        replies(first:50) { nodes { author { login } createdAt body } }
      }}
    }
  }
  mitsubishi: repository(owner:"Mitsubishi-Electric-Asia", name:"melfa_ros2_driver") {
    discussion(number:25) {
      title closed
      reactions { totalCount }
      comments(first:100) { nodes {
        author { login } createdAt body
        reactions { totalCount }
        replies(first:50) { nodes { author { login } createdAt body } }
      }}
    }
  }
}
"""


def main() -> None:
    out_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/vendor-discussions.json"
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN or GH_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({"query": QUERY}).encode()
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
        data = json.loads(resp.read().decode())

    errors = data.get("errors")
    if errors:
        print(f"GraphQL errors: {errors}", file=sys.stderr)
        sys.exit(1)

    slugs = list((data.get("data") or {}).keys())
    print(f"Snapshot contains data for: {', '.join(slugs)}")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
