---
rfc: 0675
title: UniVLA (OpenDriveLab/UniVLA) integration — request for comment
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

# RFC-0675: UniVLA (OpenDriveLab/UniVLA) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It continues the VLA / robot-foundation-model wave (Move #61).

## Summary

[`OpenDriveLab/UniVLA`](https://github.com/OpenDriveLab/UniVLA) is a generalist policy that plans in a unified, embodiment-agnostic latent action space and is then post-trained and decoded to a specific embodiment for deployment (real-world arm experiments, LIBERO, CALVIN). That decode-from-agnostic-to-concrete step is exactly where a per-embodiment admissibility check fits: the specific robot declares a capability manifest and a safety envelope, and URML checks the decoded concrete action is admissible on that robot before execution. This is a request for comment.

## The relationship (URML beside UniVLA)

- **Agnostic action, concrete gate.** UniVLA's strength is planning in an embodiment-agnostic action space; when that action is decoded onto a particular robot, URML checks the concrete action fits that robot's declared force, reach, and mobility, inside its safety envelope, before dispatch. URML does not touch the latent-action learning; it gates the concrete result.
- **A complement, not a constraint.** An embodiment-agnostic policy still needs the concrete action to be admissible on the embodiment that runs it; a declared per-embodiment capability + envelope is the natural place that check lives.
- **A neutral layer.** URML is substrate- and model-neutral (the LLM bridge is provider-agnostic). It composes above the decoded action rather than depending on the policy's internals.

## What is asked

1. At the decode-to-embodiment step, would a declared per-embodiment capability + safety envelope be a useful admissibility check on the concrete action?
2. Would a small worked example mapping a decoded UniVLA action onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #61 VLA / robot-foundation-model wave (open-weight tranche).

## Implementation note

Outreach only. The post is a GitHub Issue on `OpenDriveLab/UniVLA` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
