---
rfc: 0637
title: VoxPoser (huangwl18/VoxPoser) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-25
updated: 2026-06-25
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

# RFC-0637: VoxPoser (huangwl18/VoxPoser) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #61 (university lane).

## Summary

[`huangwl18/VoxPoser`](https://github.com/huangwl18/VoxPoser) (Stanford Vision & Learning Lab; Wenlong Huang, with Fei-Fei Li and Jiajun Wu) turns a free-form instruction directly into an executed manipulation trajectory via composed 3D value maps, zero-shot, with no task-specific training. That language-to-motion directness is precisely where URML's validate-before-actuate gate has a surface: a robot declares a capability manifest and a safety envelope, and URML validates the synthesized motion against that declaration before it executes. This is a request for comment.

## The relationship (URML beside VoxPoser)

- **Check the trajectory before the arm moves.** VoxPoser composes the trajectory; URML checks it is admissible on the specific robot, flagging a motion that exceeds the arm's reach, the gripper's force, or a declared keep-out region, before anything actuates. It does not touch the value-map synthesis; it is the last checkable step.
- **A guardrail for zero-shot output.** Because the synthesis is zero-shot and unconstrained by task-specific training, a static declared-capability check is a natural complement: creative trajectory, declared safe envelope.

## What is asked

1. Is a declared capability + safety envelope a useful guardrail on top of zero-shot trajectory synthesis?
2. Would a small worked example mapping a VoxPoser-style trajectory onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a zero-shot instruction-to-trajectory synthesizer. Part of Move #61 (university lane); US, Stanford SVL.

## Implementation note

Outreach only. The post is a GitHub Issue on `huangwl18/VoxPoser` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
