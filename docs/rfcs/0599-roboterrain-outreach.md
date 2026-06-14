---
rfc: 0599
title: RoboTerrain integration — request for comment
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

# RFC-0599: RoboTerrain integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the inspection-robotics wave (Move #55).

## Summary

[`jackvice/RoboTerrain`](https://github.com/jackvice/RoboTerrain) (Apache-2.0) is a ROS 2 + Gazebo reinforcement-learning framework for off-road navigation, with environments that explicitly include industrial inspection and construction sites (Husky, rover, Leo platforms). URML sits above a trained off-road policy at the intent layer: it declares the goal and the operating bounds, validates them, and the policy drives. This RFC asks whether the mapping is useful.

## The mapping (URML beside RoboTerrain)

- **A validated-intent gate over a trained policy.** RoboTerrain trains policies to navigate unstructured terrain. URML's decide-then-do split puts a typed, validated intent in front of the policy: declare the inspection or traversal goal plus the off-road operating bounds (slope, traversability, standoff), validate against the platform's declared capabilities, then let the trained policy drive within that envelope. The training and the policy stay with RoboTerrain.
- **A policy that declares its envelope.** URML's LearnedPolicy direction (RFC-0383) is the idea that a trained policy can declare the conditions it was trained for, so an intent can be checked against that envelope before the policy is trusted on a real inspection.

## What is asked

1. Is a typed, validated intent gate (declare goal + off-road bounds, validate, then let the policy drive) useful above a RoboTerrain-trained policy?
2. Could a trained policy declare a training/operating envelope a URML intent is checked against (RFC-0383)?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's decide-then-do split (RFC-0002), the LearnedPolicy envelope (RFC-0383), the safety-envelope validation, and the off-road / unstructured-terrain framing. Completes Move #55; the off-road-RL inspection target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `jackvice/RoboTerrain` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move55.yaml`.
