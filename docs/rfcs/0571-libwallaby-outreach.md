---
rfc: 0571
title: KIPR libwallaby integration — request for comment
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

# RFC-0571: KIPR libwallaby integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52).

## Summary

[`kipr/libwallaby`](https://github.com/kipr/libwallaby) (GPL-3.0) is the robot-control library behind KIPR's Wombat/Wallaby controllers, used in Botball and other educational robotics programs. URML is a small, Apache-2.0 language for robot intent: an instruction (including an English one) becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. This RFC is a consume / front-door note, with no code reuse (libwallaby is GPL-3.0).

## The mapping (URML beside libwallaby)

- **A typed, English-friendly intent layer for student robots.** Students program against libwallaby. URML adds a small layer at the top: a declared intent checked against the robot's declared capabilities before it runs, optionally starting from an English sentence. libwallaby stays the runtime; URML makes the intent and its validation explicit, which suits a teaching context.
- **Cross-citation only.** Given the GPL-3.0 license, this proposes no shared code, only a boundary between a validated intent and the control library that executes it.

## What is asked

Request for comment from the KIPR maintainers:

1. Is a typed, validated intent layer (declare intent, check against capabilities, optionally from English) a useful teaching companion above libwallaby?
2. Does URML's capability manifest map onto how a Wombat/Wallaby robot is configured?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the capability manifest, and the educational profile (RFC-0011). Part of Move #52; the Botball/KIPR educational target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `kipr/libwallaby` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move52.yaml`.
