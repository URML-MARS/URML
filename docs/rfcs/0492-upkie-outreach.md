---
rfc: 0492
title: Upkie integration — request for comment
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

# RFC-0492: Upkie integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`upkie/upkie`](https://github.com/upkie/upkie) (Apache-2.0, ~370 stars, active) is an open-hardware, open-software wheeled-biped balancing robot that runs its agents in Python and C++ on a Raspberry Pi. URML is interesting to Upkie as the validated-intent layer above its balancing controller: a high-level command ("go to the door", "turn around") becomes a typed primitive, validated against Upkie's declared mobility and balance limits before dispatch, while the balancing loop keeps running underneath. This RFC asks whether the mapping is useful.

## The mapping (URML beside Upkie)

- **Capability manifest.** Upkie's wheeled-biped mobility and its balance envelope (the limits it must stay within to stay upright) map onto a URML manifest: a `mobility` block for locomotion plus a `whole_body` stability declaration (center-of-mass / support bounds, RFC-0384). The manifest says what Upkie can be asked to do and the envelope it cannot leave.
- **Validated intent, then dispatch.** A locomotion intent is checked against those declared limits and the active safety envelope before it reaches the balancing agent (the decide-then-do split). URML is the typed gate; Upkie's controller stays the thing that balances and drives.

## What is asked

Request for comment from the Upkie maintainers:

1. Does declaring Upkie's mobility plus a `whole_body` balance envelope as a URML manifest read right for a wheeled biped?
2. Is a validated-intent gate above the balancing controller (intent checked against the balance envelope before dispatch) interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `mobility` block and the `whole_body` kinematic-structure + stability-limits declaration (RFC-0384), plus the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `upkie/upkie` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
