---
rfc: 0231
title: Marlin (3D-printer / CNC firmware) integration, request for comment from MarlinFirmware maintainers
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

# RFC-0231: Marlin (3D-printer / CNC firmware) integration

## Summary

URML proposes a capability-manifest mapping for Marlin-driven motion platforms. The ask is light: Apache-2.0, no spec change proposed, nothing for Marlin maintainers to maintain. URML emits G-code; Marlin already consumes G-code. The question is whether the mapping shape is sensible from the firmware-maintainer point of view.

## Concrete example

English sentence (a user types this into a URML front end):

> "Print this part."

URML primitive (Layer 2, what the validator sees):

```
run_print_job(file="bracket.gcode", profile="pla_0.2mm")
```

Marlin call (what the firmware actually receives, over serial / USB):

```
G28        ; home all axes
G1 Z5 F300
G1 X20 Y20 F3000
M104 S200  ; (process-control, outside URML scope)
... (G-code stream from the sliced file) ...
M84        ; disable steppers
```

URML does not generate the slicer output. URML composes the job-level intent ("print this file on this printer") and hands the existing G-code stream to Marlin over the same boundary a slicer or host already uses.

## Why URML on this target

Marlin is the de-facto open firmware on Cartesian, CoreXY, and Delta printers. The integration boundary is the G-code stream, which Marlin already documents. There is no shared-code path proposed: URML stays Apache-2.0, Marlin stays GPL-3.0, and the two meet over the wire. The ask is one round of feedback on the manifest mapping. No spec change is proposed here. Nothing in this RFC requires maintainer work in the Marlin tree.

## Capability-manifest mapping

| URML field | Maps to Marlin attribute |
|---|---|
| `name` | Deployment handle (`marlin_ender3_v2`, `marlin_voron_legacy`, etc.) |
| `mobility.drive_type` | Cartesian / CoreXY / Delta (no v0.1 enum entry today; Spec RFC queued) |
| `mobility.max_velocity` | `DEFAULT_MAX_FEEDRATE` per axis (Configuration.h) |
| `substrate.motion_controller: custom` (`marlin`) | Declares Marlin firmware as the motion substrate |
| Work envelope | `X_BED_SIZE`, `Y_BED_SIZE`, `Z_MAX_POS` (Configuration.h) |
| Compile target | G-code stream over USB / serial |

## Drawbacks

- Proposal only. No adapter ships in this RFC.
- GPL-3.0 boundary. Integration stays at the G-code wire; URML vendors no Marlin code.
- URML maps motion intent, not thermal or material process. A Marlin mapping that covers motion but not the heater is partial by design.

## Unresolved questions

For the MarlinFirmware maintainers:

1. Is the G-code stream the right boundary for a third-party intent layer, or is there a cleaner entry (host / serial protocol extension) you would point to?

## How to respond

`MarlinFirmware/Marlin` has Issues enabled. URML's planned channel: a single GitHub Issue pointing to this RFC, with the G-code-boundary framing explicit. If Issues are not the right venue, the planned fallback is the Marlin community forum.

Sibling RFC at the firmware-vs-host split: [RFC-0227 (Klipper)](0227-klipper-outreach.md). Klipper is the host-plus-firmware target; Marlin is the firmware-only target. The two are deliberately separate engagements.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (GPL-3.0, 17.4k stars, Issues enabled, last commit 2026-05-27, isArchived: false).
- [x] Concrete example shows English sentence, URML primitive, and Marlin call.
- [x] One real question, not a numbered dump.
- [x] Drawbacks real (GPL-3.0 IPC boundary, motion-only scope, proposal status).
- [x] Backward compatibility additive; no Layer-2 primitive added; no spec change.
- [x] Provenance: community OSS, US lead with global contributors; default policy passes.
- [x] CLAUDE.md compliance check passed.
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
