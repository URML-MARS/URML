---
rfc: 0482
title: Open-TeleVision integration — request for comment
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

# RFC-0482: Open-TeleVision integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validated-intent layer.

## Summary

[`OpenTeleVision/TeleVision`](https://github.com/OpenTeleVision/TeleVision) (Apache-2.0, ~1273 stars) is an immersive VR teleoperation system with active visual feedback (CoRL 2024), widely used for bimanual and humanoid demonstration collection. URML is interesting to it as a validated shared-autonomy layer the immersive operator can hand off to, and as a typed schema for the demonstrated intent recorded with the stereo stream. This RFC asks whether either is useful.

## The mapping (URML beside Open-TeleVision)

Two complementary seams:

- **Shared-autonomy handoff.** Inside the immersive session the operator can issue a high-level command; URML validates it against the robot's declared capabilities and safety envelope, then dispatches, with full teleop as the correction path. URML adds a capability/envelope gate around the autonomy a raw immersive stream lacks.
- **Typed-intent annotation.** A demonstration is labelled with the URML primitives it realizes, so an immersive bimanual demo carries validatable typed intent next to the video — relevant since URML already models bimanual manipulation (an `arm` selector + a `bimanual` primitive).

## What is asked

Request for comment from the Open-TeleVision maintainers:

1. Is a validated shared-autonomy handoff interesting inside an immersive teleop session?
2. Is labelling demonstrations with typed URML intent (including bimanual) useful for the data collected?
3. Which is the cleaner first seam — the handoff, or the annotation?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's validated-intent layer (RFC-0002) and the bimanual manipulation work (RFC-0010); the VLA / robot-learning engagements (Moves #11, #38); the GELLO anchor (RFC-0479). Open-TeleVision is the immersive-VR-teleop vertex of the teleop / data-collection wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `OpenTeleVision/TeleVision` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0; the repo's LICENSE file is Apache-2.0 even though the GitHub classifier shows none). Tracked in `examples/lighthouses/outreach-move42.yaml`.
