---
rfc: 0453
title: BEHAVIOR-1K (Stanford) integration — request for comment
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

# RFC-0453: BEHAVIOR-1K (Stanford) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family, the simulation-engagement pattern (RFC-0381), and the wrap-a-learned-policy pattern. Tier B.

## Summary

[`StanfordVL/BEHAVIOR-1K`](https://github.com/StanfordVL/BEHAVIOR-1K) (~1,508 stars, active, Discussions on) is the Stanford Vision Lab embodied-AI platform covering 1,000 everyday household activities, a benchmark for generalist embodied agents. Its activity definitions are essentially structured task intent, which makes it a natural place to discuss a typed, validated intent layer above the policies that execute those activities. This RFC asks whether that is interesting.

## The mapping (URML above BEHAVIOR-1K)

URML sits above the simulated robot / learned policy as a validated intent layer:

- A URML intent expresses a BEHAVIOR activity goal and its envelope; a learned policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts.
- BEHAVIOR's structured activity/predicate definitions and URML's typed intent + manifest are complementary: a place to compare how each expresses task goals and constraints.
- Validate-before-actuate refuses an out-of-capability request before the simulated robot moves.

## What is asked

Request for comment from the BEHAVIOR-1K maintainers:

1. Is a typed, validated intent layer above BEHAVIOR activities interesting for embodied-AI research?
2. What should a URML capability manifest declare to describe a BEHAVIOR task robot honestly (arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, object/activity vocabulary)?
3. How do BEHAVIOR's activity/predicate definitions relate to URML's typed intent + safety envelope?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the simulation-engagement pattern (RFC-0381); the earlier VLA wave (Move #11). BEHAVIOR-1K is the everyday-activity-benchmark vertex of the round-2 wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Discussion on `StanfordVL/BEHAVIOR-1K` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front. The repo's license terms are project-specific; URML proposes nothing under them and asks no change. Tracked in `examples/lighthouses/outreach-move38.yaml`.
