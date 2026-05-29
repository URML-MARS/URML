---
rfc: 0231
title: LinuxCNC (CNC machine-tool motion substrate) integration, request for comment from LinuxCNC maintainers
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

# RFC-0231: LinuxCNC (CNC machine-tool motion substrate) integration

## Summary

URML does not yet ship a LinuxCNC manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for LinuxCNC-driven machine tools over [`LinuxCNC/linuxcnc`](https://github.com/LinuxCNC/linuxcnc) (GPL-2.0), and **requests review and feedback from the LinuxCNC maintainers**. No spec change.

**This is a Move-18 frame-break RFC, the second motion-control target after RFC-0227 (Klipper).** LinuxCNC is the original machine-intent community: mills, lathes, routers, plasma and laser cutters driven by G-code. A CNC machine is a positioning robot, G-code is its motion substrate, and the community has thought about "describe the cut, the machine executes it" for longer than most robotics stacks have existed.

## Motivation

LinuxCNC runs a real-time motion controller on Linux, reads G-code (RS-274), and drives steppers or servos through its HAL (Hardware Abstraction Layer). Repo at [`LinuxCNC/linuxcnc`](https://github.com/LinuxCNC/linuxcnc) (GPL-2.0, 2.3k stars, Issues enabled, last commit 2026-05-29, **not archived**).

URML benefits from documenting the LinuxCNC manifest mapping because:

1. **It is the deepest motion-control reframe URML can make.** A CNC mill is a Cartesian positioning robot. If URML's motion vocabulary maps onto LinuxCNC, the substrate-neutrality claim reaches machine tools, a domain no robotics stack URML has engaged covers.
2. **LinuxCNC already has a HAL, and so does URML.** LinuxCNC's HAL is a real-time signal-and-component layer; URML's Layer 1 is a capability HAL. The two are different abstractions at different altitudes, and the relationship is worth getting right rather than assuming.
3. **G-code is the shared compile target with RFC-0227.** A URML to G-code path validated against both Klipper and LinuxCNC is stronger evidence that the fabrication-motion mapping is substrate-neutral and not Klipper-specific.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `linuxcnc_mill_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to LinuxCNC attribute |
|---|---|
| `name` | Deployment handle (`linuxcnc_3axis_mill`, `linuxcnc_lathe`, etc.) |
| `mobility.drive_type` | **No clean v0.1 entry.** CNC kinematics are `trivkins` Cartesian / `lathe` / gantry / 5-axis; URML's enum has no machine-tool kinematics. Spec RFC queued (shared with RFC-0227). |
| `mobility.max_velocity` | INI `[TRAJ] MAX_LINEAR_VELOCITY` |
| `substrate.motion_controller: custom` (`linuxcnc`) | Declares LinuxCNC + its HAL as the motion substrate |
| Work-envelope / limits | INI `[AXIS_*] MIN_LIMIT` / `MAX_LIMIT` / `MAX_VELOCITY` / `MAX_ACCELERATION` (no v0.1 manifest field; queued) |
| Compile target | G-code (RS-274) emitted to LinuxCNC over its interpreter / `linuxcncrsh` boundary |

### What URML v0.1 does not yet express for LinuxCNC

1. **Machine-tool kinematics classes.** URML's `drive_type` enum has no Cartesian-gantry / lathe / 5-axis machine-tool kinematics. Spec RFC queued (shared with RFC-0227 Klipper), following the RFC-0009 precedent that added `quadruped` / `biped`.
2. **G-code-class substrate declaration.** URML's manifest has no `substrate.motion_controller` enum entry for a G-code-consuming controller.
3. **Work-envelope and per-axis limits.** Machine envelope and per-axis limits have no v0.1 manifest field.
4. **HAL-altitude boundary.** LinuxCNC's HAL is a real-time signal layer below URML's capability HAL. URML maps the motion-intent altitude (what move to make), not LinuxCNC HAL pin wiring. Stated as a boundary, not an omission.
5. **Scope boundary.** URML maps motion intent. Spindle speed, coolant, tool-change cycles, and feed-rate-as-material-process are machine process control and stay outside URML's scope.

### Compatibility notes

- **Project.** [`LinuxCNC/linuxcnc`](https://github.com/LinuxCNC/linuxcnc) — long-running community open-source project (post-EMC2 lineage). GPL-2.0.
- **Engagement repo.** GPL-2.0, 2.3k stars, Issues enabled, last commit 2026-05-29, **not archived**.
- **Origin.** Community open-source (international contributor base). Passes US-federal default policy (community OSS, no covered-list vendor, no single-vendor coupling).
- **License fit.** GPL-2.0 does **not** compose into URML's Apache-2.0 by code vendoring. Integration stays at the G-code / IPC boundary (URML emits G-code consumed over LinuxCNC's interpreter / `linuxcncrsh` socket), no LinuxCNC code in the URML repo. Same shape as RFC-0227 (Klipper) and RFC-0166 (piper1-gpl).
- **Maintainer signal.** Daily activity, deep and long-tenured community, mailing-list and forum culture.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; machine-tool kinematics `drive_type` classes + G-code substrate declaration + work-envelope manifest fields are queued Spec RFCs (shared with RFC-0227).
- Reference runtime: a future `LinuxCNCAdapter` emitting G-code over `linuxcncrsh` is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Shared Spec-RFC prerequisites** with RFC-0227 (fabrication / machine-tool kinematics, G-code substrate, work-envelope).
- **HAL-name collision risk.** Both projects use "HAL" for different things; a reviewer could read URML as conflating them. URML's answer: they are different altitudes and URML maps the upper one.
- **Identity-edge risk.** Machine tools sit at the edge of "robot intent." The reframe is deliberate; URML maps motion intent only.
- **GPL-2.0 boundary** constrains integration to IPC.

## Alternatives considered

1. **Bundle LinuxCNC into RFC-0227 (Klipper) as one fabrication-motion RFC.** Rejected. Per-target engagement is URML's house pattern; LinuxCNC's machine-tool kinematics and real-time HAL differ enough from Klipper's printer focus to warrant a distinct conversation, even though they share queued Spec RFCs.
2. **Engage at the HAL layer rather than G-code.** Rejected. URML's motion-intent altitude maps to G-code; the real-time HAL is below the line URML describes.
3. **Treat machine tools as out of URML's scope.** Rejected. A Cartesian mill is a positioning robot; declining it would concede substrate-neutrality at the machine-tool boundary.

## Prior art

- [`LinuxCNC/linuxcnc`](https://github.com/LinuxCNC/linuxcnc) — the upstream controller.
- [RFC-0227 (Klipper)](0227-klipper-outreach.md) — sibling fabrication-motion RFC; shares the queued Spec RFCs and the G-code boundary.
- [RFC-0009 (mobility specialization)](0009-legged-humanoid-mobility.md) — the precedent for extending the `drive_type` enum.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the compatible-runtimes registry a LinuxCNC adapter could list against.
- [RFC-0166 (piper1-gpl)](0166-piper1-gpl-outreach.md) — the GPL IPC-boundary integration shape.

## Unresolved questions

For the LinuxCNC maintainers:

1. **Machine-tool kinematics.** Would a URML `drive_type` declaring machine-tool kinematics (Cartesian / lathe / gantry / 5-axis) be the right manifest shape, or should URML reference the INI / kinematics module directly?
2. **HAL boundary.** Is the distinction "URML maps motion intent, LinuxCNC HAL wires real-time signals" the right framing, or does it misread how you would expect an external intent layer to compose?
3. **Integration boundary.** Is G-code over `linuxcncrsh` the boundary you would expect, or is there a cleaner external-command interface?
4. **Work-envelope and limits.** Should URML's manifest cross-reference the INI limits or restate them?
5. **Scope boundary.** URML maps motion intent, not spindle / coolant / tool-change process control. Is a motion-only mapping useful for CNC, or does it omit too much?
6. **License boundary.** URML stays Apache-2.0 and integrates at the G-code / IPC boundary with no LinuxCNC code vendored. Does that match your expectation?
7. **Adapter home and conformance.** URML repo (a `LinuxCNCAdapter`), a LinuxCNC-side bridge, or neither? Would LinuxCNC consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported, no obligation.)
8. **Anything else.**

## Implementation note

RFC-0231 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`LinuxCNC/linuxcnc` has Issues enabled. The project's cultural home for discussion is the LinuxCNC forum (and developer mailing list). URML's planned channel: a forum thread pointing to this RFC, with a GitHub Issue (labelled `question`) only if the maintainers prefer it. If the GitHub-Issue venue is not the right place for a cross-project RFC, that answer is useful and URML will route to the forum.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (GPL-2.0, 2.3k stars [2305], Issues enabled, last commit 2026-05-29, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (shared Spec-RFC prerequisites, HAL-name collision risk, identity-edge risk, GPL IPC-only boundary).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: community OSS (international); GPL-2.0 integration at the IPC boundary; default policy passes.
- [x] CLAUDE.md compliance check passed.
