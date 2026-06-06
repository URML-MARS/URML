---
rfc: 0410
title: PRBonn AgriBot integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0410: PRBonn AgriBot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and capability-manifest model.

## Summary

[`PRBonn/agribot`](https://github.com/PRBonn/agribot) (BSD-2-Clause, ~179 stars) is a from-scratch agricultural data-recording field robot from the University of Bonn Photogrammetry & Robotics lab — one of the most credible academic groups in agricultural perception and mapping. The platform is ROS-based, and PRBonn's broader work (crop/weed semantic mapping, agricultural SLAM) is exactly the kind of perception substrate a validated intent layer composes with. This RFC asks whether a URML intent layer above an AgriBot-class field robot is interesting.

## The mapping (URML above AgriBot)

URML sits above the field robot as a validated intent layer:

- URML's ROS 2 runtime targets the AgriBot's ROS surface; a "survey the field and record" intent lowers onto its navigation + data-recording interface.
- PRBonn's crop/weed perception is the kind of `detect` source URML consumes: a detection binds a target a downstream action consumes (the decide-then-do split).
- Validate-before-actuate refuses an out-of-capability request before dispatch; the field-robot shape stresses the manifest usefully (row geometry, sensor suite, GNSS).

## What is asked

Request for comment from the PRBonn AgriBot maintainers:

1. What should a URML capability manifest declare to describe an agricultural field robot honestly (drive type, row/field geometry, sensor suite, GNSS/positioning)?
2. Is a validated natural-language intent layer above an AgriBot-class platform interesting for the lab's research?
3. Where is the cleanest seam — URML above the navigation/recording interface, or composing with the lab's perception/mapping outputs as `detect` sources?

Nothing here asks PRBonn to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `detect`-then-act split (RFC-0002); the SLAM/state-estimation engagement (Move #25) as the pattern of consuming a perception/estimate rather than reimplementing it. PRBonn is the academic field-robot / ag-perception vertex of the agriculture wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `PRBonn/agribot` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-2-Clause). Tracked in `examples/lighthouses/outreach-move33.yaml`.
