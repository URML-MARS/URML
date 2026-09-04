---
rfc: 0697
title: ARMOUR (roahmlab/armour) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-04
updated: 2026-09-04
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

# RFC-0697: ARMOUR (roahmlab/armour) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the Move #73 wave (follow-on).

## Summary

[`roahmlab/armour`](https://github.com/roahmlab/armour) (ROAHM Lab, University of Michigan) is a reachability-based trajectory optimization method that produces provably-safe manipulation trajectories by accounting for uncertainty in real time. It is the closest thing to URML's own discipline reached from the other direction: ARMOUR *certifies a trajectory as safe before it is executed*, and URML *validates an intent as admissible before it is dispatched*. This is a request for comment on whether a lightweight declarative layer and a heavyweight reachability certificate are complementary.

## The relationship (URML beside ARMOUR)

- **Same goal, different weight class.** ARMOUR derives a strong, formal guarantee: a reachable-set certificate that the planned motion stays safe under uncertainty. URML does a cheap, declarative, static admissibility check: a robot declares a capability manifest (joint limits, reachable workspace, payload, force) and a safety envelope, and URML refuses an intent that falls outside them before dispatch. The URML check is portable across substrates and necessary, not sufficient; it does not replace a reachability certificate.
- **Consume-the-trajectory, validate admissibility.** ARMOUR decides the motion; URML checks the resulting trajectory is admissible on the specific arm and inside the declared envelope before it runs. URML is not a source of planning constraints and does not reason about reachable sets; it is the portable pre-dispatch gate around the planner.
- **A possible portable front-end.** A declarative capability + envelope manifest could act as a portable, human-readable declaration that sits in front of an ARMOUR-planned motion, so the same declared intent travels across arms while ARMOUR provides the deep certificate underneath.
- **Neutral by construction.** URML is substrate- and model-neutral, cross-cites only (ARMOUR is GPL-3.0; no code is reused and no license question is raised).

## What is asked

1. Is a lightweight, declarative capability + envelope check a useful complement to a reachability-based safety certificate, or does the certificate already subsume it in your view?
2. Would a small worked example validating an ARMOUR-planned trajectory against a URML manifest (admissibility only, no execution) be worth comparing notes on?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. The closest conceptual sibling is the formal-safety framing in RFC-0678 (Safe-ROS): a lightweight declarative check beside a heavyweight formal method. Part of the Move #73 wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `roahmlab/armour` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move73.yaml`.
