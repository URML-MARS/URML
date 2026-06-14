---
rfc: 0587
title: PyLabRobot integration — request for comment
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

# RFC-0587: PyLabRobot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the lab-automation wave (Move #54); PyLabRobot is the cleanest structural fit in the wave.

## Summary

[`PyLabRobot/pylabrobot`](https://github.com/PyLabRobot/pylabrobot) (MIT) is a hardware-agnostic Python SDK for laboratory automation: one command set drives liquid handlers (Hamilton, Tecan, Opentrons), plate readers, pumps, and more, against a structured model of the deck and labware. URML is a hardware-agnostic language for robot intent built on the same instinct: a typed intent, validated against a declared capability manifest and a safety envelope, then dispatched to whatever substrate executes it. The structural overlap is unusually close, which is why this RFC leads the wave.

## The relationship (URML beside PyLabRobot)

- **Two hardware-agnostic layers, one shared idea.** PyLabRobot abstracts many instruments behind a universal command set plus a deck/labware model. URML abstracts many robots behind typed primitives plus a capability manifest. The interesting question is whether PyLabRobot's deck and labware description is, in effect, the lab-automation form of a URML capability manifest, so that a high-level protocol could be validated against what the configured deck can actually do before any command is issued.
- **What URML would add, if anything.** Not a replacement for PyLabRobot's drivers. The candidate contribution is the pre-dispatch validation gate: an instruction (including a natural-language one) becomes a typed protocol step, checked against the deck/labware capabilities and operating limits, and only then handed to PyLabRobot. Whether that gate is useful or redundant with PyLabRobot's own checks is a real question for the maintainers.

## What is asked

1. Is PyLabRobot's deck/labware model close enough to a capability manifest that validating a protocol against it (before dispatch) would be meaningful?
2. Is a typed, statically-validated intent layer (optionally from natural language) a useful thing to sit above PyLabRobot's universal command set, or does the command set already carry the right guarantees?
3. Which boundary, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-1 capability manifest, the five-pass validator, and the decide-then-do split (RFC-0002). Anchor of Move #54; PyLabRobot is the strongest hardware-agnostic-SDK fit found in the 2026-06-14 candidate search.

## Implementation note

Outreach only. The post is a GitHub Issue on `PyLabRobot/pylabrobot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move54.yaml`.
