---
rfc: 0233
title: LinuxCNC (general-purpose CNC / mill / lathe / robot-arm controller) integration, request for comment from LinuxCNC maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0233: LinuxCNC (general-purpose CNC controller) integration

## Summary

URML proposes a capability-manifest mapping for LinuxCNC-driven machines. The ask is light: Apache-2.0, no spec change proposed, nothing for LinuxCNC maintainers to maintain. URML emits G-code; LinuxCNC consumes G-code (RS274NGC) and exposes a HAL component model below it. The question is whether the G-code boundary is the right entry, or whether HAL is.

## Concrete example

English sentence:

> "Mill this pocket."

URML primitive:

```
run_machining_job(file="pocket.ngc", workpiece="6061_aluminum")
```

LinuxCNC call (URML hands the G-code to LinuxCNC; LinuxCNC's interpreter and motion planner drive HAL):

```
G54           ; work coordinate system
G0 Z5
G0 X10 Y10
G1 Z-2 F100
G1 X40 Y10 F500
G1 X40 Y40
G1 X10 Y40
G1 X10 Y10
G0 Z5
M30
```

URML never replaces LinuxCNC's interpreter or HAL. The boundary is the G-code stream that LinuxCNC already accepts.

## Why URML on this target

LinuxCNC runs mills, lathes, 3D printers, plasma cutters, robot arms, and hexapods on a real-time Linux kernel with a HAL component model below the interpreter. The breadth is the point: a URML mapping that lands on LinuxCNC reaches further than Marlin or Klipper (mills and lathes and robot arms, not only printers). URML stays Apache-2.0; LinuxCNC stays GPL-2.0; integration stays at the G-code or HAL boundary with no code vendoring. The ask is one round of feedback. No spec change is proposed here.

## Capability-manifest mapping

| URML field | Maps to LinuxCNC attribute |
|---|---|
| `name` | Deployment handle (`linuxcnc_bridgeport_mill`, `linuxcnc_hexapod`, etc.) |
| `mobility.drive_type` | Cartesian / lathe / hexapod / robot-arm kinematics (no v0.1 enum entry; Spec RFC queued) |
| `substrate.motion_controller: custom` (`linuxcnc`) | Declares LinuxCNC as the controller |
| `substrate.interface` | G-code (RS274NGC) or HAL pins / signals |
| Work envelope and limits | `.ini` `MAX_VELOCITY`, `MAX_ACCELERATION`, per-axis `MIN_LIMIT` / `MAX_LIMIT` |
| Machine class | mill / lathe / 3D-printer / plasma / robot-arm / hexapod (no v0.1 manifest field) |

## Drawbacks

- Proposal only.
- GPL-2.0 boundary. Integration stays at G-code or HAL; URML vendors no LinuxCNC code.
- Machine-class breadth. A single mapping that covers mill and lathe and robot-arm motion runs the risk of becoming a lowest-common-denominator. The mapping declares the class up front to avoid that.

## Unresolved questions

For the LinuxCNC maintainers:

1. For a third-party intent layer that wants to drive a machine from a higher-level description, do you consider the G-code interpreter or HAL the cleaner integration boundary, given the range of machine classes LinuxCNC supports?

## How to respond

The LinuxCNC forum is the primary maintainer hub. URML's planned channel: a forum thread pointing to this RFC, with a GitHub Issue as a secondary touch if maintainers prefer that venue.

Sibling RFCs at the fabrication-motion cluster: [RFC-0227 (Klipper)](0227-klipper-outreach.md) is the host-plus-firmware printer target. [RFC-0231 (Marlin)](0231-marlin-outreach.md) is the firmware-only printer target. LinuxCNC is the broader machine-tool target above both.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (GPL-2.0, 2.3k stars, Issues enabled, last commit 2026-05-29, isArchived: false).
- [x] Concrete example shows English sentence, URML primitive, and LinuxCNC G-code call.
- [x] One real question, not a numbered dump.
- [x] Drawbacks real (GPL-2.0 boundary, machine-class breadth, proposal status).
- [x] Backward compatibility additive; no Layer-2 primitive added; no spec change.
- [x] Provenance: community OSS, US/EU contributor base; default policy passes.
- [x] CLAUDE.md compliance check passed.
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
