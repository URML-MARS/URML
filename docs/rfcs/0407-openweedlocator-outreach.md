---
rfc: 0407
title: OpenWeedLocator integration — request for comment
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

# RFC-0407: OpenWeedLocator integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's detect-then-act primitive pattern (`detect` binds a target; an actuation step consumes it) and the validate-before-actuate discipline.

## Summary

[OpenWeedLocator (OWL)](https://github.com/geezacoleman/OpenWeedLocator) (MIT, ~471 stars, Issues + Discussions enabled, active) is a low-cost image-based weed-detection and spot-spray device: a Raspberry Pi detects weeds and fires relays/solenoids to spray them. It is the most-engaged open weeding project, and its detect-then-actuate loop maps cleanly onto URML's decide-then-do model. This RFC asks whether a validated intent layer above OWL is interesting.

## The mapping (URML above OWL)

URML's primitive model is exactly a detect-then-act split, which OWL embodies:

- `detect` (the weed detection) binds a target; an actuation step (the spray) consumes it — the same `detect` -> `grasp($target)` precedent URML uses elsewhere, here `detect` -> spray.
- Validate-before-actuate is the safety point that matters for a sprayer: a spray action outside the declared application envelope (a no-spray zone, a rate cap, an undeclared nozzle) is refused before a relay fires.
- A URML capability manifest would declare what OWL can sense and actuate (detection classes, nozzle/relay configuration, spray-rate limits, exclusion zones), making "spray the weeds but not within 1 m of the crop row" a validatable intent.

## What is asked

Request for comment from the OpenWeedLocator maintainers:

1. Is a validated intent layer above OWL's detect-then-spray loop interesting, or does the existing configuration already cover that need?
2. What should a URML manifest declare to describe a spot-sprayer honestly (detection classes, nozzle/relay configuration, application-rate limits, no-spray exclusion zones)?
3. Where is the cleanest seam — URML above OWL's detection + relay layer, or as a planning layer feeding it?

Nothing here asks OWL to adopt, host, or maintain anything.

## Prior art / context

URML's `detect` primitive and the decide-then-do split (RFC-0002); the manipulation work (RFC-0010) as the general detect-then-actuate precedent. OWL is the perception-plus-actuation device vertex of the agriculture wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `geezacoleman/OpenWeedLocator` (Discussions enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move33.yaml`.
