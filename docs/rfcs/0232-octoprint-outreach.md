---
rfc: 0232
title: OctoPrint (3D-printer host / web UI) integration, request for comment from OctoPrint maintainers
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

# RFC-0232: OctoPrint (3D-printer host / web UI) integration

## Summary

URML proposes a capability-manifest mapping for OctoPrint-hosted printers. The ask is light: Apache-2.0, no spec change proposed, nothing for OctoPrint maintainers to maintain. URML composes print-job intent; OctoPrint already exposes a REST API and a plugin surface. The question is which one is the cleaner boundary for a third-party intent layer.

## Concrete example

English sentence:

> "Start the print I uploaded."

URML primitive:

```
start_print(file="bracket.gcode")
```

OctoPrint call (URML hits the REST API; OctoPrint then streams G-code to whichever firmware sits below):

```
POST /api/files/local/bracket.gcode
{ "command": "select", "print": true }
```

URML never embeds inside OctoPrint. The boundary is HTTP, the same boundary Cura, PrusaSlicer, and every existing host plugin use.

## Why URML on this target

OctoPrint is the dominant open host for 3D printers and speaks to Marlin, Klipper, and RepRap firmware over G-code. The integration boundary is HTTP / REST (or a small plugin if maintainers prefer). URML stays Apache-2.0; OctoPrint stays AGPL-3.0; no code crosses the boundary. The ask is one round of feedback on the mapping. No spec change is proposed here.

## Capability-manifest mapping

| URML field | Maps to OctoPrint attribute |
|---|---|
| `name` | Deployment handle (`octoprint_pi5_voron`, etc.) |
| `substrate.host: custom` (`octoprint`) | Declares OctoPrint as the host above the firmware |
| `substrate.api: custom` (`octoprint_rest`) | REST API as the integration boundary |
| `substrate.firmware` | Marlin / Klipper / RepRap (cross-references RFC-0227 and RFC-0231) |
| Print-job catalog | `/api/files/local` listing |
| Job state | `/api/job` state machine |

## Drawbacks

- Proposal only.
- AGPL-3.0 boundary. Integration stays at REST or a plugin; URML vendors no OctoPrint code, and a network-service interaction has its own AGPL implications a deployer must read.
- URML maps job and motion intent, not the plugin ecosystem (slicer, camera, filament sensor). A focused mapping is the design choice.

## Unresolved questions

For the OctoPrint maintainers:

1. For a third-party intent layer that drives a print job from a higher-level description, do you prefer the REST API as the boundary, or a small dedicated plugin?

## How to respond

OctoPrint's primary community venue is the OctoPrint community forum on Discourse. URML's planned channel: a Discourse thread pointing to this RFC, with the AGPL-3.0 boundary stated up front. GitHub Discussion is the fallback if the maintainers redirect there.

Sibling RFCs: [RFC-0231 (Marlin)](0231-marlin-outreach.md) is the firmware target OctoPrint hosts. [RFC-0227 (Klipper)](0227-klipper-outreach.md) is the host-plus-firmware target alternative to OctoPrint-on-Marlin.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (AGPL-3.0, 9.0k stars, Issues enabled, last commit 2026-05-27, isArchived: false).
- [x] Concrete example shows English sentence, URML primitive, and OctoPrint REST call.
- [x] One real question, not a numbered dump.
- [x] Drawbacks real (AGPL-3.0 boundary, scope limited to job/motion).
- [x] Backward compatibility additive; no Layer-2 primitive added; no spec change.
- [x] Provenance: community OSS, DE founder Gina Hausge; default policy passes.
- [x] CLAUDE.md compliance check passed.
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
