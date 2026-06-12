---
rfc: 0479
title: GELLO integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0479: GELLO integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validated-intent layer and its decide-then-do split. It is the anchor of the teleoperation / data-collection wave (Move #42).

## Summary

[`wuphilipp/gello_software`](https://github.com/wuphilipp/gello_software) (MIT, ~488 stars, active) is the software for GELLO, a low-cost leader-arm teleoperation rig that has become a default way to collect manipulation demonstrations. URML is interesting to a teleop / data-collection system in two ways, neither of which competes with manual control: as a validated *shared-autonomy* layer the rig can hand off to, and as a typed *schema for the demonstrated intent* recorded alongside the trajectory. This RFC asks whether either is useful.

## The mapping (URML beside GELLO)

Two complementary seams:

- **Shared-autonomy handoff.** The operator stays in control by default; when they issue a high-level command ("pick that up", "move to the bin"), URML validates it against the robot's declared capabilities and a safety envelope, then dispatches — and teleop remains the correction path. URML adds the capability/envelope gate a raw teleop stream does not have.
- **Typed-intent annotation.** Each demonstration segment is labelled with the URML primitive it represents (`grasp($obj)`, `move_to(bin)`), so a recorded demo carries a typed, validatable intent next to the trajectory — structured supervision a downstream policy can learn from, and a record the validator can check against the manifest.

## What is asked

Request for comment from the GELLO maintainers:

1. Is a validated shared-autonomy handoff (operator commands a high-level intent; URML validates + dispatches; teleop corrects) interesting on a GELLO rig?
2. Is labelling demonstration segments with a typed URML primitive useful for the data you collect?
3. Which is the cleaner first seam — the handoff, or the annotation?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's validated-intent layer and the decide-then-do split (RFC-0002); the VLA / robot-learning engagements (Moves #11, #38) that consume demonstration data. GELLO is the anchor of the teleop / data-collection wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `wuphilipp/gello_software` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move42.yaml`.
