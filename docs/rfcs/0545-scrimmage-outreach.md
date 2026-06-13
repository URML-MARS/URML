---
rfc: 0545
title: SCRIMMAGE integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0545: SCRIMMAGE integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the swarm / multi-robot / alternative-framework wave (Move #49).

## Summary

[`gtri/scrimmage`](https://github.com/gtri/scrimmage) (LGPL-3.0, ~178 stars, active, Georgia Tech Research Institute) is a multi-agent robotics simulator built for large heterogeneous scenarios. URML is interesting at the multi-robot coordination layer: a scenario of N agents maps onto URML's fleet roster, and the per-agent actions plus the cross-agent separation constraints are exactly what URML declares and validates. This RFC asks whether the mapping is useful.

## The mapping (URML beside SCRIMMAGE)

- **Roster + deconfliction for a scenario.** A SCRIMMAGE scenario of many agents maps onto a URML roster (RFC-0286): each agent a member with a capability manifest, the scenario's separation requirements expressed as cross-robot deconfliction (RFC-0291). URML validates the multi-agent intent before it runs.
- **Validated intent, then simulate / dispatch.** URML is the typed, statically-validated multi-agent intent; SCRIMMAGE is the simulation (or, for a real deployment, the substrate executes). URML does not simulate; it declares and checks.

## What is asked

Request for comment from the SCRIMMAGE maintainers:

1. Does a URML fleet roster + cross-agent deconfliction fit how SCRIMMAGE scenarios declare many heterogeneous agents?
2. Is a statically-validated multi-agent intent layer above a SCRIMMAGE scenario interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's multi-robot fleet addressing (RFC-0286), cross-robot deconfliction (RFC-0291), and the simulation engagements (Move #24). Part of Move #49.

## Implementation note

Outreach only. The post is a GitHub Issue on `gtri/scrimmage` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is LGPL-3.0; state it, do not ask). Tracked in `examples/lighthouses/outreach-move49.yaml`.
