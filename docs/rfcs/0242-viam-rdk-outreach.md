---
rfc: 0242
title: Viam RDK conceptual-peer integration, request for comment from Viam maintainers
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

# RFC-0242: Viam RDK conceptual-peer integration, request for comment from Viam maintainers

## Summary

URML is a small open language for robot intent. Viam's RDK is a modular, cloud-coupled robotics framework that composes adapters over hardware; URML composes intent over substrates. The two systems overlap at the hardware-abstraction layer with different design points: Viam routes through the cloud, URML validates locally before dispatch. This RFC frames the relationship as a conceptual peer (with a partial-substrate aspect at the resource boundary) and asks one light question about the cleanest interoperability seam. This RFC also completes Move-18 (all 16 engageable RFCs across batches 1 through 4, with RFC-0238 Pepper carried as a Tier C exclusion-with-cause stub). No spec change proposed, nothing for you to maintain.

## Concrete example

A Viam config declares a robot's resources:

```json
{
  "components": [
    { "name": "base", "type": "base", "model": "wheeled" },
    { "name": "cam",  "type": "camera", "model": "webcam" },
    { "name": "arm",  "type": "arm", "model": "ur5e" }
  ]
}
```

The same robot expressed as a URML capability manifest declares `mobility.drive_type: differential`, an arm with named end-effector poses, and a camera with a frame-id, then validates an English plan like:

> Drive to the workbench, pick up the wrench, place it on the cart.

against that manifest before any command leaves the host. Viam composes adapters over hardware; URML composes intent over substrates. Same physical robot, two layers of the stack speaking to each other at the resource boundary.

## Why URML on this target

This is a conceptual peer engagement with a partial-substrate aspect. Viam's RDK sits at the hardware-abstraction layer; URML's manifest sits above that layer and below the natural-language layer. A URML manifest could in principle declare Viam-managed resources as the validated capability surface, which makes Viam one of the few peer systems where mutual interoperability is structurally plausible rather than just rhetorical. The ask is light: where does Viam see the cleanest seam. AGPL-3.0 on Viam's RDK means any integration stays at the REST or cloud boundary, never embedded.

## Capability-manifest mapping

This is a peer-citation plus partial-substrate declaration shape, not a full adapter mapping. URML's docs and registry would carry a "conceptual peers" section that names Viam with the framing below, and an open question about whether the resource layer is also a seam.

| URML peer-citation field | Viam RDK value |
| ------------------------ | -------------- |
| `peer.name`              | Viam RDK       |
| `peer.repo`              | `viamrobotics/rdk` |
| `peer.surface`           | modular hardware-abstraction with cloud coupling |
| `peer.relationship`      | partial substrate at the resource boundary; conceptual peer above it |
| `peer.candidate_seam`    | resource-API, intent-level, or mutual-citation (open question; AGPL-3.0 keeps any code seam at the REST or cloud boundary) |

## Drawbacks

- AGPL-3.0 on Viam's RDK means any code-level integration stays at the REST or cloud boundary; URML cannot embed RDK as a library.
- Viam's design assumes a cloud round-trip; URML's posture is local-validate-then-dispatch. The seam between the two has to be explicit about where the trust boundary sits.
- `viamrobotics/rdk` has Issues disabled; the maintainer-confirmed channel is Discord, which is a different engagement surface than URML's other Move-18 RFCs.

## Unresolved questions

Where does Viam see the cleanest interoperability seam with URML, at the resource-API level (URML manifest declares Viam-managed resources), at the intent level (URML emits high-level intent that Viam dispatches), or as mutual citation without a code seam at all?

## How to respond

Issues are disabled on `viamrobotics/rdk`. The maintainer-confirmed channel is the Viam Discord; a short message in the appropriate channel pointing to this RFC is the intended shape. If Discord turns out not to be the right venue, GitHub Discussions or a direct maintainer contact are acceptable fallbacks. Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (AGPL-3.0, 164 stars, Issues disabled, last commit 2026-05-28, isArchived: false).
- [x] Conceptual-peer framing explicit; partial-substrate aspect at resource boundary noted.
- [x] No spec change proposed; AGPL-3.0 boundary acknowledged (REST or cloud only).
- [x] Discord-channel reality recorded; Issues-disabled surface flagged.
- [x] Ledger row drafted in `outreach-move18.yaml`; AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Move-18 completion noted (16 engageable RFCs across batches 1 through 4; RFC-0238 Pepper carried as Tier C exclusion-with-cause).
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
