---
rfc: 0503
title: bipedal-locomotion-framework integration — request for comment
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

# RFC-0503: bipedal-locomotion-framework integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`gbionics/bipedal-locomotion-framework`](https://github.com/gbionics/bipedal-locomotion-framework) (BSD-3-Clause, ~220 stars, active, IIT lineage; transferred from `ami-iit`) is a set of libraries for bipedal locomotion on humanoids (model-predictive control plus whole-body control). URML is interesting one layer above: a locomotion intent for a humanoid is validated against the robot's declared structure and stability limits, then handed to this framework's MPC/WBC to realize. This RFC asks whether the seam is useful.

## The mapping (URML beside the framework)

- **Whole-body manifest.** The humanoid's kinematic structure and stability limits (center-of-mass bounds, support polygon) map onto a URML `whole_body` declaration (RFC-0384). URML validates a locomotion intent against that envelope before it reaches the controller.
- **Validated goal, then locomotion.** URML decides (typed, validated intent); the framework does (the MPC + whole-body control that keeps the humanoid balanced and moving). URML is the typed gate above the locomotion stack.

## What is asked

Request for comment from the maintainers:

1. Does a URML `whole_body` manifest (structure + stability limits) match how this framework models the humanoid?
2. Is a validated-intent layer that hands locomotion goals to the MPC/WBC interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `whole_body` kinematic-structure + stability-limits declaration (RFC-0384) and the decide-then-do split (RFC-0002). Part of Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `gbionics/bipedal-locomotion-framework` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
