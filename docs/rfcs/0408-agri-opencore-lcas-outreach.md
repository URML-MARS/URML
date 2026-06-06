---
rfc: 0408
title: Agri-OpenCore / L-CAS integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0408: Agri-OpenCore / L-CAS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, the simulation-fidelity hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)), and the manipulation work ([RFC-0010](0010-whole-body-bimanual-manipulation.md)). It anchors a single engagement on the L-CAS agri cluster rather than posting to each repo.

## Summary

[`aoc_tomato_farm`](https://github.com/LCAS/aoc_tomato_farm) (Apache-2.0, Issues enabled, ROS 2 Humble) is a tomato-glasshouse digital-twin generator and simulator from the Lincoln Centre for Autonomous Systems (L-CAS) / Agri-OpenCore — the most active academic agri-robotics ecosystem found, alongside the lab's GNSS drivers, crop-monitoring (`Qualicrop`), and mobile-manipulator (`hunter_with_arm`) stacks. It is a ROS 2 ag environment a URML-validated command can drive, and the lab is a high-value research engagement. This RFC asks whether a validated intent layer above the Agri-OpenCore stack is interesting.

## The mapping (URML above the Agri-OpenCore stack)

URML sits above the lab's ROS 2 stack as a validated intent layer:

- URML's ROS 2 runtime targets the `aoc_tomato_farm` digital twin and the lab's field/glasshouse robots directly; a "inspect row 4 and report ripe tomatoes" intent lowers onto the ROS 2 surface.
- URML's `validation` block (RFC-0381) records the simulation-fidelity context the glasshouse digital twin makes concrete; the lab's mobile-manipulator work (`hunter_with_arm`) is where URML's manipulation primitives (RFC-0010) would exercise harvesting intent.
- Validate-before-actuate refuses an out-of-capability request before dispatch — useful across a heterogeneous research fleet.

## What is asked

Request for comment from the L-CAS / Agri-OpenCore maintainers:

1. Is a validated natural-language intent layer above the Agri-OpenCore stack interesting for the lab's glasshouse / field robotics?
2. What should a URML capability manifest declare to describe a glasshouse or field agri-robot honestly (drive type, row/bench geometry, crop vocabulary, manipulator reach for harvesting, GNSS)?
3. Where is the cleanest seam — the `aoc_tomato_farm` digital twin for a demonstration, or a specific platform repo?

Nothing here asks L-CAS to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation`); RFC-0010 (manipulation, for harvesting); the broader L-CAS org (`Qualicrop`, GNSS drivers, `hunter_with_arm`) referenced rather than posted to separately (org-anchor courtesy). Agri-OpenCore is the academic-ecosystem vertex of the agriculture wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `LCAS/aoc_tomato_farm` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Sibling L-CAS repos are referenced, not posted to separately. Tracked in `examples/lighthouses/outreach-move33.yaml`.
