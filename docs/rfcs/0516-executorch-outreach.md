---
rfc: 0516
title: ExecuTorch integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0516: ExecuTorch integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the AI / robot-learning wave (Move #46).

## Summary

[`pytorch/executorch`](https://github.com/pytorch/executorch) (BSD, ~4.7k stars, very active, PyTorch Foundation) runs PyTorch models on-device across mobile, embedded, and edge targets — including the edge compute a robot carries to run a learned policy. URML is interesting one layer above the inference runtime: ExecuTorch executes the policy on-device; URML validates the action the policy proposes against the robot's declared capabilities and a safety envelope before it is dispatched. This RFC asks whether the seam is worth describing.

## The mapping (URML beside ExecuTorch)

- **On-device inference, then the gate.** A policy deployed to a robot's edge compute runs under ExecuTorch. The action it produces is then checked by URML against the robot's declared capabilities and the active safety envelope before dispatch (the decide-then-do split). ExecuTorch is the runtime that computes the action; URML is the typed gate that decides whether to dispatch it.
- **The policy's declared envelope.** The model ExecuTorch runs has the observation/action spaces and training domain a URML `LearnedPolicy` declaration (RFC-0383) records, so the on-device policy carries the bounds the gate enforces.

## What is asked

Request for comment from the ExecuTorch maintainers:

1. Is "ExecuTorch runs the policy on-device, URML validates the action before dispatch" a sensible description of the layering for a robot?
2. Is a `LearnedPolicy` envelope traveling with an on-device model useful for the robotics-deployment case?
3. Which is the cleaner first seam, and is this the right altitude (an inference runtime) to engage?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383), the decide-then-do split (RFC-0002), and the on-device-LLM / edge engagements (RFC-0021 and the MCU-substrate work). Part of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `pytorch/executorch` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
