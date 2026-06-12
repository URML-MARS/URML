---
rfc: 0467
title: rosboard integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
supersedes: —
superseded-by: —
---

<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# RFC-0467: rosboard integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validate-before-actuate audit trail.

## Summary

[`dheera/rosboard`](https://github.com/dheera/rosboard) (BSD-3-Clause, ~1.1k stars, active) is a ROS node that serves a web dashboard for visualizing topics in a browser — the lowest-friction way to watch a robot from a phone or laptop with no install. URML is interesting to it as a *data source*: the validated-intent audit stream (intent → verdict → dispatch) is exactly the kind of human-legible signal a glanceable dashboard wants. This RFC asks whether surfacing it is interesting.

## The mapping (URML on a rosboard panel)

URML sits beside, not below, the dashboard:

- A URML runtime publishes its audit records on a topic; rosboard can render them as a live panel: the current intent, whether it validated, and what was dispatched — readable at a glance next to the usual topic tiles.
- A refused intent (out-of-capability or out-of-envelope) becomes a visible, explained event rather than a silent non-action.

## What is asked

Request for comment from the rosboard maintainer:

1. Is a "validated intent" panel (intent / verdict / dispatch) a useful addition to rosboard's topic tiles?
2. Is publishing audit records on a ROS topic the right seam, or a dedicated rosboard data type?
3. What would a glanceable validated-intent tile most want to show?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's five-pass validator + audit trail; the Open MCT telemetry engagement (RFC-0395); the Lichtblick anchor (RFC-0463). rosboard is the lightweight-web-dashboard vertex of the developer-tooling wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `dheera/rosboard` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move40.yaml`.
