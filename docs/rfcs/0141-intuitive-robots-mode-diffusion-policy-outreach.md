---
rfc: 0141
title: Intuitive Robots MoDE Diffusion Policy (mixture-of-experts diffusion transformer) integration, request for comment from intuitive-robots maintainers
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

# RFC-0141: Intuitive Robots MoDE Diffusion Policy (MoE diffusion transformer) integration, request for comment from intuitive-robots maintainers

## Summary

URML does not yet ship a MoDE Diffusion Policy fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for MoDE (Mixture-of-Experts Diffusion Policy), the ICLR 2025 contribution from Karlsruhe Institute of Technology (DE) and MIT (US), over [`intuitive-robots/MoDE_Diffusion_Policy`](https://github.com/intuitive-robots/MoDE_Diffusion_Policy) (MIT), and **requests review and feedback from the intuitive-robots maintainers**. No spec change.

This RFC pairs with [RFC-0140 (Amazon Spherical-DP)](0140-amazon-spherical-diffusion-policy-outreach.md) and [RFC-0142 (Stanford Diffusion Policy)](0142-stanford-diffusion-policy-outreach.md) on URML's diffusion-policy-class Spec-RFC gap. MoDE's distinct contribution is **mixture-of-experts routing** on top of the diffusion-transformer backbone.

## Motivation

The intuitive-robots group at Karlsruhe Institute of Technology (KIT, Germany) collaborated with MIT (US) on the MoDE architecture, published at ICLR 2025. Repo at [`intuitive-robots/MoDE_Diffusion_Policy`](https://github.com/intuitive-robots/MoDE_Diffusion_Policy) (MIT, 122 stars, Issues enabled, last commit `2025-05-16` — active within URML's 6-month window from 2026-05-28).

The distinct URML-side contribution: **MoE routing declaration**. URML's manifest does not today declare which expert is active or how routing happens; MoDE introduces this as a structural property of the controller. Worth a separate RFC because the routing declaration is independent of the equivariance question RFC-0140 surfaces.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mode_dp_cell.yaml` fixture)

| URML field | Maps to MoDE attribute |
|---|---|
| `name` | Deployment handle (`mode_dp_default`) |
| `controller_class: custom` (`mode_diffusion_policy`) | Declares the MoE-DT policy is in the loop |
| `controller_class: custom` (`expert_count`) | Number of experts in the mixture |
| `controller_class: custom` (`routing_class`) | Routing class (`token_routing` / `task_routing` / etc.) |
| `controller_class: custom` (`action_horizon`) | Multi-step action chunk |
| `controller_class: custom` (`input_modalities`) | RGB / language / proprioception modalities consumed |

### What URML v0.1 does not yet express for MoDE

1. **MoE routing declaration.** URML's manifest does not today declare which experts a learned controller uses or how routing happens. Spec RFC for MoE routing declaration is queued; MoDE is the natural vendor input.
2. **Diffusion-policy class declaration.** Shared gap with RFC-0140 / RFC-0142.
3. **Multi-collaborator origin declaration.** MoDE is a KIT-DE + MIT-US collaboration; URML's manifest origin field is single-country. Honest cross-citation of multi-origin research artifacts is a minor manifest schema gap.

### Compatibility notes

- **Vendor org.** [`intuitive-robots`](https://github.com/intuitive-robots) — KIT research group.
- **Flagship repo.** [`intuitive-robots/MoDE_Diffusion_Policy`](https://github.com/intuitive-robots/MoDE_Diffusion_Policy) — MIT, 122 stars, Issues enabled, last commit 2025-05-16 (active).
- **Origin.** Karlsruhe Institute of Technology (Germany, DE) + Massachusetts Institute of Technology (US). Passes US-federal default policy (DE = NATO allied).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active surface (12 days since last commit at research time); ICLR 2025 publication anchor.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; MoE routing + diffusion-policy class Spec RFCs queued in parallel.
- Reference runtime: future `reference/vla-bridge/MoDEBridge` is a candidate; URML's bridge declares the expert count + routing class to the manifest.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **MoE routing is novel schema territory.** URML's manifest is not MoE-aware in v0.1.
- **Diffusion-policy class Spec RFC prerequisite** (shared with RFC-0140 / RFC-0142).
- **Multi-origin research artifact.** KIT-DE + MIT-US collaboration; URML's manifest origin field is single-country (minor schema gap noted honestly).

## Alternatives considered

1. **Skip MoDE as duplicate with Stanford DP / Spherical-DP.** Rejected. The MoE-routing contribution is structurally distinct from both.
2. **Bundle MoDE + Spherical-DP + Stanford DP into one diffusion-policy RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.
3. **Engage KIT broader (intuitive-robots group has other repos).** Considered. Per-paper-repo engagement is the cleaner shape; broader-group engagement is future work.

## Prior art

- [`intuitive-robots/MoDE_Diffusion_Policy`](https://github.com/intuitive-robots/MoDE_Diffusion_Policy) — the upstream repo.
- [RFC-0140 (Amazon Spherical-DP)](0140-amazon-spherical-diffusion-policy-outreach.md), [RFC-0142 (Stanford DP)](0142-stanford-diffusion-policy-outreach.md) — Move-11 diffusion-policy lineage siblings.
- [RFC-0139 (Octo)](0139-octo-outreach.md) — Move-11 generalist diffusion-transformer policy.

## Unresolved questions

For the intuitive-robots MoDE maintainers:

1. **MoE routing declaration manifest fields.** URML's v0.1 has no `routing_class` / `expert_count` declarations. A Spec RFC adding them is queued. What manifest fields would a MoDE deployment expect?
2. **Diffusion-policy class declaration.** Shared with RFC-0140 / RFC-0142.
3. **Multi-collaborator-origin declaration.** Should URML's manifest declare multi-origin research artifacts honestly (origin: `DE+US` rather than single-country)?
4. **Bridge home.** URML repo (`reference/vla-bridge/`), KIT-maintained, or external?
5. **Conformance listing.** Would the intuitive-robots maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships?
6. **Anything else.**

## Implementation note

RFC-0141 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`intuitive-robots/MoDE_Diffusion_Policy` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 122 stars, Issues enabled, last commit 2025-05-16 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (MoE schema novelty, diffusion-policy Spec-RFC prerequisite, multi-origin gap).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: KIT DE + MIT US; default policy passes.
- [x] CLAUDE.md compliance check passed.
