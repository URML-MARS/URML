---
rfc: 0232
title: Pybricks (LEGO programmable-hub education substrate) integration, request for comment from Pybricks maintainers
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

# RFC-0232: Pybricks (LEGO programmable-hub education substrate) integration

## Summary

URML does not yet ship a Pybricks manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Pybricks-driven LEGO robots over [`pybricks/pybricks-micropython`](https://github.com/pybricks/pybricks-micropython) (MIT), and **requests review and feedback from the Pybricks maintainers**. No spec change.

**This is a Move-18 frame-break RFC, the second education-pipeline target after RFC-0228 (WPILib).** Where WPILib reaches high-school FIRST Robotics, Pybricks reaches the layer below it: kids and classrooms programming LEGO SPIKE Prime, MINDSTORMS, and Technic hubs in Python. It is the youngest on-ramp in robotics, and the first place a generation meets "write what the robot should do."

## Motivation

Pybricks is MIT-licensed MicroPython firmware for LEGO programmable hubs. A user writes a Python program against the Pybricks API (motors, sensors, a `DriveBase`), and it runs on the hub. Repo at [`pybricks/pybricks-micropython`](https://github.com/pybricks/pybricks-micropython) (MIT, 324 stars, last commit 2026-05-28, **not archived**).

URML benefits from documenting the Pybricks manifest mapping because:

1. **It is the earliest adoption surface in robotics.** Per the manifesto's "optimize for inevitability," reaching learners before they form a mental model is the highest-leverage education move. Pybricks reaches them earlier than WPILib does.
2. **The `DriveBase` maps onto URML's existing mobility vocabulary.** Pybricks robots are typically two-wheel differential-drive, which URML's `differential` `drive_type` already covers. The mapping is honest and small.
3. **It is a clean MIT, non-ROS substrate.** A URML to Pybricks-Python path is another substrate-neutrality data point, with no copyleft or vendor-SDK friction.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `pybricks_drivebase_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to Pybricks attribute |
|---|---|
| `name` | Deployment handle (`pybricks_spike_prime`, `pybricks_technic_hub`, etc.) |
| `mobility.drive_type: differential` | Pybricks `DriveBase` (two driven wheels) maps cleanly |
| `mobility.max_velocity` | `DriveBase` configured straight speed (converted to m/s) |
| `substrate.controller: custom` (`pybricks` on a LEGO hub) | Declares the Pybricks MicroPython runtime on the hub as the substrate |
| Actuator / sensor inventory | Pybricks `Motor` + sensor objects bound to hub ports |
| Compile target | A Pybricks Python program run on the hub |

### What URML v0.1 does not yet express for Pybricks

1. **LEGO-hub MCU substrate declaration.** URML's manifest has no `substrate.controller` enum entry for a LEGO programmable hub running MicroPython.
2. **Port-topology declaration.** Pybricks binds motors and sensors to named hub ports (A-F). URML's manifest cannot today declare port-level actuator topology.
3. **Block-to-text bridge.** Many learners start in a block editor before Python. URML's natural-language layer and a block environment are different front-ends to the same intent; declaring that relationship is out of v0.1 scope and noted as a boundary.

### Compatibility notes

- **Project.** [`pybricks/pybricks-micropython`](https://github.com/pybricks/pybricks-micropython) — community open-source project (The Pybricks Authors). MIT.
- **Engagement repo.** MIT, 324 stars, last commit 2026-05-28, **not archived**. Issues on the code repo are disabled by design; the project routes issues and questions to [`pybricks/support`](https://github.com/pybricks/support) (MIT, Issues enabled), which is the engagement surface.
- **Origin.** Community open-source. Passes US-federal default policy (MIT OSS, no covered-list vendor).
- **License fit.** MIT composes cleanly with URML's Apache-2.0 stance.
- **Maintainer signal.** Active firmware development; dedicated support repo for user interaction.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; LEGO-hub MCU substrate declaration + port-topology declaration are queued Spec RFCs.
- Reference runtime: a future `PybricksAdapter` emitting a Pybricks Python program is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Spec-RFC prerequisites** (hub substrate declaration, port topology).
- **Engagement-venue indirection.** Issues live on `pybricks/support`, not the code repo; URML must route correctly.
- **Education-framing risk.** A maintainer could read "youngest on-ramp" as URML treating Pybricks as a toy. URML's answer: `DriveBase` is a real differential-drive mapping, and the intent vocabulary is the same one URML uses for industrial robots.

## Alternatives considered

1. **Engage LEGO Education (the company) instead of Pybricks.** Rejected. Pybricks is the open, MIT-licensed, programmable surface; the official block environments are closed and not an integration boundary.
2. **Bundle Pybricks with WPILib (RFC-0228) as one education RFC.** Rejected. Different substrates, different audiences (K-12 LEGO vs high-school FRC), different maintainers; per-target engagement is the house pattern.
3. **Wait for a block-to-URML story before engaging.** Rejected. The Python `DriveBase` mapping is useful now; the block-front-end relationship is a separable later question.

## Prior art

- [`pybricks/pybricks-micropython`](https://github.com/pybricks/pybricks-micropython) — the upstream firmware; [`pybricks/support`](https://github.com/pybricks/support) is the issue / question tracker.
- [RFC-0228 (WPILib)](0228-wpilib-outreach.md) — sibling education-pipeline RFC, one tier up the age range.
- [RFC-0009 (mobility specialization)](0009-legged-humanoid-mobility.md) — the mobility-class vocabulary; `differential` already covers a `DriveBase`.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the compatible-runtimes registry a Pybricks adapter could list against.

## Unresolved questions

For the Pybricks maintainers:

1. **Hub substrate declaration.** What would a URML manifest need to capture about a Pybricks hub (model, firmware, port map) to be useful, without overreaching into per-program detail?
2. **Integration boundary.** Is generating a Pybricks Python program the right boundary, or is there a cleaner external-command path to a running hub?
3. **Port topology.** Should URML's manifest declare motor / sensor port bindings, or treat that as below the manifest line?
4. **DriveBase mapping.** Is `differential` a faithful capability description of a `DriveBase`, or are there configurations (e.g. steering, single-motor) that need distinct handling?
5. **Block-front-end relationship.** Is the natural-language-to-Pybricks idea coherent with how learners actually progress from blocks to Python, or a mismatch?
6. **Adapter home.** URML repo (a `PybricksAdapter`), a Pybricks-side example, or neither?
7. **Conformance listing.** Would Pybricks consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported, no obligation.)
8. **Anything else.**

## Implementation note

RFC-0232 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

The code repo has Issues disabled by design; the project routes issues and questions to [`pybricks/support`](https://github.com/pybricks/support) (Issues enabled). URML's planned channel: a single Issue on `pybricks/support` (labelled `question`) pointing to this RFC. If the maintainers prefer another venue or human-only correspondence, that preference is welcome and URML will route to it.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (code repo MIT, 324 stars, Issues disabled by design, last commit 2026-05-28, isArchived: false; `pybricks/support` MIT, Issues enabled — engagement surface).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (Spec-RFC prerequisites, engagement-venue indirection, education-framing risk).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: community OSS; MIT composes cleanly; default policy passes.
- [x] CLAUDE.md compliance check passed.
