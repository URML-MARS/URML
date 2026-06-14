---
rfc: 0572
title: GoPiGo3 integration — request for comment
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

# RFC-0572: GoPiGo3 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52).

## Summary

[`DexterInd/GoPiGo3`](https://github.com/DexterInd/GoPiGo3) is the driver and API for the GoPiGo3, a popular Raspberry Pi based educational robot. URML is a small, Apache-2.0 language for robot intent: an English instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. A simple, well-defined educational robot is an ideal place to show the natural-language-to-validated-intent path end to end. This RFC asks whether the mapping is useful.

## The mapping (URML beside GoPiGo3)

- **An English front door for a beginner robot.** The GoPiGo3 has a small, clear set of capabilities (drive, turn, sensors). That maps cleanly onto a URML capability manifest, so "drive forward two metres, then stop if you see an obstacle" can become a typed, validated intent and then GoPiGo3 API calls. URML adds the typed validation and the English layer; the GoPiGo3 API stays the runtime.
- **A teaching artifact.** For a learner, seeing an instruction become a checked plan, and seeing why an impossible instruction is rejected, is exactly the kind of thing a small platform makes vivid.

## What is asked

Request for comment from the GoPiGo3 maintainers:

1. Is an English-to-validated-intent front door useful for a beginner educational robot like the GoPiGo3?
2. Does the GoPiGo3's capability set map cleanly onto a URML capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the capability manifest, the five-pass validator, and the educational profile (RFC-0011). Part of Move #52; the beginner Raspberry-Pi-robot target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `DexterInd/GoPiGo3` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the license is non-standard / unrecognized by GitHub; state that, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move52.yaml`.
