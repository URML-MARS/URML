---
rfc: 0208
title: QGroundControl (Linux Foundation Dronecode operator-control UI) cross-citation, request for comment from QGC maintainers
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

# RFC-0208: QGroundControl (Linux Foundation Dronecode operator-control UI) cross-citation

## Summary

URML's drone profile dispatches against autopilot substrates (PX4 sibling [RFC-0196](0196-px4-autopilot-outreach.md), MAVLink sibling [RFC-0197](0197-mavlink-outreach.md), MAVSDK sibling [RFC-0198](0198-mavsdk-outreach.md)); the operator-control surface (ground-station / mission-planning UI) is QGroundControl. This RFC documents the proposed URML v0.1 capability-manifest mapping for the operator-control-surface class, engaged at the Linux Foundation Dronecode layer via [`mavlink/qgroundcontrol`](https://github.com/mavlink/qgroundcontrol) (Apache-2.0), and **requests review and feedback from the QGC maintainers**. No spec change.

This is a **Tier B cross-citation** RFC (not a primary substrate). QGroundControl is the operator-control UI, not the autopilot proper; URML cites it at the manifest-declaration layer rather than embedding it as a runtime adapter.

## Motivation

QGroundControl is the canonical open-source ground-control station for MAVLink-compatible autopilots (PX4 and ArduPilot). URML's drone-runtime stack ends at the autopilot dispatch layer; the operator-control surface (mission upload, telemetry display, manual override) is where production drone operators interact with the system. URML's manifest could declare `operator_control_surface: qgroundcontrol` as a deployment metadata field, enabling deployment-tier introspection.

Repo at [`mavlink/qgroundcontrol`](https://github.com/mavlink/qgroundcontrol) (Apache-2.0, 4.6k stars, Issues + Discussions enabled, last commit `2026-05-28`, **not archived**). Linux Foundation Dronecode Foundation governance.

URML benefits from documenting the engagement because:

1. **Operator-control-surface manifest field.** Production drone deployments routinely declare the operator-control UI as part of the deployment configuration; URML's manifest could declare it for deployment-tier introspection.
2. **MAVLink-message subset declaration.** QGC consumes a specific MAVLink message subset; URML's manifest could declare the message-subset expectation at the operator-control boundary.
3. **Plan / mission-file format declaration.** QGC's `.plan` file format is a deployment artifact; URML's manifest could declare the format reference for envelope-validation.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `qgroundcontrol_operator_surface.yaml` fragment)

| URML field | Maps to QGroundControl attribute |
|---|---|
| `name` | Deployment handle (`qgc_operator_surface_px4`) |
| `operator_control_surface: qgroundcontrol` | URML's first operator-control-surface enum value |
| `operator_control.mavlink_message_subset` | QGC-consumed MAVLink message subset |
| `operator_control.plan_format` | QGC `.plan` mission-file format declaration |
| `operator_control.telemetry_subset` | Operator-displayed telemetry message subset |
| `operator_control.manual_override.enabled` | Manual override channel availability |

### What URML v0.1 does not yet express for QGroundControl

1. **Operator-control-surface enum.** First-class manifest field; URML's first.
2. **MAVLink message-subset declaration.** Operator-surface MAVLink subset (different from autopilot-side full message set); URML's manifest could declare.
3. **Plan-format declaration.** QGC `.plan` JSON format reference; deployment artifact.
4. **Telemetry subset declaration.** Operator-displayed message subset for deployment-tier UI specification.

### Compatibility notes

- **Vendor org.** [`mavlink`](https://github.com/mavlink) (sibling to MAVLink RFC-0197 governance) — Linux Foundation Dronecode Foundation.
- **Engagement repo.** [`mavlink/qgroundcontrol`](https://github.com/mavlink/qgroundcontrol) — Apache-2.0, 4.6k stars, Issues + Discussions enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** Shares organization with [`mavlink/mavlink`](https://github.com/mavlink/mavlink) (RFC-0197) and [`mavlink/MAVSDK`](https://github.com/mavlink/MAVSDK) (RFC-0198).
- **Origin.** Linux Foundation Dronecode Foundation (multi-vendor, US-headquartered Linux Foundation). Passes US-federal default policy.
- **License fit.** Apache-2.0. Clean fit.
- **Maintainer signal.** Active commits; the canonical MAVLink ground-control station.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; operator-control-surface enum + MAVLink-subset declaration + plan-format reference + telemetry-subset Spec RFCs queued.
- Reference runtime: cross-citation only; no in-repo URML adapter for the operator-control surface (URML's runtime stack ends at the autopilot boundary, sibling RFC-0198 MAVSDK).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Operator-control-surface novelty** — URML's first operator-control-surface manifest declaration; no prior pattern.
- **Cross-citation-only** — URML's runtime stack ends at the autopilot; QGC engagement is at manifest-declaration layer only.
- **MAVLink-subset declaration semantic burden** — bridging operator-side vs autopilot-side message expectations.

## Alternatives considered

1. **Skip QGC; declare only autopilot-substrate manifest fields.** Rejected. Production deployments routinely include operator-control-surface declaration; ignoring it leaves URML's manifest incomplete for the operator-experience tier.
2. **Bundle QGC with PX4 in a single Dronecode RFC.** Rejected. QGC is operator-side; PX4 is autopilot-side. Different responsibilities, different deployment lifecycles. Per-target RFCs let conversation thread per group.
3. **Engage at Linux Foundation Dronecode meta layer.** Considered. Per-project engagement is the lowest-friction first-contact; foundation-level discussion stays open as escalation.

## Prior art

- [`mavlink/qgroundcontrol`](https://github.com/mavlink/qgroundcontrol) — the upstream QGC stack (engagement anchor).
- [RFC-0196 (PX4 outreach)](0196-px4-autopilot-outreach.md), [RFC-0197 (MAVLink outreach)](0197-mavlink-outreach.md), [RFC-0198 (MAVSDK outreach)](0198-mavsdk-outreach.md) — sibling Move-16 batch-1 RFCs under shared Dronecode governance.

## Unresolved questions

For the QGC / Dronecode maintainers:

1. **Operator-control-surface enum manifest field.** URML's first; QGC perspective on the enum value (`qgroundcontrol`, `qgc`)?
2. **MAVLink message-subset declaration.** Manifest field for operator-side MAVLink subset (different from autopilot full set)?
3. **Plan-format declaration.** QGC `.plan` JSON format reference — manifest declaration shape?
4. **Telemetry-subset declaration.** Operator-displayed telemetry message subset for deployment-tier UI specification?
5. **Manual-override declaration.** Should URML's manifest declare manual-override channel availability as a deployment metadata field?
6. **Cross-citation discipline.** URML proposes cross-citation only (no in-repo adapter); preferred citation form from the QGC side (README link, COMPATIBILITY.md entry)?
7. **Conformance listing.** Would QGC / Dronecode consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once URML's manifest fields stabilize?
8. **Anything else.**

## Implementation note

RFC-0208 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`mavlink/qgroundcontrol` has Issues + Discussions enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the operator-control-surface + cross-citation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0, 4.6k stars, Issues + Discussions enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (operator-control-surface novelty, cross-citation-only, MAVLink-subset declaration burden).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation Dronecode Foundation; default policy passes.
- [x] CLAUDE.md compliance check passed.
