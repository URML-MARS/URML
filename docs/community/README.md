# URML community signals

This directory holds the monthly community-activity notes for the URML repository.

## What lives here

- `metrics-YYYY-MM.md` — one curated, human-edited note per calendar month, summarizing forks, stars, traffic, issue and PR activity, RFC movement, and new contributors. These are the public face: a record that the project is alive, where attention is coming from, and what's moving.

The notes are generated as drafts by automation, then edited by the maintainer before merging. The narrative — *why* the numbers moved, what conversations they reflect, what's worth highlighting — is added by hand. The numbers without context are just numbers.

## How the notes are generated

A monthly GitHub Actions cron job runs [`.github/scripts/collect_metrics.py`](../../.github/scripts/collect_metrics.py), which calls the GitHub REST API via `gh api` and produces two artifacts:

1. **`metrics-YYYY-MM-full.json`** — the full raw dump, uploaded as a workflow artifact (private to the maintainer via the Actions UI). Not committed to the repo. Useful for spot-checking, trend analysis, and going deeper than the public note.
2. **`metrics-YYYY-MM.md`** — a curated Markdown draft that the workflow opens as a draft pull request. The maintainer edits, fills in the *Narrative* section, and merges — or closes the PR without merging if a particular month is better not recorded publicly.

Manual runs are possible via `workflow_dispatch` from the Actions tab.

The traffic numbers (clones, views, top referrers, top paths) cover a rolling 14-day window — GitHub's traffic API does not retain longer history. They are reported as-of the run date, not for the calendar month being summarized. The note is explicit about this.

## What the notes deliberately do not include

- **Per-user activity profiles.** Counts and aggregates only; no individual-contributor dashboards beyond naming new contributors (which is GitHub-public anyway).
- **Telemetry from runtimes or tools.** Per [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do, URML tools do not collect usage telemetry. These notes only summarize what is already public on the repo.
- **External-platform engagement.** Mailing lists, social media, conference activity belong elsewhere if they become relevant; this directory tracks repo signals only.

## Running locally

The same script can be invoked from a developer machine if `gh auth login` is set up:

```bash
python .github/scripts/collect_metrics.py --repo URML-MARS/URML --dry-run
```

`--dry-run` prints both outputs to stdout instead of writing files. Useful for spot-checking the first-response calculations before trusting a monthly note.
