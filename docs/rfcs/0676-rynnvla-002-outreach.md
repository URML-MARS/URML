---
rfc: 0676
title: RynnVLA-002 (alibaba-damo-academy/RynnVLA-002) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-18
updated: 2026-08-18
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

# RFC-0676: RynnVLA-002 (alibaba-damo-academy/RynnVLA-002) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It continues the VLA / robot-foundation-model wave (Move #61).

## Summary

[`alibaba-damo-academy/RynnVLA-002`](https://github.com/alibaba-damo-academy/RynnVLA-002) unifies a Vision-Language-Action model and a world model in one framework: the VLA half maps text and image observations to a concrete continuous action (via an Action Transformer, with wrist-camera and state input) on real-world LeRobot arms, and the world-model half predicts the next frame given an action. Because the VLA half emits a concrete action for a real arm, URML's validate-before-actuate gate has a surface: the robot declares a capability manifest and a safety envelope, and URML checks the emitted action is admissible before dispatch. This is a request for comment.

## The relationship (URML beside RynnVLA-002)

- **The model emits the action, the validator gates it.** RynnVLA-002 emits the continuous action; URML checks it is admissible on the declared LeRobot arm (within its force, reach, and mobility, inside the safety envelope) before it reaches the hardware. URML does not touch the model or the world-model rollout.
- **Static gate, complementary to the world model.** The world model predicts consequences by rolling a frame forward; URML's check is a static admissibility gate that needs no rollout and runs before dispatch. The two are complementary vantage points on the same action.
- **A neutral layer.** URML is substrate- and model-neutral (the LLM bridge is provider-agnostic). It composes above the emitted action rather than depending on the model's internals.

## What is asked

1. For the real-world LeRobot experiments, would a declared capability + safety envelope be a useful pre-dispatch guard on the emitted action?
2. Would a small worked example mapping a RynnVLA-002 action onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #61 VLA / robot-foundation-model wave (open-weight tranche).

## Implementation note

Outreach only. The post is a GitHub Issue on `alibaba-damo-academy/RynnVLA-002` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
