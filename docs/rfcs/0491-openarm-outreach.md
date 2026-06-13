---
rfc: 0491
title: OpenArm integration — request for comment
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

# RFC-0491: OpenArm integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability manifest and its decide-then-do split. It is the anchor of the open robot-platforms wave (Move #44).

## Summary

[`enactic/openarm`](https://github.com/enactic/openarm) (Apache-2.0, ~2.6k stars, very active) is a fully open-source arm platform for contact-rich physical-AI research, available in single- and dual-arm configurations. URML is interesting to a platform like OpenArm as the layer above its SDK: a person (or a higher-level planner) expresses an intent, URML turns it into a typed primitive, validates it against the arm's declared capabilities and a safety envelope, then dispatches to OpenArm's existing control stack. This RFC asks whether that mapping is useful.

## The mapping (URML beside OpenArm)

- **Capability manifest.** OpenArm's joints, end-effector, reach, and payload become a URML Layer-1 manifest. A bimanual OpenArm declares its two arms via `manipulation.arms` (per-arm gripper), so a command can address `left` / `right` or a named arm, and a coordinated two-arm intent uses URML's `bimanual` primitive (RFC-0010). The single-arm config is the same manifest with one declared arm.
- **Validated intent, then dispatch.** `grasp`, `release`, and a bimanual lift are validated against the declared arms, gripper force limits, and the active safety envelope before anything moves (the decide-then-do split). OpenArm's SDK stays the execution layer; URML adds the typed, checkable gate above it.

## What is asked

Request for comment from the OpenArm maintainers:

1. Does mapping OpenArm's single- and dual-arm configurations onto a URML manifest (`manipulation.arms` + the `bimanual` primitive) read right for how the arms are actually addressed?
2. Is a validated-intent gate above the OpenArm SDK (intent checked against declared arms + force limits + envelope before dispatch) interesting for contact-rich work?
3. Which is the cleaner first seam — the manifest mapping, or the validated-dispatch adapter?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's whole-body / bimanual manipulation model (RFC-0010: `arm` selector + `manipulation.arms` + the `bimanual` primitive) and the decide-then-do split (RFC-0002). OpenArm is the anchor of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `enactic/openarm` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
