---
rfc: 0187
title: 1X Technologies (EVE / NEO humanoid) integration, request for comment from 1x-technologies maintainers
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

# RFC-0187: 1X Technologies (EVE / NEO humanoid) integration

## Summary

URML does not yet ship a 1X-specific manifest fixture or adapter beyond the existing `neo_biped` fixture stub. This RFC documents the proposed URML v0.1 capability-manifest mapping for 1X Technologies' EVE and NEO humanoid platforms over [`1x-technologies/eve-ros2-examples`](https://github.com/1x-technologies/eve-ros2-examples) (Apache-2.0), and **requests review and feedback from the 1x-technologies maintainers**. No spec change.

**This is the only commercial humanoid OEM with vendor-direct active public robot code that URML's Move-14 research surfaced.** Apptronik, Sanctuary AI, Figure AI, Tesla Optimus, Agility Robotics, and Boston Dynamics Atlas all lack engageable public surfaces (full audit in [`move14-research-2026-05-28.md`](../../examples/lighthouses/move14-research-2026-05-28.md)). 1X's vendor-direct ROS 2 examples make this RFC possible at all.

## Motivation

1X Technologies AS (Oslo, Norway) makes the EVE (wheeled humanoid) and NEO (bipedal humanoid) platforms. URML's existing `neo_biped` manifest fixture (per RFC-0009 mobility specialization) declares NEO as a bipedal humanoid class; this RFC closes the loop with the upstream surface.

Repo at [`1x-technologies/eve-ros2-examples`](https://github.com/1x-technologies/eve-ros2-examples) (Apache-2.0, 6 stars, Issues enabled, last commit `2026-01-12`, **not archived**). Modest star count (6) reflects a developer-program-only posture — 1X distributes hardware in a managed program rather than mass-market — but the vendor-direct surface is real and Apache-2.0.

The URML-fit framing is **humanoid-fixture validation upstream**. URML's `neo_biped` fixture exists today; engagement validates / refines it with the vendor maintainer. Same posture URML adopted with `microbit_edu` (RFC-0172 micro:bit Foundation).

## Detailed design

### URML v0.1 capability-manifest mapping (refines existing `neo_biped.yaml` fixture)

| URML field | Maps to 1X attribute |
|---|---|
| `name` | Specific platform (`1x_eve_wheeled`, `1x_neo_biped`) |
| `mobility.drive_type: biped` (NEO) / `omnidirectional` (EVE) | URML's v0.1 mobility-class enum |
| `actuators` | Full-body articulation per 1X spec |
| `controller_class: custom` (`1x_proprietary_neural_network_controller`) | 1X uses neural-network-trained controllers (signaling-public material) |
| `developer_program_class: custom` (`1x_managed`) | 1X's managed-program distribution model |

### What URML v0.1 does not yet express for 1X

1. **Humanoid platform refinement.** URML's `neo_biped` fixture is a stub; this RFC asks the vendor to refine the manifest fields (DoF inventory, sensor inventory, controller-class declaration).
2. **EVE wheeled-humanoid topology.** URML's mobility enum has `omnidirectional` but doesn't today distinguish wheeled-base + humanoid-torso as a composite topology (similar gap to RFC-0184 Stretch but with humanoid upper-body).
3. **Neural-network controller declaration.** 1X's controllers are NN-trained (per public materials); URML's manifest cannot today declare learned-controller class for a humanoid (sibling gap to the VLA declarations from Move-11 RFC-0138 OpenVLA / RFC-0139 Octo / RFC-0151 CogACT).
4. **Managed-program distribution class.** 1X distributes via managed program rather than commodity hardware; URML's manifest cannot today declare this deployment posture.

### Compatibility notes

- **Vendor org.** [`1x-technologies`](https://github.com/1x-technologies) — 1X Technologies AS, Oslo, Norway.
- **Flagship repo.** [`1x-technologies/eve-ros2-examples`](https://github.com/1x-technologies/eve-ros2-examples) — Apache-2.0, 6 stars, Issues enabled, last commit 2026-01-12, **not archived**.
- **Companion repos.** 24 total public repos at `1x-technologies` org.
- **Origin.** 1X Technologies AS, Oslo, Norway (NO). Passes US-federal default policy (NATO ally).
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Modest star count (6) is developer-program-only posture; vendor-direct is the durability signal.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; humanoid platform refinement + wheeled-humanoid composite topology + NN-controller class + managed-program distribution-class Spec RFCs queued.
- Reference runtime: future `reference/humanoid-runtime/OneXAdapter` is a candidate.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multiple Spec-RFC prerequisites** (humanoid refinement, wheeled-humanoid topology, NN-controller class, managed-program distribution).
- **Modest engagement surface.** 6 stars + developer-program-only posture mean engagement is light-touch.
- **Existing `neo_biped` fixture cross-link.** Any maintainer feedback might prompt fixture refinements — that's positive but is follow-up scope.

## Alternatives considered

1. **Cross-citation only.** Considered. Vendor-direct + Apache-2.0 + active argues for full manifest mapping; cross-citation alone is too thin given URML's existing fixture.
2. **Engage 1X via developer-program channels off GitHub.** Possible. URML's outreach is GitHub-first; if maintainers redirect, URML follows.
3. **Skip 1X as overlapping with URML's `neo_biped` fixture.** Rejected. The fixture is URML-side declaration; the engagement validates upstream.

## Prior art

- [`1x-technologies/eve-ros2-examples`](https://github.com/1x-technologies/eve-ros2-examples) — the upstream ROS 2 examples.
- URML's existing `neo_biped.yaml` fixture stub — the URML-side declaration this RFC formalizes.
- URML's other humanoid fixtures (`apollo_biped`, `digit_biped`, `figure_biped`, `optimus_biped`) — URML-side fixtures that exist without engageable upstream surfaces (Move-14 Tier C audit).
- [RFC-0138 (OpenVLA)](0138-openvla-outreach.md), [RFC-0139 (Octo)](0139-octo-outreach.md) — Move-11 VLA RFCs sharing the learned-controller manifest gap.

## Unresolved questions

For the 1x-technologies maintainers:

1. **Humanoid platform refinement.** URML's `neo_biped` fixture sketches the NEO manifest mapping. What fields would 1X refine / add (DoF inventory, sensor inventory)?
2. **EVE wheeled-humanoid topology.** Wheeled-base + humanoid-torso composite — manifest declaration shape?
3. **NN-controller class declaration.** Should URML's manifest declare which NN-controller class is active (similar shape to URML's VLA RFCs from Move #11)?
4. **Managed-program distribution-class.** Should URML's manifest declare 1X's managed-program distribution model?
5. **Adapter home.** URML repo (`reference/humanoid-runtime/OneXAdapter`), 1X-maintained `1x-technologies/eve-urml-bridge`, or both?
6. **Conformance listing.** Would 1X Technologies consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0187 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml).

## How to respond

`1x-technologies/eve-ros2-examples` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 6 stars, Issues enabled, last commit 2026-01-12, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multiple Spec-RFC prerequisites, modest engagement surface, existing fixture cross-link scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: 1X Technologies AS NO Oslo; default policy passes.
- [x] CLAUDE.md compliance check passed.
