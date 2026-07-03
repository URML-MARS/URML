---
rfc: 0658
title: AIRO airo-mono (airo-ugent/airo-mono) integration — request for comment
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

# RFC-0658: AIRO airo-mono integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #67.

## Summary

[`airo-ugent/airo-mono`](https://github.com/airo-ugent/airo-mono) (AI and Robotics Lab, Ghent University) is a Python library for robotic manipulation: the shared building blocks the lab's projects use to command arms and grippers. URML is a small Apache-2.0 language that checks an intended manipulation against a robot's declared capability manifest and safety envelope before it runs. A manipulation library that issues arm and gripper commands is a place where such a check can sit, one layer above the command.

## The relationship (URML beside airo-mono)

Code built on airo-mono decides a manipulation and issues it through the library. URML can declare the arm's reach and payload and the gripper's force range, and validate a commanded manipulation against that declaration before the library dispatches it. It is a static admissibility check above the library, not a replacement for any of it.

To be honest about the fit: airo-mono is infrastructure, not a policy or a model, so URML's value here is narrower than for an autonomy layer that generates actions. It is the same check, applied to whatever the code above the library decides to command.

## What is asked

1. For a manipulation library, is a declared-capability and envelope check above the commands a useful addition for the projects built on it, or does that belong in each project rather than near the library?
2. Would a small worked example mapping an airo-mono arm-and-gripper command onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied above a robotic-manipulation library. MIT; AIRO, Ghent University, Belgium. Part of Move #67.

## Implementation note

Outreach only. The post is a GitHub Issue on `airo-ugent/airo-mono` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move67.yaml`.
