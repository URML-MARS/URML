---
rfc: 0228
title: WPILib (FIRST Robotics education substrate) integration, request for comment from WPILib maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Open
created: 2026-05-29
updated: 2026-05-30
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

# RFC-0228: WPILib (FIRST Robotics education substrate) integration

## Summary

URML does not yet ship a WPILib manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for WPILib-driven FRC robots over [`wpilibsuite/allwpilib`](https://github.com/wpilibsuite/allwpilib) (BSD-3-Clause), and **requests review and feedback from the WPILib maintainers**. No spec change.

**This is a Move-18 frame-break RFC, and URML's first education-pipeline target.** WPILib is not a robot vendor; it is the open library that tens of thousands of FIRST Robotics Competition students program a real robot with every season. Per the manifesto's "optimize for inevitability," the surface that teaches the next generation of roboticists is a strategic adoption surface, not a niche one.

## Motivation

WPILib is the open-source library suite (Java, C++, Python) that FRC teams use to control a robot from a roboRIO. It abstracts drivetrains, motor controllers over CAN, sensors, and command-based scheduling. Repo at [`wpilibsuite/allwpilib`](https://github.com/wpilibsuite/allwpilib) (BSD-3-Clause, 1.3k stars, Issues enabled, last commit 2026-05-29, **not archived**).

URML benefits from documenting the WPILib manifest mapping because:

1. **It is the largest student-roboticist on-ramp in the world.** A generation that learns "describe what the robot should do" alongside WPILib carries the mental model forward. Adoption at scale starts where people first learn.
2. **FRC drivetrains exercise URML's mobility vocabulary and one real gap.** Differential (tank) and mecanum map onto URML's existing enum; swerve does not, and swerve is now the dominant competitive drivetrain. The mapping surfaces a concrete, well-bounded Spec RFC.
3. **WPILib is a clean substrate-neutrality test.** It has no ROS dependency. A URML mapping that lands on WPILib is another data point that the language sits above substrates rather than assuming one.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `wpilib_frc_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to WPILib attribute |
|---|---|
| `name` | Deployment handle (`frc_team_robot_2026`, etc.) |
| `mobility.drive_type` | `differential` (tank / arcade) and `omnidirectional` (mecanum) map cleanly; **swerve has no v0.1 entry** (Spec RFC queued) |
| `mobility.max_velocity` | Team-characterized free-speed (m/s) |
| `substrate.controller: custom` (`wpilib` / `roboRIO`) | Declares the roboRIO + WPILib runtime as the substrate |
| Motor / actuator inventory | CAN motor controllers (e.g. CTRE, REV) declared per drivetrain |

### What URML v0.1 does not yet express for WPILib

1. **Swerve-drive mobility class.** URML's `drive_type` enum has `differential` and `omnidirectional` but no `swerve`. Swerve is the dominant modern FRC drivetrain and a distinct kinematic class (independently steered and driven modules). Spec RFC queued, following the RFC-0009 precedent that added `quadruped` / `biped`.
2. **CAN motor-controller substrate declaration.** URML's manifest cannot today declare the CAN motor-controller inventory (vendor, count) that a WPILib drivetrain composes from.
3. **Competition-context deployment metadata.** FRC robots are built to a season's game rules and field. URML's manifest has no field for season / field deployment context, which is real metadata for a reproducible FRC deployment.

### Compatibility notes

- **Project.** [`wpilibsuite/allwpilib`](https://github.com/wpilibsuite/allwpilib) — maintained by WPILib (FIRST and WPILib contributors). BSD-3-Clause.
- **Engagement repo.** BSD-3-Clause, 1.3k stars, Issues enabled, last commit 2026-05-29, **not archived**.
- **Origin.** US-domiciled (FIRST / WPI heritage). Passes US-federal default policy cleanly.
- **License fit.** BSD-3-Clause composes cleanly with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity, multi-language library, large and predictable seasonal user base.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; swerve `drive_type` class + CAN motor-controller declaration + competition-context metadata are queued Spec RFCs.
- Reference runtime: a future `WPILibAdapter` (emitting to a roboRIO over the WPILib command interface, or generating a command-based skeleton) is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Spec-RFC prerequisite** (swerve class is the headline one).
- **Seasonal audience.** FRC engagement has a competition rhythm; maintainer attention is not uniform across the year.
- **Education framing risk.** A maintainer could read "education on-ramp" as URML treating WPILib as a teaching toy rather than a real substrate. URML's answer: the mapping is a real motion mapping, swerve included, not a demo.

## Alternatives considered

1. **Engage a vendor SDK (CTRE Phoenix, REV) instead of WPILib core.** Rejected for batch 1. WPILib is the vendor-neutral substrate every FRC team shares; vendor SDKs sit below it and are future candidates.
2. **Engage FIRST (the organization) rather than the library maintainers.** Rejected. The library is the technical surface; the mapping conversation belongs with the maintainers, not the program office.
3. **Skip swerve and map only differential / mecanum.** Rejected. Swerve is the dominant modern drivetrain; a mapping that omits it would be obsolete on arrival.

## Prior art

- [`wpilibsuite/allwpilib`](https://github.com/wpilibsuite/allwpilib) — the upstream library suite.
- [RFC-0009 (mobility specialization)](0009-legged-humanoid-mobility.md) — the precedent for extending the `drive_type` enum; a `swerve` class follows the same path.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the compatible-runtimes registry a WPILib adapter could list against.
- [RFC-0227 (Klipper)](0227-klipper-outreach.md), [RFC-0229 (Crazyflie)](0229-crazyflie-outreach.md), [RFC-0230 (OpenBCI / BrainFlow)](0230-openbci-brainflow-outreach.md) — sibling Move-18 frame-break RFCs.

## Unresolved questions

For the WPILib maintainers:

1. **Swerve mobility class.** URML's `drive_type` enum has no `swerve`. Spec RFC queued. What does a swerve declaration need to capture at the capability level (module count, independent steering) without overreaching into per-module geometry?
2. **Integration boundary.** For an external intent layer, is the cleaner boundary generating a command-based skeleton, or driving the robot over an existing WPILib interface (e.g. a network-table or command path)?
3. **CAN motor-controller declaration.** Should URML's manifest declare the CAN motor-controller inventory (vendor, count), or treat it as below the manifest line?
4. **Competition-context metadata.** Is season / field deployment context worth declaring in a manifest, or is it out of scope for a capability description?
5. **Language target.** WPILib ships Java, C++, and Python. Which is the natural target for a generated adapter or skeleton?
6. **Adapter home.** URML repo (a `WPILibAdapter`), a WPILib-side example, or neither?
7. **Conformance listing.** Would WPILib consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0228 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`wpilibsuite/allwpilib` has Issues enabled. The FRC community's cultural home for design discussion is the Chief Delphi forum. URML's planned channel: a Chief Delphi thread pointing to this RFC, with a GitHub Issue (labelled `question`) only if the maintainers prefer it. If the GitHub-Issue venue is not the right place for a cross-project RFC, that answer is useful and URML will route to Chief Delphi.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (BSD-3-Clause, 1.3k stars [1280], Issues enabled, last commit 2026-05-29, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (swerve Spec-RFC prerequisite, seasonal audience, education-framing risk).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: US-domiciled (FIRST / WPI); BSD-3-Clause composes cleanly; default policy passes.
- [x] CLAUDE.md compliance check passed.
