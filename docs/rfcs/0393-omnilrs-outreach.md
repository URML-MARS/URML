---
rfc: 0393
title: OmniLRS (Omniverse Lunar Robotics Simulator) integration — request for comment
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

# RFC-0393: OmniLRS (Omniverse Lunar Robotics Simulator) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the simulation-fidelity manifest hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)).

## Summary

[OmniLRS](https://github.com/OmniLRS/OmniLRS) (BSD-3-Clause, ~219 stars) is the Omniverse Lunar Robotics Simulator: an Isaac-Sim-based lunar environment with explicit ROS 2 / Space-ROS teleop integration. It is a simulation substrate where a URML-validated command can drive a lunar rover through the existing ROS 2 bridge. This RFC asks the OmniLRS maintainers whether a URML demonstration on the simulator is interesting and how the lunar context should be declared.

## The mapping (URML above OmniLRS)

URML sits above the sim's ROS 2 bridge as a validated intent layer:

- A URML program drives an OmniLRS lunar rover via the simulator's ROS 2 / Space-ROS teleop interface — the same ROS surface URML's runtime already targets.
- URML's `validation` block (RFC-0381) declares the simulation-fidelity context (terrain class, simulator target) the deployment was validated against, which OmniLRS's regolith / deformable-terrain modeling makes concrete.
- The hermetic, sim-first posture matches URML's own (its mock substrate proves the language end to end with no hardware); OmniLRS is the high-fidelity lunar counterpart.

## What is asked

Request for comment from OmniLRS maintainers:

1. Is a validated natural-language intent layer above OmniLRS interesting as a teaching / demonstration surface for lunar-rover scenarios?
2. What should a URML manifest declare to describe a lunar deployment honestly (terrain/regolith class, slope and traction limits, lighting / thermal constraints)?
3. Where is the cleanest seam for a URML → OmniLRS demonstration via the ROS 2 / Space-ROS bridge?

Nothing here asks OmniLRS to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation` simulation-fidelity hints, surfaced by the Move #24 sim wave); RFC-0388 (Space-ROS), to which OmniLRS already bridges. OmniLRS is the lunar-simulation vertex of the space wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `OmniLRS/OmniLRS` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move31.yaml`.
