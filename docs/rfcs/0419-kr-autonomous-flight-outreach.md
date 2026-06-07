---
rfc: 0419
title: KumarRobotics kr_autonomous_flight integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0419: KumarRobotics kr_autonomous_flight integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type and ROS 2 runtime. Tier B.

## Summary

[`KumarRobotics/kr_autonomous_flight`](https://github.com/KumarRobotics/kr_autonomous_flight) (UPenn academic software license, ~771 stars, active) is a complete GPS-denied autonomous-flight stack from the Kumar Lab at UPenn — one of the most credible groups in aerial autonomy. It is released under the lab's own academic-use software license (URML proposes nothing under it; this is a mapping discussion only). This RFC asks whether a validated intent layer above a GPS-denied autonomy stack is interesting.

## The mapping (URML above kr_autonomous_flight)

URML sits above the autonomy stack as a validated intent layer:

- URML's `aerial` drive type and ROS 2 runtime meet the stack on its ROS surface; "fly to this position through the building and report" lowers onto its planning/control layer.
- The stack's strength is GPS-denied state estimation; URML consumes that estimate rather than reimplementing it (the same posture as the SLAM/state-estimation engagement, Move #25).
- Validate-before-actuate refuses an out-of-envelope request before the drone acts, which matters in cluttered indoor flight.

## What is asked

Request for comment from the kr_autonomous_flight maintainers:

1. Is the ROS surface the right seam for an external validated-intent layer above a GPS-denied autonomy stack?
2. What should a URML capability manifest declare to describe such a platform honestly (drive type, altitude/speed limits, positioning source, operating volume)?
3. Is a validated natural-language layer interesting for the lab's GPS-denied flight research?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and ROS 2 runtime; the SLAM/state-estimation engagement (Move #25) — consume the estimate, do not reinvent it; the aerial-autonomy anchor (RFC-0412). kr_autonomous_flight is the GPS-denied-autonomy vertex of the aerial wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `KumarRobotics/kr_autonomous_flight` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front. The repo carries a UPenn academic software license; URML proposes nothing under it and asks no license change. Tracked in `examples/lighthouses/outreach-move34.yaml`.
