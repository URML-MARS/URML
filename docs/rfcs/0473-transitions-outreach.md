---
rfc: 0473
title: transitions (pytransitions) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0473: transitions (pytransitions) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition and Python reference tooling. Tier B (general-purpose, not robotics-native).

## Summary

[`pytransitions/transitions`](https://github.com/pytransitions/transitions) (MIT, ~6.5k stars, active) is the canonical lightweight Python finite-state-machine library (hierarchical + async variants). It is not robotics-specific, but it is what a great many Python robot stacks reach for when they need an FSM, which makes it a natural, low-friction target for "a validated URML program lowered to a transitions state machine." This RFC asks whether that lowering is sound.

## The mapping (URML lowered to a transitions FSM)

URML sits above the FSM library as a validated-intent layer:

- A validated URML program's control flow lowers to a `transitions` machine: sequence → ordered states, branch → conditional transitions, retry → a self-loop transition with a guard. URML primitives are dispatched from `on_enter` callbacks.
- URML supplies what a bare FSM does not: the typed args, the capability match against the manifest, and the safety-envelope check — all verified before the machine starts stepping.
- Because both URML's reference tooling and transitions are Python, the adapter is a small, dependency-light module.

## What is asked

Request for comment from the transitions maintainers:

1. Is "URML validated program → a transitions FSM" a sensible lowering, and does HSM (hierarchical) cover URML's nested sequence/branch?
2. What callback shape (`on_enter` per state) is idiomatic for dispatching a validated action?
3. Is there interest in a small reference adapter, or is this better left as a downstream example?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002) and Python reference tooling; the behavior-tree anchor (RFC-0470); the SMACC2 robotics-FSM engagement (RFC-0472). transitions is the general-purpose-Python-FSM vertex of the orchestration wave (Tier B; cross-domain).

## Implementation note

Outreach only. The post is a GitHub Discussion on `pytransitions/transitions` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move41.yaml`.
