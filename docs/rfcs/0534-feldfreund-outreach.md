---
rfc: 0534
title: Feldfreund (feldfreund_devkit_ros) integration — request for comment
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

# RFC-0534: Feldfreund (feldfreund_devkit_ros) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48), agriculture.

## Summary

[`zauberzeug/feldfreund_devkit_ros`](https://github.com/zauberzeug/feldfreund_devkit_ros) (MIT, active, Zauberzeug GmbH, Germany) is the ROS 2 control for the Feldfreund autonomous field-weeding platform. URML is interesting as the natural-language front door above the platform: a field task ("weed row 4", "return to charge") becomes a typed primitive, validated against the platform's declared mobility and tool, then dispatched to its ROS 2 stack. This RFC asks whether the mapping is useful.

## The mapping (URML beside Feldfreund)

- **Field task as validated intent.** Feldfreund's mobility (field navigation) and its weeding tool map onto a URML manifest. A field task is validated against that manifest and a safety envelope (the field boundary as a geofence) before dispatch.
- **NL front door, then dispatch.** URML turns a field instruction into the typed primitive and hands the motion / tool action to the Feldfreund ROS 2 stack. URML adds the capability/envelope gate above it.

## What is asked

Request for comment from the Zauberzeug maintainers:

1. Does mapping the Feldfreund platform (field mobility + weeding tool + field-boundary geofence) onto a URML manifest read right?
2. Is an English-to-validated-field-task front door above the ROS 2 stack interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `mobility` block, the safety-envelope geofence model (RFC-0291), the agriculture engagements (Move #33: FarmBot, L-CAS), and the decide-then-do split (RFC-0002). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `zauberzeug/feldfreund_devkit_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
