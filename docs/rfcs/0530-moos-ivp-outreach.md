---
rfc: 0530
title: MOOS-IvP integration — request for comment
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

# RFC-0530: MOOS-IvP integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48).

## Summary

[`moos-ivp/moos-ivp`](https://github.com/moos-ivp/moos-ivp) (MIT, active, MIT) is MOOS-IvP: C++ autonomy modules for marine robots, built around the MOOS middleware and the IvP Helm, which arbitrates between competing behaviors via interval-programming optimization. URML is a conceptual peer at a different layer: it is a declarative, validatable representation of *intent*, which sits above a behavior-arbitration helm. This RFC asks whether the relationship is useful.

## The mapping (URML beside MOOS-IvP)

- **Intent above the helm.** A URML program declares the mission intent for a marine vehicle, validated against the vehicle's declared capabilities and a safety envelope; the IvP Helm then arbitrates the behaviors that realize it. URML is the typed declaration of what should happen; IvP is the runtime arbitration of how.
- **A vehicle manifest.** The ASV/AUV's mobility (a marine `drive_type`) and operating limits map onto a URML manifest, so the declared intent is checkable before it reaches the helm.

## What is asked

Request for comment from the MOOS-IvP maintainers:

1. Is "URML declares the validated mission intent, the IvP Helm arbitrates the behaviors" a sensible layering for a marine vehicle?
2. Does a URML marine-vehicle manifest fit how MOOS-IvP models a platform's capabilities and limits?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything. (This proposes no code reuse, only a layering / conceptual-peer relationship.)

## Prior art / context

URML's behavior composition, the marine runtime and `drive_type` (the BlueROV / ArduSub work), and the decide-then-do split (RFC-0002). Part of Move #48; MOOS-IvP is a behavior-arbitration conceptual peer.

## Implementation note

Outreach only. The post is a GitHub Issue on `moos-ivp/moos-ivp` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (state the actual license from the repo; do not ask). Tracked in `examples/lighthouses/outreach-move48.yaml`.
