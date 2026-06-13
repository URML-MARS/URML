---
rfc: 0537
title: Roomi integration — request for comment
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

# RFC-0537: Roomi integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48), service + manipulation.

## Summary

[`jadechoghari/roomi`](https://github.com/jadechoghari/roomi) (Apache-2.0, active, US) is an open autonomous cleaning / housekeeping robot: a mobile base with dual arms and multi-camera sensing, spanning hardware, firmware, and sim. URML is interesting as the validated-intent layer above a mobile-manipulation service robot, where the dual arms tie directly to URML's bimanual model. This RFC asks whether the mapping is useful.

## The mapping (URML beside Roomi)

- **Mobile manipulation, declared.** Roomi's mobile base and two arms map onto a URML manifest: mobility plus `manipulation.arms` (per-arm), so a "tidy this surface" task is a composition of `move_to` and arm primitives, including coordinated two-arm work via the `bimanual` primitive (RFC-0010). Each step is validated against the manifest and safety envelope.
- **Apache-2.0 enables an adapter.** A `RoomiAdapter` against the published stack is the established URML pattern.

## What is asked

Request for comment from the Roomi maintainer:

1. Does mapping Roomi (mobile base + dual arms + cameras) onto a URML manifest (`mobility` + `manipulation.arms` + `bimanual`) read right?
2. Is a validated mobile-manipulation intent layer above the stack interesting for a housekeeping robot?
3. Which is the cleaner first seam — the manifest mapping, or a `RoomiAdapter`?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's whole-body / bimanual manipulation model (RFC-0010), the mobile-manipulation engagements (Move #35), and the decide-then-do split (RFC-0002). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `jadechoghari/roomi` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
