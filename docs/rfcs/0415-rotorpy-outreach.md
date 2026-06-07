---
rfc: 0415
title: RotorPy integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0415: RotorPy integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type and the sim-engagement pattern (ties RFC-0381).

## Summary

[`spencerfolk/rotorpy`](https://github.com/spencerfolk/rotorpy) (MIT, ~267 stars, active) is a Python multirotor simulator with realistic aerodynamics, built for education and research at UPenn. A lightweight, hackable Python quad sim is an ideal place to demonstrate a validated natural-language layer before any hardware. This RFC asks whether a URML intent layer above RotorPy is interesting.

## The mapping (URML above RotorPy)

URML sits above the simulated drone as a validated intent layer:

- A URML `aerial` program (take off, fly a path, hover, land) drives a RotorPy vehicle through its Python control interface; URML's optional validation block records the simulation-fidelity context a run was checked in.
- Validate-before-actuate refuses an out-of-envelope request (altitude, speed) before the simulated motors spin — the same safety seam that protects real hardware, shown in a classroom-friendly setting.
- The sim-first posture matches URML's own (the reference runtime ships a mock substrate).

## What is asked

Request for comment from the RotorPy maintainers:

1. Is a validated natural-language intent layer above RotorPy interesting as a teaching / research surface?
2. What should a URML capability manifest declare to describe a simulated multirotor honestly (drive type, altitude/speed limits, control modes)?
3. Is the Python control interface the right seam, or is a higher-level mission API a better fit?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type; the simulation-engagement pattern (RFC-0381); the aerial-autonomy anchor (RFC-0412). RotorPy is the lightweight-Python-sim vertex of the aerial wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `spencerfolk/rotorpy` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move34.yaml`.
