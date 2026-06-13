---
rfc: 0496
title: The BiMo Project integration — request for comment
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

# RFC-0496: The BiMo Project integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`mekion/the-bimo-project`](https://github.com/mekion/the-bimo-project) (Apache-2.0, ~155 stars, active) is an open bipedal-robot platform: 3D-printable, with a clean Python API and an Isaac Lab sim-to-real workflow. URML is interesting to BiMo in two complementary ways: as the validated-intent layer above its Python API (a typed command checked against the biped's declared structure and balance envelope), and as the place a sim-trained policy declares the domain it was trained in so a deployment can be validated against it. This RFC asks whether either is useful.

## The mapping (URML beside BiMo)

- **Capability manifest + validated intent.** The biped's kinematic structure and balance limits map onto a URML `whole_body` declaration (RFC-0384) plus a `mobility` block; a locomotion intent is validated against that envelope before it reaches the Python API (the decide-then-do split).
- **Sim-to-real envelope (optional).** BiMo's Isaac Lab workflow trains policies in a simulated domain. URML's `LearnedPolicy` declaration (RFC-0383) lets a trained policy carry the observation/action spaces and training-domain bounds it learned, so the validator can refuse to dispatch it outside the domain it was trained for. This is the sim-to-real boundary made checkable.

## What is asked

Request for comment from the BiMo maintainers:

1. Does a URML manifest for the biped (`whole_body` structure + balance envelope) read right, and does a validated-intent layer above the Python API fit?
2. For the Isaac Lab sim-to-real side, is a declared training envelope (the sim domain a policy must stay within on the real biped) useful?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `whole_body` declaration (RFC-0384), the `LearnedPolicy` training envelope (RFC-0383), and the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `mekion/the-bimo-project` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
