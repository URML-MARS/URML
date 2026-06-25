---
rfc: 0632
title: Magma (microsoft/Magma) integration — request for comment
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

# RFC-0632: Magma (microsoft/Magma) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the VLA / robot-foundation-model wave (Move #61).

## Summary

[`microsoft/Magma`](https://github.com/microsoft/Magma) (Microsoft Research, US) is a multimodal foundation model for AI agents that grounds language and vision into action across UI agents and robot manipulation. Because its output is a concrete action rather than text, it sits exactly where URML's validate-before-actuate gate has a surface: a robot declares a capability manifest (grippers, reach, payload, sensors) and a safety envelope, and URML validates each action against that declaration before it reaches the hardware. This is a request for comment.

## The relationship (URML beside Magma)

- **The model proposes, the validator gates.** Magma decides what action to take; URML checks the specific action is admissible on the specific robot (within its declared force, reach, mobility, and object vocabulary, inside the safety envelope) before it executes. URML does not constrain the model; it makes the action surface checkable.
- **A neutral layer.** URML is substrate- and model-neutral by construction (the LLM bridge is provider-agnostic). It composes above Magma's action output rather than depending on its internals.

## What is asked

1. Would a declared capability + safety envelope be a useful guardrail on top of Magma's action output, especially for manipulation across embodiments?
2. Would a small worked example mapping a Magma action onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of Move #61 (the net-new VLA / robot-foundation-model wave); US-origin lead target.

## Implementation note

Outreach only. The post is a GitHub Issue on `microsoft/Magma` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
