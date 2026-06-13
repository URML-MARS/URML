---
rfc: 0535
title: OpenExo integration — request for comment
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

# RFC-0535: OpenExo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48), assistive robotics (research scope).

## Summary

[`naubiomech/OpenExo`](https://github.com/naubiomech/OpenExo) (active, Northern Arizona University Biomechatronics) is described as the first comprehensive open-source modular exoskeleton framework (hip / ankle / elbow assistance), published in Science Robotics. It runs on a Teensy / Arduino microcontroller substrate. URML is interesting as a typed, validatable declaration of an assistance intent and the safety envelope it must stay within. This RFC is a research-scope request for comment; it makes no clinical claim.

## The mapping (URML beside OpenExo)

- **Assistance mode as declared intent, bounded by an envelope.** An exoskeleton's assistance configuration (which joint, torque profile, mode) can be expressed as a typed URML declaration, validated against the device's declared actuation capabilities and a safety envelope (torque / range limits) before it is applied. The envelope is the load-bearing part: an assistance command outside the declared safe limits is refused.
- **MCU substrate.** OpenExo's Teensy / Arduino target fits URML's minimal-MCU and `set_output` actuation work (the on-ethos, dependency-free posture).

## What is asked

Request for comment from the OpenExo maintainers:

1. Is a typed, envelope-bounded declaration of an assistance configuration useful for an open exoskeleton (research scope)?
2. Does URML's MCU-substrate / actuation model fit the Teensy / Arduino target?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything, and makes no clinical claim.

## Prior art / context

URML's safety envelope, the minimal-MCU capability subset (RFC-0018) and `set_output` actuation (RFC-0017), and the medical / surgical research engagements (Move #37, research-scope norm). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `naubiomech/OpenExo` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (state the repo's actual license; do not ask). Tracked in `examples/lighthouses/outreach-move48.yaml`.
