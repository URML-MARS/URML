---
rfc: 0657
title: VeriGraph (daniekpo/verigraph) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-03
updated: 2026-07-03
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

# RFC-0657: VeriGraph integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #67.

## Summary

[`daniekpo/verigraph`](https://github.com/daniekpo/verigraph) (Daniel Ekpo, Brigham Young University) uses scene graphs to make robot planning verifiable: it produces action sequences that can be checked against the scene before execution. That is the closest conceptual sibling URML has found. URML is a small Apache-2.0 language that verifies an intended action a different way, against a robot's declared capability manifest and safety envelope, before it runs. The two verify different things, and they may compose.

## The relationship (URML beside VeriGraph)

VeriGraph verifies that a planned action is consistent with the scene: the objects, the relations, whether the plan makes semantic sense. URML verifies that the action is admissible on the specific robot: reach, payload, gripper force, keep-out, speed. One is a semantic check against the world; the other is a capability check against the machine. A plan that passes both is verified in scene and admissible on the robot, and neither check subsumes the other.

URML does not build scene graphs and does not plan. It is interested in the seam: an action VeriGraph has verified against the scene, checked against what the robot is declared able to do, before it executes.

## What is asked

1. Do a scene-graph verification (semantic) and a declared-capability-plus-envelope verification (admissibility) compose cleanly as two independent gates on the same action, or do they overlap more than that framing suggests?
2. Would a small worked example, taking a VeriGraph-verified action sequence through a URML manifest check (validated, no execution), help show where the two lines sit?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, placed beside a scene-graph verifiable-planning method. MIT; Brigham Young University (Daniel Ekpo), US. Part of Move #67.

## Implementation note

Outreach only. The post is a GitHub Issue on `daniekpo/verigraph` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move67.yaml`.
