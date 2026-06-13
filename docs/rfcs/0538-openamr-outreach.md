---
rfc: 0538
title: OpenAMR integration — request for comment
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

# RFC-0538: OpenAMR integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48), intralogistics.

## Summary

[`openAMRobot/openamr`](https://github.com/openAMRobot/openamr) (MIT, active, Cyprus / EU) is an affordable modular Autonomous Mobile Robot for SME intralogistics, ROS-based and integrating Open-RMF. URML is interesting at the open-platform altitude (not a closed AMR vendor): a transport task becomes a typed, validated intent, and URML's warehouse vocabulary already covers the cell. This RFC asks whether the mapping is useful.

## The mapping (URML beside OpenAMR)

- **Warehouse intent, zero new vocabulary.** OpenAMR's mobility and the deployment's named locations / occupancy zones map onto a URML manifest under the warehouse profile (RFC-0022). A pick-to-conveyor or transport task is validated against the manifest and a safety envelope before dispatch.
- **Fleet + RMF.** OpenAMR integrates Open-RMF; URML's fleet roster (RFC-0286) and cross-robot deconfliction (RFC-0291) are the static-validation complement to RMF's runtime orchestration, the same framing as the warehouse-interop engagements (Move #21).

## What is asked

Request for comment from the OpenAMR maintainers:

1. Does mapping an OpenAMR (mobility + locations + occupancy zones) onto a URML warehouse-profile manifest read right?
2. Is a validated transport-intent layer (with fleet validation as the RMF complement) interesting for SME intralogistics?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's warehouse profile (RFC-0022), fleet roster (RFC-0286), deconfliction (RFC-0291), and the warehouse-AMR / interop engagements (Move #21: VDA5050, openTCS, InOrbit / Open-RMF). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `openAMRobot/openamr` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
