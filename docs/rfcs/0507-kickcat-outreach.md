---
rfc: 0507
title: KickCAT (EtherCAT) integration — request for comment
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

# RFC-0507: KickCAT (EtherCAT) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`leducp/KickCAT`](https://github.com/leducp/KickCAT) (CeCILL-C, ~150 stars, active) is an open-source C++ EtherCAT master/slave stack. EtherCAT is the fieldbus beneath the actuation layer in many industrial and legged systems. URML sits well above the bus: it validates an intent against the robot's declared capabilities and a safety envelope, and the validated actuation reaches the drives over a fieldbus master like KickCAT. This RFC asks whether the seam is worth describing.

## The mapping (URML beside KickCAT)

- **Below URML's Layer-1 HAL.** URML's actuation primitives are validated statically; the realized motion reaches the servo drives over EtherCAT. KickCAT is a fieldbus master in that path. URML is the typed, pre-dispatch-validated intent; KickCAT is the deterministic transport to the drives. This mirrors URML's existing `ros2_control` HAL-seam mapping (RFC-0319), one layer lower.
- **No spec coupling.** URML declares the actuation intent and its limits; the fieldbus master executes the cyclic exchange. The two are cleanly separable.

## What is asked

Request for comment from the KickCAT maintainer:

1. Is "URML validates actuation intent above, KickCAT carries it to the drives over EtherCAT" an accurate description of the layering?
2. Is this the right altitude to engage (a fieldbus master), or is the integrator/ros2_control layer the better seam?
3. Which first seam, if any, is worth pursuing?

Nothing here asks the project to adopt, host, or maintain anything. (KickCAT is CeCILL-C; this RFC proposes no code reuse, only a layering description.)

## Prior art / context

URML's Layer-1 HAL, the `ros2_control` seam (RFC-0319), and the actuation-control engagements (Move #23: ros2_control / ethercat_driver_ros2 / ros2_canopen). Part of Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `leducp/KickCAT` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is CeCILL-C; state it, do not ask). Tracked in `examples/lighthouses/outreach-move45.yaml`.
