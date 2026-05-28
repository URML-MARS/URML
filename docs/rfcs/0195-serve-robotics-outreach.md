---
rfc: 0195
title: Serve Robotics (sidewalk delivery, Uber spinoff) integration, request for comment from serve-robotics maintainers
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

# RFC-0195: Serve Robotics (sidewalk delivery, Uber spinoff) integration — light-touch engagement (completes Move-15)

## Summary

URML does not yet ship a Serve Robotics manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest **cross-citation** for Serve Robotics — the Uber-spinoff sidewalk-delivery company — over [`serve-robotics/Model-Optimizer`](https://github.com/serve-robotics/Model-Optimizer) (Apache-2.0), and **requests review and feedback from the serve-robotics maintainers**. Engagement is light-touch given the fork-heavy public surface (minimal vendor-original engageable code). No spec change.

**Completes the 5 Move-15 engageable RFCs.**

This RFC is the **sidewalk-delivery sibling** to RFC-0193 Starship Technologies. Both engage delivery-class robotics at the infrastructure-only layer because both companies' actual delivery-robot stacks are closed.

## Motivation

Serve Robotics (US, founded 2017 as Postmates X, spun off from Uber) operates sidewalk-delivery robots in US urban markets. The org has 24 public GitHub repos — but on inspection these are predominantly forks (Model-Optimizer, horde, libOpenDRIVE, unreal-mcp, xviz, and similar community-fork copies). Minimal vendor-original engageable code.

Engagement anchor at [`serve-robotics/Model-Optimizer`](https://github.com/serve-robotics/Model-Optimizer) (Apache-2.0, fork, last commit `2026-05-22` active).

URML's engagement angle here is honest light-touch. The sidewalk-delivery class is real and worth a manifest declaration; Serve's public surface doesn't carry adapter-grade engagement weight, but the engagement asks where vendor-original engagement surface exists.

## Detailed design

### URML v0.1 capability-manifest mapping (cross-citation framing for `serve_sidewalk_delivery_cell.yaml` fixture)

| URML field | Maps to Serve Robotics attribute |
|---|---|
| `name` | Generic identifier (`serve_robotics_sidewalk_delivery`) |
| `mobility.drive_type: differential` | Wheeled differential mobile base |
| `platform_class: custom` (`sidewalk_delivery`) | Same shared declaration as RFC-0193 Starship |
| `deployment_context: custom` (`urban_us_public_space`) | US-urban deployment context |
| `payload_class: custom` (`food_delivery_locked_compartment`) | Food-delivery use case |
| `engagement_surface_quality: custom` (`fork_heavy_minimal_original`) | Honest manifest declaration of the engagement-surface quality |

### What URML v0.1 does not yet express for Serve Robotics

1. **Sidewalk-delivery platform-class declaration.** Same shared gap as RFC-0193 Starship Technologies. Spec RFC queued.
2. **Engagement-surface-quality declaration.** URML's manifest cannot today declare that the public engagement surface is fork-heavy / minimal-original — relevant for downstream operator awareness of engagement depth. Novel manifest territory.

### Compatibility notes

- **Vendor org.** [`serve-robotics`](https://github.com/serve-robotics) — Serve Robotics, US (Uber spinoff).
- **Engagement anchor.** [`serve-robotics/Model-Optimizer`](https://github.com/serve-robotics/Model-Optimizer) — Apache-2.0, fork, last commit 2026-05-22 active.
- **Origin.** Serve Robotics, US (Redwood City CA). Passes US-federal default policy.
- **License fit.** Apache-2.0 on the public-fork surface cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Fork-heavy public surface signals engagement-channel mismatch — vendor-original engagement may live off-GitHub.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; sidewalk-delivery platform-class Spec RFC (shared with RFC-0193) + engagement-surface-quality declaration Spec RFC queued.
- Reference runtime: cross-citation framing only — public surface doesn't carry adapter-grade engagement.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Minimal vendor-original public surface.** Engagement is light-touch by necessity; URML can't dispatch primitives onto Serve's actual robot stack from the public surface.
- **Engagement-surface-quality declaration is novel manifest territory.**
- **Sidewalk-delivery class Spec RFC prerequisite** (shared with RFC-0193).

## Alternatives considered

1. **Skip Serve Robotics as the surface is fork-heavy.** Considered. Tier B framing with explicit fork-heavy acknowledgement is the honest middle path — engagement asks where vendor-original surface exists.
2. **Bundle Serve with sibling Move-15 delivery RFCs (Starship RFC-0193).** Rejected. Per-vendor RFCs.
3. **Engage Serve via off-GitHub developer channels.** Possible if maintainers redirect; URML's outreach is GitHub-first.

## Prior art

- [`serve-robotics/Model-Optimizer`](https://github.com/serve-robotics/Model-Optimizer) — the engagement anchor.
- [RFC-0193 (Starship Technologies)](0193-starship-technologies-outreach.md) — sibling Move-15 sidewalk-delivery RFC sharing the platform-class Spec-RFC gap.

## Unresolved questions

For the serve-robotics maintainers:

1. **Vendor-original engagement surface.** Where does Serve's vendor-original code (vs forks) live? Off-GitHub developer portal, private repos, or fork-heavy posture is intentional?
2. **Sidewalk-delivery platform-class manifest fields.** Same shared question as RFC-0193 Starship.
3. **Engagement-surface-quality declaration.** Should URML's manifest declare the engagement-surface quality (vendor-original vs fork-heavy vs closed-stack) for downstream operator awareness?
4. **Bridge home.** Cross-citation only (recommended given fork-heavy surface), URML repo, or external?
5. **Conformance listing.** If vendor-original surface emerges, would Serve Robotics consider a README link to URML's compatible-runtimes registry?
6. **Anything else.**

## Implementation note

RFC-0195 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move15.yaml`](../../examples/lighthouses/outreach-move15.yaml). **Completes the 5 Move-15 engageable RFCs.**

## How to respond

`serve-robotics/Model-Optimizer` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the fork-heavy-public-surface framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, fork, active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (minimal vendor-original surface, engagement-surface-quality novelty, Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Serve Robotics US Redwood City; default policy passes.
- [x] CLAUDE.md compliance check passed.
