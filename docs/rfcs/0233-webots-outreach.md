---
rfc: 0233
title: Webots (open robot-simulation substrate) integration, request for comment from Cyberbotics / Webots maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0233: Webots (open robot-simulation substrate) integration

## Summary

URML does not yet ship a Webots manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Webots-simulated robots over [`cyberbotics/webots`](https://github.com/cyberbotics/webots) (Apache-2.0), and **requests review and feedback from the Cyberbotics / Webots maintainers**. No spec change.

**This is a Move-18 frame-break RFC that closes a real gap rather than opening a new frontier.** URML has engaged Gazebo (RFC-0037), NVIDIA Isaac (RFC-0050), CARLA (RFC-0051), and MuJoCo (RFC-0060, RFC-0144), but never Webots, one of the most widely used open-source robot simulators and the cleanest Apache-2.0 surface among them. The frame-break is noticing the omission.

## Motivation

Webots is a mature, Apache-2.0, cross-platform robot simulator with a large library of robot and sensor models and controllers in C, C++, Python, Java, and MATLAB. Repo at [`cyberbotics/webots`](https://github.com/cyberbotics/webots) (Apache-2.0, 4.4k stars, Issues enabled, last commit 2026-05-28, **not archived**).

URML benefits from documenting the Webots manifest mapping because:

1. **It completes URML's open-simulator coverage.** Engaging Gazebo, Isaac, CARLA, and MuJoCo but not Webots is an inconsistency. A venture-scale "works everywhere" claim should not skip a flagship open simulator.
2. **It is the cleanest sim-substrate license fit.** Webots is Apache-2.0 end to end, which composes with URML's stance better than the mixed licenses elsewhere in the sim set.
3. **A simulated demo is the most reproducible URML demo.** Webots runs hermetically on any OS with no robot hardware, which matches URML's MockROSAdapter and bootstrap posture for the "one sentence to motion" hero path.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `webots_sim_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to Webots attribute |
|---|---|
| `name` | Deployment / world handle (`webots_epuck`, `webots_tiago_world`, etc.) |
| `substrate.simulator: custom` (`webots`) | Declares Webots as the simulation substrate (no v0.1 enum entry; Spec RFC queued, shared with the sim set) |
| `mobility.drive_type` | The simulated robot's class (Webots is robot-agnostic; e.g. `differential` for e-puck, `biped` for a humanoid PROTO) |
| Robot model | Webots PROTO node as the upstream-declared robot inventory URML cross-references |
| Compile target | A Webots controller (Python the natural first target) bound to the robot node |

### What URML v0.1 does not yet express for Webots

1. **Simulation-substrate declaration.** URML's manifest has no `substrate.simulator` enum entry. This is the same gap surfaced by the prior sim RFCs (Gazebo / Isaac / CARLA / MuJoCo); Webots reinforces a shared queued Spec RFC.
2. **Sim-versus-real deployment context.** A manifest validated against a Webots model and against the physical robot are the same capability but different deployment contexts; URML has no field to declare which is active.
3. **PROTO model cross-reference.** Webots robots are declared as PROTO nodes; URML's manifest cannot today reference a specific PROTO as the simulated platform.

### Compatibility notes

- **Vendor.** [`cyberbotics`](https://github.com/cyberbotics) — Cyberbotics Ltd (Switzerland, EPFL lineage). Open-sourced Webots under Apache-2.0 in 2018.
- **Engagement repo.** [`cyberbotics/webots`](https://github.com/cyberbotics/webots) — Apache-2.0, 4.4k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Origin.** Switzerland (allied; not on any covered list). Passes US-federal default policy.
- **License fit.** Apache-2.0 composes cleanly with URML's Apache-2.0 stance; the cleanest fit in URML's simulator set.
- **Maintainer signal.** Daily activity, large model library, responsive issue tracker plus community Discord.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; simulation-substrate declaration + sim-versus-real deployment context are queued Spec RFCs (shared with RFC-0037 / RFC-0050 / RFC-0051 / RFC-0060 / RFC-0144).
- Reference runtime: a future `WebotsAdapter` driving a Webots controller is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Spec-RFC prerequisite** (simulation-substrate declaration), shared with the rest of the sim set.
- **Robot-agnostic ambiguity.** Webots simulates many robot classes; a Webots manifest mostly inherits the simulated robot's capabilities, so the Webots-specific surface is thin (substrate declaration plus PROTO reference).
- **Overlap risk.** A reviewer could ask why Webots needs its own RFC when the sim-substrate gap is already known. The answer: Webots is a distinct maintainer and the only flagship open simulator URML had skipped.

## Alternatives considered

1. **Fold Webots into a single sim-substrate Spec RFC rather than an outreach RFC.** Rejected for engagement. The Spec RFC is the right home for the field; this Outreach RFC is the right way to ask the Webots maintainers whether the mapping fits their model.
2. **Engage at `cyberbotics/webots_ros2` instead of core.** Deferred. The ROS 2 interface is a strong secondary surface; the substrate mapping belongs at the simulator core, which is also substrate-neutral (Webots runs without ROS).
3. **Skip Webots since the sim gap is documented.** Rejected. Skipping it is exactly the inconsistency this RFC fixes.

## Prior art

- [`cyberbotics/webots`](https://github.com/cyberbotics/webots) — the upstream simulator.
- [RFC-0037 (OSRF / Gazebo)](0037-osrf-gazebo-integration.md), [RFC-0050 (NVIDIA Isaac)](0050-nvidia-isaac-lab-integration.md), [RFC-0051 (CARLA)](0051-carla-simulator-integration.md), [RFC-0060 (MuJoCo)](0060-mujoco-integration.md) — the existing sim-substrate set Webots completes.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the compatible-runtimes registry a Webots adapter could list against.

## Unresolved questions

For the Cyberbotics / Webots maintainers:

1. **Simulation-substrate declaration.** Is `substrate.simulator: webots` plus a PROTO reference the right manifest shape, or would you expect URML to reference a world file or a different handle?
2. **Integration boundary.** Is a generated Webots controller (Python) the natural boundary, or would the supervisor / extern-controller API be cleaner for an external intent layer?
3. **Sim-versus-real.** Many Webots robots have physical twins. Should URML's manifest declare sim-versus-real as deployment context, and does that match how your users move between the two?
4. **PROTO cross-reference.** Should URML reference a specific PROTO node, or is the robot model below the manifest line?
5. **Core versus webots_ros2.** Is engagement better at the simulator core or at `webots_ros2` for a substrate-neutral intent layer?
6. **Adapter home.** URML repo (a `WebotsAdapter`), a Webots-side sample, or neither?
7. **Conformance listing.** Would Webots consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported, no obligation.)
8. **Anything else.**

## Implementation note

RFC-0233 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`cyberbotics/webots` has Issues enabled and an active community Discord. URML's planned channel: a single GitHub Issue (labelled `question`) pointing to this RFC, or a Discord thread if the maintainers prefer. If the GitHub-Issue venue is not the right place for a cross-project RFC, that answer is useful and URML will route to Discord.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0, 4.4k stars [4383], Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (shared sim Spec-RFC prerequisite, robot-agnostic thin surface, overlap risk).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Switzerland (allied, passes default policy); Apache-2.0 composes cleanly; default policy passes.
- [x] CLAUDE.md compliance check passed.
