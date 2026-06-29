---
rfc: 0641
title: Embodied Chain-of-Thought (MichalZawalski/embodied-CoT) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-28
updated: 2026-06-28
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

# RFC-0641: Embodied Chain-of-Thought integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #63 (VLA / robot-foundation mini-wave).

## Summary

[`MichalZawalski/embodied-CoT`](https://github.com/MichalZawalski/embodied-CoT) trains a vision-language-action policy to reason out loud before it acts: it writes an embodied chain of thought (the plan, the sub-tasks, the gripper position it is moving toward) and then emits the action. URML is a small Apache-2.0 language whose one job is to check an intended action against a robot's declared capability manifest and safety envelope before it runs. The interesting overlap is the reasoning trace: ECoT already exposes the policy's intent in a legible form, which is exactly the place a capability check can sit.

## The relationship (URML beside ECoT)

The reasoning chain is a gift to a static check. When the model writes "move to the drawer handle, then close the gripper," URML can ask, before the arm moves, whether that handle pose is inside the declared reach and whether the gripper the manifest declares can close on it. A plausible-but-out-of-capability plan is caught at the point where it is still just text, not motion.

URML touches none of the policy or the reasoning generation. It is the last checkable step between the emitted action and the hardware, and the explicit ECoT trace makes a rejection explainable rather than opaque ("rejected: the reasoned sub-goal exceeds declared reach").

## What is asked

1. Does an explicit embodied reasoning trace make a pre-actuation capability check more useful than it would be on a black-box action head, since the intent is already written down?
2. Would a small worked example mapping an ECoT sub-goal and its action onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a reasoning-then-acting VLA. MIT-licensed; Michał Zawalski (University of Warsaw, with US co-authors). Part of Move #63.

## Implementation note

Outreach only. The post is a GitHub Issue on `MichalZawalski/embodied-CoT` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move63.yaml`.
