---
rfc: 0394
title: JPL Open Source Rover integration — request for comment (education / demo)
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

# RFC-0394: JPL Open Source Rover integration — request for comment (education / demo)

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its education examples.

## Summary

The [JPL Open Source Rover](https://github.com/nasa-jpl/open-source-rover) (Apache-2.0, ~9.4k stars) is a build-it-yourself 6-wheel Mars-style rover, used widely in classrooms and maker spaces. URML's headline is "one English sentence makes a robot move," validated before it actuates — a natural, approachable teaching layer on top of an educational rover. This RFC pitches that education/demo angle and asks the maintainers whether it is of interest.

## The mapping (URML as a teaching layer)

URML sits above the rover's software as a validated intent layer:

- A learner writes "drive to the rock and take a photo"; URML turns it into typed `move_to` / `capture` primitives, validates them against the rover's declared capability manifest and a safety envelope, and dispatches to the rover's ROS surface. The validation step is itself a teaching moment: the manifest makes "what can this robot do" explicit and inspectable.
- The loop is hermetic-first (URML's mock substrate runs the whole language → validation → execution pipeline with no hardware), so a classroom can use it before a physical rover exists, then point the same program at the real one.
- This is an education engagement, not a flight-software one: the value is pedagogical clarity, not operational rigor.

## What is asked

Request for comment from the Open Source Rover maintainers:

1. Is a validated natural-language intent layer interesting as a teaching add-on for the rover community?
2. What would make a URML manifest for the rover most useful in a classroom (a ready-made manifest shipped as an example, a tutorial)?
3. Is there interest in a small "one sentence drives the rover" demonstration contributed as a community example?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the education examples and tutorials (`examples/educational/`, the Move #19 education wave). The Open Source Rover is the education/maker vertex of the space wave; the framing leads with pedagogy because the platform's audience is learners.

## Implementation note

Outreach only. The post is a GitHub Discussion on `nasa-jpl/open-source-rover` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move31.yaml`.
