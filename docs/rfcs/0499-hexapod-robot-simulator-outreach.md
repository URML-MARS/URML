---
rfc: 0499
title: hexapod-robot-simulator integration — request for comment
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

# RFC-0499: hexapod-robot-simulator integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`mithi/hexapod-robot-simulator`](https://github.com/mithi/hexapod-robot-simulator) (MIT, ~870 stars) is a clean, first-principles hexapod kinematics and control project (a browser simulator, with the maintainer's `hexapod-irl` carrying the work onto real hardware). URML is interesting to a hexapod as the typed-intent layer above its gait and pose control: a "walk forward" / "turn" / "strike this pose" intent becomes a typed primitive validated against the hexapod's declared leg structure before it drives the joints. This RFC asks whether the mapping is useful.

## The mapping (URML beside the hexapod)

- **Capability manifest.** The hexapod's six legs and their degrees of freedom map onto a URML `whole_body` kinematic-structure declaration (RFC-0384) plus a legged `drive_type`. A gait or pose intent is validated against that declared structure.
- **Validated intent, then dispatch.** URML turns the request into a typed primitive and validates it; the hexapod kinematics engine executes the gait. URML is the typed gate and intent record; it does not re-implement the inverse kinematics.

## What is asked

Request for comment from the maintainer:

1. Does mapping the hexapod's six-leg structure onto a URML `whole_body` declaration read right?
2. Is a typed, validated gait/pose intent layer above the kinematics engine interesting — for the simulator, or the `hexapod-irl` real-hardware path?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `whole_body` kinematic-structure declaration (RFC-0384), legged `drive_type`, and the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `mithi/hexapod-robot-simulator` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
