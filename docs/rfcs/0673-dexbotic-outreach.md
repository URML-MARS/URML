---
rfc: 0673
title: Dexbotic (dexmal/dexbotic) integration — request for comment
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

# RFC-0673: Dexbotic (dexmal/dexbotic) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It continues the VLA / robot-foundation-model wave (Move #61).

## Summary

[`dexmal/dexbotic`](https://github.com/dexmal/dexbotic) is a VLA development and deployment toolbox that reproduces, fine-tunes, and serves mainstream policies (π0, CogACT, OFT, GR00T, NaVILA, and more) behind a unified inference API, with a unified training-data format and deployment scripts across many robots (UR5, Franka, ALOHA, SO-101, Unitree G1). Because Dexbotic is the layer that takes a policy's action output and deploys it onto a specific real robot, it sits exactly where URML's validate-before-actuate gate has a surface: each robot declares a capability manifest (grippers, reach, payload, sensors) and a safety envelope, and URML checks the action is admissible on that specific robot before it reaches the hardware. This is a request for comment.

## The relationship (URML beside Dexbotic)

- **The policy proposes, the deployment gate checks.** The served policy decides the action; URML checks the concrete action is admissible on the concrete robot (within its declared force, reach, mobility, inside the safety envelope) before dispatch. URML does not touch the policy or the training path.
- **A natural fit for a multi-robot deployment layer.** Dexbotic already carries a unified inference API and per-robot deployment scripts; a URML capability manifest is the per-robot declaration such a path could consult, so one gate covers UR5, Franka, ALOHA, SO-101 and the next robot from a single declaration.
- **A neutral layer.** URML is substrate- and model-neutral by construction (the LLM bridge is provider-agnostic). It composes above the served action rather than depending on any policy's internals.

## What is asked

1. Would a per-robot capability + safety-envelope declaration be a useful pre-dispatch guard in the inference/deployment path, given Dexbotic already spans many robots and policies through one unified format?
2. Would a small worked example mapping one deployed policy's action onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #61 VLA / robot-foundation-model wave (open-weight tranche).

## Implementation note

Outreach only. The post is a GitHub Issue on `dexmal/dexbotic` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
