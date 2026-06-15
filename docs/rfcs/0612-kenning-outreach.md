---
rfc: 0612
title: Kenning integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-15
updated: 2026-06-15
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

# RFC-0612: Kenning integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the edge-AI / on-robot-inference wave (Move #58).

## Summary

[`antmicro/kenning`](https://github.com/antmicro/kenning) (Apache-2.0, Antmicro) is a framework for deploying and optimizing edge-AI models, with ROS 2 computer-vision node support across runtimes (ONNX, TFLite, TVM). It is the layer that gets a model running efficiently on a robot's compute; URML is the layer above the model's output that turns a perception or policy result into a validated action. This RFC asks where the two meet.

## The relationship (URML beside Kenning)

- **Kenning deploys the inference; URML gates the action it informs.** Kenning optimizes and runs the model on the edge device. URML consumes the model's output (a detection, a policy decision) as a fact a typed intent conditions on, validated against the robot's capabilities and a safety envelope before dispatch. Kenning keeps the deployment and optimization; URML stays out of inference.
- **A deployed model that carries an envelope.** Kenning produces a deployed, optimized model artifact. URML's LearnedPolicy direction (RFC-0383) is the idea that such an artifact could carry the operating envelope it is valid within, so an intent that relies on it is checked against that envelope. For an edge deployment where the model is quantized or optimized, knowing the envelope it still holds for is genuinely useful.

## What is asked

1. Is a typed, validated action layer downstream of a Kenning-deployed model (the action checked against the robot's capabilities + envelope, then dispatched) useful?
2. Could a deployed/optimized model artifact carry an operating envelope a URML intent is checked against (RFC-0383)?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's consume-the-estimate framing (Move #25), the LearnedPolicy envelope (RFC-0383), and the safety-envelope validation. Part of Move #58; the edge-AI deployment framework of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `antmicro/kenning` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move58.yaml`.
