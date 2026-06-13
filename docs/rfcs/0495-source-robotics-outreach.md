---
rfc: 0495
title: Source Robotics (PAROL6 / Faze4) integration — request for comment
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

# RFC-0495: Source Robotics (PAROL6 / Faze4) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44). One RFC for the Source Robotics org, covering both open arms, rather than separate posts.

## Summary

Source Robotics builds popular open desktop robot arms: [`Source-Robotics/PAROL-commander-software`](https://github.com/Source-Robotics/PAROL-commander-software) (the control GUI / SDK for the PAROL6 6-axis desktop cobot) and [`Source-Robotics/Faze4-Robotic-arm`](https://github.com/Source-Robotics/Faze4-Robotic-arm) (a widely-built open 6-axis arm with cycloidal gearboxes). URML is interesting to a desktop arm as the layer above its controller: a "pick that up and place it there" intent becomes a typed primitive, validated against the arm's declared reach, payload, and gripper before any motion. This RFC asks whether the mapping is useful for the PAROL6 / Faze4 platforms.

## The mapping (URML beside PAROL6 / Faze4)

- **Capability manifest.** The arm's joints, reach, payload, and end-effector map onto a URML Layer-1 manifest. `pick_from` / `place_at` / `grasp` are validated against that declared workspace and gripper force limits.
- **Validated intent, then dispatch.** URML turns the intent into a typed primitive, validates it against the manifest and the active safety envelope, then hands the motion to the PAROL commander software (or the Faze4 controller). URML is the typed gate above the controller, not a replacement for it.

## What is asked

Request for comment from the Source Robotics maintainers:

1. Does mapping a PAROL6 / Faze4 arm (reach, payload, gripper) onto a URML manifest read right for a desktop arm?
2. Is a validated pick/place intent layer above the PAROL commander interesting for the desktop-cobot audience?
3. Which is the cleaner first seam, and which platform (PAROL6 or Faze4) is the better place to start?

Nothing here asks the project to adopt, host, or maintain anything. (The PAROL commander is GPL-3.0 and the Faze4 hardware is CERN-OHL; this RFC proposes no code reuse, only a capability-manifest mapping and an optional adapter.)

## Prior art / context

URML's manipulation primitives (`pick_from` / `place_at` / `grasp`, the industrial profile RFC-0013) and the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a single GitHub Issue on `Source-Robotics/PAROL-commander-software` (the active control SDK, referencing Faze4) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
