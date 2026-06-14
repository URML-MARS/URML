---
rfc: 0575
title: iRobot Create 3 integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0575: iRobot Create 3 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the education / competition wave (Move #52).

## Summary

[`iRobotEducation/create3_docs`](https://github.com/iRobotEducation/create3_docs) (BSD-3-Clause) is the documentation and resources for the iRobot Create 3, an educational mobile robot with a ROS 2 interface. URML is a small, Apache-2.0 language for robot intent: an English instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. The Create 3 is a clean, well-documented platform to show the natural-language-to-validated-intent path. This RFC asks whether the mapping is useful.

## The mapping (URML beside the Create 3)

- **An English front door over the Create 3's ROS 2 interface.** The Create 3 exposes a well-defined set of actions over ROS 2. That maps onto a URML capability manifest, so "drive a square, then dock" can become a typed, validated intent that dispatches through the Create 3's existing ROS 2 interface. URML adds the typed validation and the English layer; the Create 3 stays the runtime.
- **Educational fit.** As a teaching robot with strong docs, the Create 3 is a natural place to make the intent-and-validation story visible to learners.

## What is asked

Request for comment from the iRobot Education maintainers:

1. Is an English-to-validated-intent front door useful for the Create 3 in an educational setting?
2. Does the Create 3's ROS 2 action set map cleanly onto a URML capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the capability manifest, the ROS 2 reference runtime, and the educational profile (RFC-0011). Completes Move #52; the documented ROS-2 educational platform of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `iRobotEducation/create3_docs` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move52.yaml`.
