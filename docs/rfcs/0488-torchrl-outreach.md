---
rfc: 0488
title: TorchRL integration — request for comment
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

# RFC-0488: TorchRL integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and its decide-then-do split (RFC-0002). Part of the reinforcement-learning / policy-training wave (Move #43).

## Summary

[`pytorch/rl`](https://github.com/pytorch/rl) (TorchRL, MIT, ~3.5k stars, very active, PyTorch project) is a modular, primitive-first RL library. Its `TensorSpec` types describe observation and action specs precisely, which is a natural match for URML's typed view of the world: a TorchRL policy's specs are most of what a URML `LearnedPolicy` deployment envelope (RFC-0383) wants to carry. The "primitive-first" design philosophy also rhymes with URML's own small-vocabulary stance. This RFC asks whether the mapping is useful.

## The mapping (URML beside TorchRL)

- **Spec to envelope.** A TorchRL policy carries `TensorSpec` observation/action specs (bounds, shapes, dtypes). Those map almost directly onto a URML `LearnedPolicy` envelope: the obs/action ranges and the training-domain bounds a deployment must stay inside. The export is a thin adapter from `TensorSpec` to the URML declaration.
- **Validated deployment.** With the envelope declared, URML is the typed gate between the trained policy and the robot: each proposed action is checked against the robot's declared capabilities and the active safety envelope before dispatch (decide-then-do). The policy decides; URML does.

## What is asked

Request for comment from the TorchRL maintainers:

1. Does mapping a policy's `TensorSpec` observation/action specs onto a declared deployment envelope make sense as an optional export?
2. Is the validated-deployment gate (action checked against declared capabilities + envelope before dispatch) interesting for the robot-deployment side of TorchRL?
3. Which is the cleaner first seam — the spec-to-envelope export, or the deployment gate?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The VLA / robot-learning engagements (Moves #11, #38) at the foundation-model layer; this is the general-purpose RL layer below. Sibling RFC-0485 anchors Move #43.

## Implementation note

Outreach only. The post is a GitHub Discussion in the **Ideas** category on `pytorch/rl` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move43.yaml`.
