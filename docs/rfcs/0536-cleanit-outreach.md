---
rfc: 0536
title: CleanIt integration — request for comment
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

# RFC-0536: CleanIt integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48), service robotics.

## Summary

[`Sollimann/CleanIt`](https://github.com/Sollimann/CleanIt) (MIT, active, Norway) is open-source autonomy software in Rust + gRPC for Roomba-series vacuums. URML is interesting as the natural-language front door above a service robot's autonomy: "clean the kitchen", "go home" become typed primitives validated against the robot's declared mobility and a safety envelope. The Rust core also aligns with URML's preference for Rust in long-running infrastructure. This RFC asks whether the mapping is useful.

## The mapping (URML beside CleanIt)

- **Service-robot intent, validated.** The vacuum's mobility and named areas map onto a URML manifest; a cleaning / navigation intent is validated against it and a safety envelope before dispatch to CleanIt's autonomy.
- **NL front door over gRPC.** URML produces the validated intent; CleanIt's gRPC autonomy executes it. URML adds the typed intent and the capability/envelope gate.

## What is asked

Request for comment from the CleanIt maintainer:

1. Does mapping a vacuum's mobility + named areas onto a URML manifest fit?
2. Is an English-to-validated-intent front door above CleanIt's autonomy interesting for service robots?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `mobility` block, named locations, the decide-then-do split (RFC-0002), and URML's Rust preference for infrastructure (per CLAUDE.md). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `Sollimann/CleanIt` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
