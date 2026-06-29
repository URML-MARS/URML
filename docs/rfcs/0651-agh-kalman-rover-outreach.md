---
rfc: 0651
title: AGH Space kalman_robot (agh-space-systems-rover/kalman_robot) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-29
updated: 2026-06-29
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

# RFC-0651: AGH Space kalman_robot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #65 (domain-vertical lane).

## Summary

[`agh-space-systems-rover/kalman_robot`](https://github.com/agh-space-systems-rover/kalman_robot) (AGH Space Systems, Krakow) is the autonomy software for a planetary-analogue rover: navigation, manipulation, and the action selection that drives the platform across terrain. URML is a small Apache-2.0 language for declaring what a robot can do and checking an intended action against that declaration before it runs. A rover is a fitting case, because power and terrain bound what is admissible at any moment, and the loop that decides the next action benefits from a separate check that the action is within those bounds.

## The relationship (URML beside kalman_robot)

The rover's autonomy decides where to go and what to do; URML answers whether the chosen action is admissible given the declared envelope: drive limits, manipulation reach, and a power-state or terrain constraint the mission declares. The check sits between action selection and the drivers, and leaves the perception and the decision loop untouched.

URML does not navigate, plan, or estimate state. It declares the rover's envelope and confirms a selected action is inside it before dispatch. The planetary-analogue setting, where a wrong action is costly and oversight is intermittent, is exactly where a static pre-dispatch check earns its place.

## What is asked

1. For a rover autonomy stack, is a declared drive-and-manipulation-and-power envelope check on a selected action useful before dispatch, or is feasibility already guaranteed inside action selection?
2. Would a small worked example mapping a rover action onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a planetary-analogue rover autonomy stack. MIT; AGH Space Systems (student space-robotics team), Poland. Part of Move #65.

## Implementation note

Outreach only. The post is a GitHub Issue on `agh-space-systems-rover/kalman_robot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move65.yaml`.
