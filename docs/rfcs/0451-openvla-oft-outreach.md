---
rfc: 0451
title: OpenVLA-OFT integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0451: OpenVLA-OFT integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family and the wrap-a-learned-policy pattern.

## Summary

[`moojink/openvla-oft`](https://github.com/moojink/openvla-oft) (MIT, ~1,240 stars, Discussions on) is OpenVLA-OFT, an optimized fine-tuning recipe for the OpenVLA model (Stanford) that substantially improves speed and success rate. A widely-used VLA fine-tuning project is exactly the kind of learned-policy work URML sits above: a typed intent and a validated envelope around the fine-tuned model's actions. This RFC asks whether that is interesting. (The base OpenVLA repo was engaged separately in an earlier wave; this is the distinct OFT project.)

## The mapping (URML above OpenVLA-OFT)

URML sits above the fine-tuned VLA as a validated intent layer:

- A URML intent declares the goal and the envelope; an OpenVLA-OFT policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts.
- This is the decide-then-do split applied to learning: the fine-tuned model is the actuator, URML is the typed intent and the safety envelope around it.
- Validate-before-actuate refuses an out-of-capability request before motion.

## What is asked

Request for comment from the OpenVLA-OFT maintainer:

1. Is wrapping an OpenVLA-OFT policy in a validated intent layer + envelope interesting?
2. What should a URML capability manifest declare to describe an OFT-driven robot honestly (arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions)?
3. Is the policy/inference interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the earlier VLA wave (Move #11, which engaged the base OpenVLA repo separately). OpenVLA-OFT is the VLA-fine-tuning vertex of the round-2 wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `moojink/openvla-oft` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Distinct from the base `openvla/openvla` engagement (Move #11). Tracked in `examples/lighthouses/outreach-move38.yaml`.
