---
rfc: 0193
title: Starship Technologies (sidewalk-delivery robotics, ROS-bag infrastructure layer) integration, request for comment from starship-technologies maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0193: Starship Technologies (sidewalk delivery, ROS-bag infrastructure layer) integration

## Summary

URML does not yet ship a delivery-class manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the sidewalk-delivery class — engaged at the ROS-bag-reader infrastructure layer via [`starship-technologies/bag_rdr`](https://github.com/starship-technologies/bag_rdr) (MIT), and **requests review and feedback from the starship-technologies maintainers**. No spec change.

**This is URML's first delivery-robot RFC.** The engagement enters at the ROS-bag infrastructure layer because Starship's actual sidewalk-delivery robot stack is closed; the ROS-bag-reader is the most-engageable surface in the org's public catalog.

## Motivation

Starship Technologies (Estonian-UK, founded by Skype co-founders) operates one of the largest sidewalk-delivery fleets globally. Their public GitHub surface is small but real — 24 public repos predominantly forks or ROS-adjacent infrastructure. The actual delivery-robot stack (perception, planning, control, fleet management) is closed.

Repo at [`starship-technologies/bag_rdr`](https://github.com/starship-technologies/bag_rdr) (MIT, 29 stars, Issues enabled, last commit `2026-02-22`, **not archived**).

URML benefits from documenting the engagement because:

1. **Sidewalk-delivery class is a structural URML manifest gap.** URML's mobility-class enum has `differential` / `omnidirectional` but doesn't today distinguish urban-delivery / sidewalk-class platforms (size constraints, urban-environment navigation expectations, public-space interaction profile).
2. **ROS-bag infrastructure layer is the appropriate engagement.** URML's perception-replay / logging-format manifests can target Starship's bag-reader for sim-to-real evaluation; the engagement entry is honest about the closed-robot-stack reality.
3. **Companion to Move-14 mobile-manipulator RFCs.** Different platform-class (mobile-base-only, no manipulator), different deployment context (urban public spaces vs indoor/research).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `starship_sidewalk_delivery_cell.yaml` fixture)

| URML field | Maps to Starship attribute |
|---|---|
| `name` | Generic identifier (`starship_sidewalk_delivery_robot`) |
| `mobility.drive_type: differential` | Wheeled differential mobile base (clean v0.1 fit) |
| `platform_class: custom` (`sidewalk_delivery`) | URML's first sidewalk-delivery class declaration |
| `deployment_context: custom` (`urban_public_space`) | Urban public-space deployment constraints |
| `payload_class: custom` (`small_package_locked_compartment`) | Locked-compartment package delivery |
| `data_format: custom` (`starship_rosbag`) | ROS-bag format used by `bag_rdr` |

### What URML v0.1 does not yet express for Starship

1. **Sidewalk-delivery / urban-delivery platform-class declaration.** URML's v0.1 has no platform-class enum for delivery robots. Spec RFC queued.
2. **Urban-public-space deployment-context declaration.** Deployment context affects safety-envelope semantics (pedestrian-aware navigation, public-street operation, weather constraints); URML's manifest cannot today declare this.
3. **Closed-robot-stack engagement-layer declaration.** URML's manifest can declare that the engagement is at the infrastructure-only layer (bag-reader, format-spec) rather than the full-stack adapter pattern. Novel manifest territory.

### Compatibility notes

- **Vendor org.** [`starship-technologies`](https://github.com/starship-technologies) — Starship Technologies, Estonia + UK.
- **Engagement repo.** [`starship-technologies/bag_rdr`](https://github.com/starship-technologies/bag_rdr) — MIT, 29 stars, Issues enabled, last commit 2026-02-22, **not archived**.
- **Companion repos.** `common_cxx` (MIT), `gobag`, `bagrec` — ROS bag infrastructure family.
- **Origin.** Estonia (Tallinn) + UK. Passes US-federal default policy (Estonia NATO+EU; UK Five Eyes ally).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active but on slower cadence (~3 months from cutoff); ROS-adjacent infrastructure focus.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; sidewalk-delivery platform-class + urban-public-space deployment-context + closed-stack engagement-layer declaration Spec RFCs queued.
- Reference runtime: future `reference/delivery-runtime/StarshipBagReaderAdapter` is a candidate; engagement at the perception-replay layer rather than full-stack adapter.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Closed-robot-stack constraint** — URML's adapter cannot dispatch primitives onto Starship's actual delivery robot. Engagement is at the data/infrastructure boundary.
- **Multiple Spec-RFC prerequisites** (sidewalk-delivery class, urban-public-space deployment, closed-stack engagement-layer).
- **First-vertical novelty** — URML has no prior delivery-robot engagement to compose with.

## Alternatives considered

1. **Skip Starship as the actual robot stack is closed.** Rejected. The bag-reader infrastructure is a legitimate engagement entry, and Move-15 research surfaced this as the only viable delivery-robot engagement.
2. **Bundle Starship with sibling delivery candidates (Serve Robotics RFC-0195).** Rejected. Per-vendor RFCs let conversation thread per maintainer group.
3. **Engage Starship via their developer portal off-GitHub.** Possible if maintainers redirect; URML's outreach is GitHub-first.

## Prior art

- [`starship-technologies/bag_rdr`](https://github.com/starship-technologies/bag_rdr) — the upstream ROS-bag reader (engagement anchor).
- [RFC-0195 (Serve Robotics Model-Optimizer)](0195-serve-robotics-outreach.md) — sibling Move-15 sidewalk-delivery RFC (Uber spinoff lineage).
- URML's existing mobile-base fixtures (`clearpath_husky.yaml`, `turtlebot4_home_*`) — the mobile-base pattern Starship's class extends with sidewalk-delivery context.

## Unresolved questions

For the starship-technologies maintainers:

1. **Sidewalk-delivery platform-class manifest fields.** URML's v0.1 has no platform-class for delivery robots. Spec RFC queued. Manifest field expectations from the Starship perspective?
2. **Urban-public-space deployment-context declaration.** Manifest field for pedestrian-aware navigation + public-street operation + weather constraints?
3. **Bag-reader infrastructure scope.** Is `bag_rdr` the right URML engagement entry, or is there a different infrastructure-layer surface URML should target?
4. **Closed-stack engagement-layer declaration.** Should URML's manifest declare that the engagement is data/infrastructure-only (vs full-stack adapter)?
5. **Bridge home.** URML repo (`reference/delivery-runtime/StarshipBagReaderAdapter`), Starship-maintained, or external?
6. **Conformance listing.** Would Starship Technologies consider a README link to URML's compatible-runtimes registry once a working bridge ships?
7. **Anything else.**

## Implementation note

RFC-0193 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move15.yaml`](../../examples/lighthouses/outreach-move15.yaml).

## How to respond

`starship-technologies/bag_rdr` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the closed-robot-stack engagement-layer framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 29 stars, Issues enabled, last commit 2026-02-22, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (closed-robot-stack constraint, multiple Spec-RFC prerequisites, first-vertical novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Starship Technologies EE Tallinn / UK; default policy passes.
- [x] CLAUDE.md compliance check passed.
