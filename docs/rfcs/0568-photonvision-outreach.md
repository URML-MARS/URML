---
rfc: 0568
title: PhotonVision integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0568: PhotonVision integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52).

## Summary

[`PhotonVision/photonvision`](https://github.com/PhotonVision/photonvision) (GPL-3.0) is a free vision-processing solution widely used in FRC and FTC for tag and target detection and pose estimation. URML does not do vision; it consumes the estimate. A pose or detection from PhotonVision is exactly the kind of fact a URML intent can condition on and validate against before acting. This RFC is a consume-the-estimate note, with no code reuse (PhotonVision is GPL-3.0).

## The mapping (URML beside PhotonVision)

- **URML consumes the estimate; it does not produce it.** PhotonVision delivers a pose or target estimate. URML treats that as an input fact: an intent ("align to the tag, then place") can be expressed, validated against the robot's capabilities and a safety envelope, and conditioned on the estimate PhotonVision provides. URML stays out of perception entirely.
- **Cross-citation only.** Given the GPL-3.0 license, this proposes no shared code, only a clean boundary between a vision estimate and a validated intent that uses it.

## What is asked

Request for comment from the PhotonVision maintainers:

1. Is "PhotonVision produces the estimate, URML consumes it as a fact an intent conditions on" a sensible boundary?
2. Does a typed, validated intent layer that conditions on a vision estimate fit how teams use PhotonVision?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's "URML doesn't do perception, it consumes your estimate" framing (Move #25), the capability manifest, and the safety-envelope validation. Part of Move #52; the perception target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `PhotonVision/photonvision` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move52.yaml`.
