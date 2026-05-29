---
rfc: 0227
title: Klipper (3D-printer / CNC motion substrate) integration, request for comment from Klipper maintainers
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

# RFC-0227: Klipper (3D-printer / CNC motion substrate) integration

## Summary

URML does not yet ship a Klipper manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Klipper-driven motion platforms over [`Klipper3d/klipper`](https://github.com/Klipper3d/klipper) (GPL-3.0), and **requests review and feedback from the Klipper maintainers**. No spec change.

**This is URML's first Move-18 RFC, and its first fabrication-motion target.** Move #18 is the frame-break wave: adoption surfaces outside the conventional robot-vendor model. A 3D printer is a robot, a gantry is a positioning mechanism, and G-code is a motion substrate. None of these surface through a robot-OEM lens, and the Klipper community is one of the largest active open-source motion-control communities in existence.

## Motivation

Klipper is a host-plus-MCU motion firmware. A Python host (typically a Raspberry Pi) computes kinematics and step timing and streams them to one or more microcontrollers; the host consumes G-code as its command interface. Repo at [`Klipper3d/klipper`](https://github.com/Klipper3d/klipper) (GPL-3.0, 11.6k stars, Issues enabled, last commit 2026-05-27, **not archived**).

URML benefits from documenting the Klipper manifest mapping because:

1. **It tests the substrate-neutrality claim against a non-ROS, non-vendor target.** Klipper has zero ROS dependency and is not a robot OEM. If a URML motion mapping lands cleanly on Klipper, the "describe intent above the substrate" claim holds somewhere every prior move never reached.
2. **G-code is a real compile target.** URML's value is one human sentence to motion. A printer or CNC gantry executing a URML-derived move over G-code is a self-contained, hermetic, any-OS demo with no robot hardware required.
3. **Klipper's `printer.cfg` is an upstream-declared motion inventory.** Kinematics, per-axis position limits, velocity, and acceleration are already declared in `printer.cfg`. URML's manifest can cross-reference that inventory rather than restate it.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `klipper_gantry_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to Klipper attribute |
|---|---|
| `name` | Deployment handle (`klipper_voron_24`, `klipper_ratrig_vcore`, etc.) |
| `mobility.drive_type` | **No clean v0.1 entry.** Klipper kinematics are `cartesian` / `corexy` / `corexz` / `delta` / `polar` / `rotary_delta`; URML's enum has none of these. Spec RFC queued (see below). |
| `mobility.max_velocity` | `printer.cfg` `max_velocity` |
| `substrate.motion_controller: custom` (`klipper`) | Declares the Klipper host as the motion substrate |
| Work-envelope / limits | `printer.cfg` stepper `position_min` / `position_max`, `max_accel` (no v0.1 manifest field; queued) |
| Compile target | G-code emitted to Klipper over the virtual-serial / Moonraker API boundary |

### What URML v0.1 does not yet express for Klipper

1. **Fabrication-motion kinematics classes.** URML's `drive_type` enum is `differential` / `omnidirectional` / `ackermann` / `tracked` / `multirotor` / `fixed_wing` / `vtol` / `manipulator_base` / `underwater_thrusters` / `quadruped` / `biped`. It has no gantry kinematics (`cartesian` / `corexy` / `delta`). Spec RFC queued, following the RFC-0009 precedent that added `quadruped` / `biped`.
2. **G-code-class substrate declaration.** URML's manifest has no `substrate.motion_controller` enum entry for a G-code-consuming host.
3. **Work-envelope and per-axis limits.** Build volume and per-axis position / velocity / acceleration limits have no v0.1 manifest field.
4. **Scope boundary, stated honestly.** URML expresses motion intent. A printer's extruder temperature, material feed, and heater control are process control, not motion intent, and stay outside URML's scope. A Klipper mapping that covers motion but not the thermal / material process is a partial mapping by design, not by omission.

### Compatibility notes

- **Project.** [`Klipper3d/klipper`](https://github.com/Klipper3d/klipper) — community open-source project led by Kevin O'Connor with a large contributor base. GPL-3.0.
- **Engagement repo.** GPL-3.0, 11.6k stars, Issues enabled, last commit 2026-05-27, **not archived**.
- **Origin.** Community open-source (US-based lead maintainer). Passes US-federal default policy (community OSS, no covered-list vendor, no single-vendor coupling).
- **License fit.** GPL-3.0 does **not** compose into URML's Apache-2.0 by code vendoring. Integration stays at the G-code / IPC boundary: URML emits G-code that Klipper consumes over a process / serial boundary, with no Klipper code in the URML repo. Same shape as RFC-0166 (piper1-gpl) and RFC-0122 (GelSight).
- **Maintainer signal.** Daily activity, very large community, strict bug-report templates.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; fabrication-motion `drive_type` classes + G-code substrate declaration + work-envelope manifest fields are queued Spec RFCs.
- Reference runtime: a future `KlipperAdapter` emitting G-code over the Moonraker / virtual-serial boundary is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multiple Spec-RFC prerequisites** (fabrication-motion kinematics classes, G-code substrate declaration, work-envelope fields).
- **Identity-edge risk.** Fabrication motion sits at the edge of "robot intent." The reframe is deliberate, but a reviewer could read it as scope creep into machine-tool control. URML's answer: it maps motion intent only, and says so.
- **GPL-3.0 boundary** constrains integration to IPC; no shared-code path.

## Alternatives considered

1. **Engage at Moonraker (the HTTP API layer) instead of Klipper core.** Deferred, not rejected. Moonraker is the orchestration API, but kinematics and G-code semantics live in Klipper core. Moonraker is a strong secondary surface for the eventual adapter; the motion mapping belongs at the core.
2. **Engage Marlin (firmware) or OctoPrint (orchestration) first.** Rejected for batch 1. Klipper has the largest active community and the cleanest host-side kinematics abstraction. Marlin and OctoPrint are future frame-break candidates.
3. **Treat 3D printing / CNC as out of URML's scope.** Rejected. Motion over a Cartesian or delta machine is squarely a motion-intent mapping; declining it would concede the substrate-neutrality claim at exactly the point that tests it hardest.

## Prior art

- [`Klipper3d/klipper`](https://github.com/Klipper3d/klipper) — the upstream firmware.
- [RFC-0009 (mobility specialization)](0009-legged-humanoid-mobility.md) — the precedent for extending the `drive_type` enum (added `quadruped` / `biped`); fabrication-motion classes would follow the same path.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the compatible-runtimes registry a Klipper adapter could list against.
- [RFC-0166 (piper1-gpl)](0166-piper1-gpl-outreach.md) + [RFC-0122 (GelSight)](0122-gelsight-tactile-outreach.md) — the GPL IPC-boundary integration shape.
- [RFC-0228 (WPILib)](0228-wpilib-outreach.md), [RFC-0229 (Crazyflie)](0229-crazyflie-outreach.md), [RFC-0230 (OpenBCI / BrainFlow)](0230-openbci-brainflow-outreach.md) — sibling Move-18 frame-break RFCs.

## Unresolved questions

For the Klipper maintainers:

1. **Fabrication-motion kinematics.** Would a URML `drive_type` declaring kinematics (`cartesian` / `corexy` / `delta`) mirroring `printer.cfg` be the right manifest shape, or should URML reference the Klipper config directly rather than restate kinematics?
2. **Integration boundary.** For an external intent layer, do you consider G-code emission or the Moonraker API the cleaner boundary?
3. **Work-envelope and limits.** Should URML's manifest cross-reference `printer.cfg` position / velocity / acceleration limits, or restate them?
4. **Scope boundary.** URML maps motion intent, not extruder / heater / material process control. Is a motion-only mapping coherent for Klipper, or does it omit too much to be useful in practice?
5. **License boundary.** URML stays Apache-2.0 and would integrate at the G-code / IPC boundary with no Klipper code vendored. Does that match your expectation for a third-party layer above Klipper?
6. **Adapter home.** URML repo (a `KlipperAdapter` emitting G-code), a Klipper-side bridge, or neither?
7. **Conformance listing.** Would Klipper consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0227 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`Klipper3d/klipper` has Issues enabled, but the project directs general discussion and feature ideas to the Klipper community channels (the Klipper Discourse and Discord), and reserves GitHub Issues for bug reports under strict templates. URML respects the venue: the planned channel is a community-forum thread pointing to this RFC, not a GitHub Issue, unless a maintainer indicates an Issue is welcome. If the GitHub-Issue venue is not the right place for a cross-project RFC, that answer is useful on its own and URML will route to the forum.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (GPL-3.0, 11.6k stars [11583], Issues enabled, last commit 2026-05-27, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (Spec-RFC prerequisites, identity-edge risk, GPL IPC-only boundary).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: community OSS (US-based lead); GPL-3.0 integration at the IPC boundary; default policy passes.
- [x] CLAUDE.md compliance check passed.
