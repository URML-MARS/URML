# meta/discussions-snapshot

Machine-written branch. The scheduled workflow
`.github/workflows/discussions-snapshot.yml` on `main` force-pushes a
single-commit snapshot of this repo's GitHub Discussions here once a
day. The daily Discussions-triage cloud routine reads
`discussions.json` from this branch via `git fetch`, because its
sandbox cannot reach the GitHub API (the egress proxy serves only a
pinned set of PR-review operations).

Do not base work on this branch. History is intentionally one commit
deep on top of main.
