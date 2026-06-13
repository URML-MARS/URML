---
rfc: 0502
title: mc_rtc integration — request for comment
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

# RFC-0502: mc_rtc integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`jrl-umi3218/mc_rtc`](https://github.com/jrl-umi3218/mc_rtc) (BSD-2-Clause, ~183 stars, active, JRL Japan-France joint lab) is a real-time control interface for simulated and real robots, built around a whole-body QP and a finite-state-machine controller. URML is interesting one layer above mc_rtc: a high-level intent is turned into a typed primitive, validated against the robot's declared whole-body structure and a safety envelope, then handed to mc_rtc as the goal its QP and FSM execute. This RFC asks whether the seam is useful.

## The mapping (URML beside mc_rtc)

- **Capability + whole-body manifest.** The robot mc_rtc controls declares its kinematic structure and stability limits as a URML `whole_body` manifest (RFC-0384), plus its manipulators. URML validates an intent against that before anything is commanded.
- **Validated goal, then control.** URML is the decide layer (typed intent, validated against capabilities + envelope); mc_rtc is the do layer (the real-time QP/FSM that realizes the goal). URML adds the typed, checkable gate above the controller; it does not re-implement the control.

## What is asked

Request for comment from the mc_rtc maintainers:

1. Does a URML `whole_body` manifest fit how mc_rtc models a robot's structure and limits?
2. Is a validated-intent layer that hands goals to mc_rtc's QP/FSM interesting, or already covered by the FSM-state interface?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `whole_body` declaration (RFC-0384), the whole-body / bimanual manipulation model (RFC-0010), and the decide-then-do split (RFC-0002). Part of Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `jrl-umi3218/mc_rtc` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
