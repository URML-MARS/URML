---
rfc: 0140
title: Amazon Science Spherical Diffusion Policy (SE(3)-equivariant DP) integration, request for comment from amazon-science maintainers
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

# RFC-0140: Amazon Science Spherical Diffusion Policy (SE(3)-equivariant DP) integration, request for comment from amazon-science maintainers

## Summary

URML does not yet ship an Amazon Spherical Diffusion Policy fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the SE(3)-equivariant diffusion-policy variant published by Amazon Science (ICML 2025) over [`amazon-science/Spherical_Diffusion_Policy`](https://github.com/amazon-science/Spherical_Diffusion_Policy) (MIT), and **requests review and feedback from the amazon-science maintainers**. No spec change.

This RFC pairs with [RFC-0142 (Stanford Diffusion Policy)](0142-stanford-diffusion-policy-outreach.md) as Amazon's group-equivariant variant on the same lineage, and [RFC-0141 (MoDE-DP)](0141-intuitive-robots-mode-diffusion-policy-outreach.md) as the second 2025-era diffusion-policy contribution. The three together inform URML's queued diffusion-policy-class Spec RFC + the SE(3)-equivariance schema-extension question.

## Motivation

Amazon Science published a vendor-direct ICML 2025 paper introducing SE(3)-equivariant constraints on diffusion-policy architectures, with real-robot demonstrations. The repo at [`amazon-science/Spherical_Diffusion_Policy`](https://github.com/amazon-science/Spherical_Diffusion_Policy) (MIT, 42 stars, Issues enabled, last commit `2025-07-08`) is the vendor-direct surface.

The distinct contribution is **group equivariance** — the policy respects the SE(3) symmetry of 3D rigid-body transformations, which means the same action applied to a rotated scene yields the rotated action. This is structurally relevant to URML because URML's manifest declares mobility / actuator geometry; a group-equivariant policy interacts with the manifest's coordinate-frame declarations in a way URML does not yet reason about.

Engagement is light-touch (42 stars is modest, vendor-direct but not high-velocity), and the URML-fit angle is the SE(3)-equivariance schema-extension question.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `amazon_spherical_dp_cell.yaml` fixture)

| URML field | Maps to Spherical-DP attribute |
|---|---|
| `name` | Deployment handle (`amazon_spherical_dp_default`) |
| `controller_class: custom` (`spherical_diffusion_policy`) | Declares the SE(3)-equivariant diffusion policy is in the loop |
| `controller_class: custom` (`equivariance: se3`) | Declares the group-equivariance class |
| `controller_class: custom` (`action_horizon`) | Multi-step action chunk |
| `controller_class: custom` (`coordinate_frame_alignment`) | Declares the manifest's coordinate-frame must align with the policy's input frame |

### What URML v0.1 does not yet express for Spherical-DP

1. **SE(3) / group-equivariance declaration.** URML's v0.1 manifest does not today declare which symmetry classes a learned controller respects. A Spec RFC adding `equivariance_class` (with values `none / se3 / so3 / equivariant_custom`) is queued; this is the schema-extension specific contribution of Spherical-DP.
2. **Diffusion-policy class declaration.** Shared gap with RFC-0141 / RFC-0142.
3. **Coordinate-frame alignment between manifest and policy.** URML's manifest declares actuator-frame; the policy expects input-frame alignment. The composition is not today first-class.

### Compatibility notes

- **Vendor org.** [`amazon-science`](https://github.com/amazon-science) — vendor-direct.
- **Flagship repo.** [`amazon-science/Spherical_Diffusion_Policy`](https://github.com/amazon-science/Spherical_Diffusion_Policy) — MIT, 42 stars, Issues enabled, last commit 2025-07-08 (`>10 months` stale from 2026-05-28; vendor-direct but modest cadence).
- **Origin.** Amazon Science, Santa Clara, CA, US. Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Vendor-direct ICML 2025 publication; modest GitHub cadence (42 stars, paper-anchored repos often plateau).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; group-equivariance + diffusion-policy class Spec RFCs queued in parallel.
- Reference runtime: future `reference/vla-bridge/SphericalDPBridge` is a candidate; URML's bridge declares the equivariance class to the manifest.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Modest GitHub cadence** (42 stars, `>10 months` stale). Paper-anchored repos often plateau; engagement may be light.
- **SE(3) equivariance is novel schema territory.** URML's manifest is not group-equivariance-aware in v0.1; Spec RFC for equivariance-class declaration is queued.
- **Diffusion-policy class Spec RFC prerequisite** (shared with RFC-0141 / RFC-0142).

## Alternatives considered

1. **Skip Spherical-DP as duplicate with Stanford DP.** Rejected. The SE(3)-equivariance contribution is distinct and the schema-extension question is specific to this variant.
2. **Bundle Spherical-DP + MoDE-DP + Stanford-DP into one diffusion-policy RFC.** Rejected. Per-vendor RFCs let each thread carry its own engagement state.
3. **Defer until equivariance Spec RFC lands.** Rejected. Amazon Science feedback informs the Spec RFC.

## Prior art

- [`amazon-science/Spherical_Diffusion_Policy`](https://github.com/amazon-science/Spherical_Diffusion_Policy) — the upstream repo.
- [RFC-0142 (Stanford Diffusion Policy)](0142-stanford-diffusion-policy-outreach.md) — foundational DP that Spherical-DP extends.
- [RFC-0141 (Intuitive Robots MoDE-DP)](0141-intuitive-robots-mode-diffusion-policy-outreach.md) — sibling 2025-era DP variant.
- [RFC-0139 (Octo)](0139-octo-outreach.md) — Move-11 generalist diffusion-transformer policy.

## Unresolved questions

For the amazon-science Spherical-DP maintainers:

1. **Repository roadmap.** Is `amazon-science/Spherical_Diffusion_Policy` planned for continued iteration, or is the published-paper-and-checkpoint posture the steady state?
2. **Equivariance-class manifest fields.** URML's v0.1 has no `equivariance_class` declaration. A Spec RFC adding it is queued. What manifest fields would a Spherical-DP deployment expect (group-class, basis representation, equivariance-loss-vs-architecture distinction)?
3. **Coordinate-frame alignment.** Should URML's manifest declare the coordinate-frame the policy expects, or is that always envelope-side?
4. **Diffusion-policy class declaration.** Shared with RFC-0141 / RFC-0142. Manifest field expectations from Amazon's perspective?
5. **Bridge home.** URML repo (`reference/vla-bridge/`), Amazon-maintained, or external?
6. **Conformance listing.** Would Amazon Science consider a README link to URML's compatible-runtimes registry once a working bridge ships?
7. **Anything else.**

## Implementation note

RFC-0140 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`amazon-science/Spherical_Diffusion_Policy` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 42 stars, Issues enabled, last commit 2025-07-08, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (modest cadence, equivariance schema novelty, diffusion-policy Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Amazon Science US (Santa Clara); default policy passes.
- [x] CLAUDE.md compliance check passed.
