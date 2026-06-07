---
rfc: 0440
title: Surgical Robotics Challenge integration — request for comment
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

# RFC-0440: Surgical Robotics Challenge integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the safety-envelope model. It is the anchor of the medical / surgical research-robotics wave (Move #37). **Scope: research and simulation only. URML makes no clinical claim and is not for patient use.**

## Summary

[`surgical-robotics-ai/surgical_robotics_challenge`](https://github.com/surgical-robotics-ai/surgical_robotics_challenge) (custom permissive academic license, ~109 stars, very active, Discussions on) is the AMBF/ROS interactive robot-assisted suturing simulation behind the AccelNet surgical-robotics challenge (a JHU + WPI consortium). Its audience is precisely "turn a high-level surgical-subtask description into validated robot action in a research sim" — exactly URML's shape. This RFC asks whether a validated intent layer above it is interesting for research.

## The mapping (URML above the challenge sim)

URML sits above the simulated research robot as a validated intent layer:

- URML's ROS 2 runtime meets the challenge environment on its ROS surface; a research subtask ("approach the needle, then insert at the entry marker") lowers onto the dVRK PSM/ECM interface as typed primitives, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-workspace pose or an undeclared instrument before motion — a research-grade safety boundary, and a natural fit for a community whose explicit norm is "not for clinical use".
- URML's safety envelope is a place to declare the research constraints a subtask must respect (workspace bounds, instrument set, no-go regions).

## What is asked

Request for comment from the Surgical Robotics Challenge maintainers:

1. Is a validated intent layer above the challenge sim interesting as a way to express and check surgical-subtask intent in research?
2. What should a URML capability manifest declare to describe a research surgical robot honestly (arms/instruments, reach/DOF, workspace bounds, instrument vocabulary)?
3. Where is the cleanest seam — above the AMBF/ROS action surface, or composing with the challenge's task definitions?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27); the safety / runtime-verification engagement (Move #28) on declared properties; the bimanual work (RFC-0010) for two-arm surgical platforms. The Surgical Robotics Challenge is the anchor of the medical / surgical research wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `surgical-robotics-ai/surgical_robotics_challenge` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (custom permissive academic license). Research/sim framing only. The sibling `SurgicAI` repo is referenced, not posted to separately. Tracked in `examples/lighthouses/outreach-move37.yaml`.
