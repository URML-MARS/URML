---
rfc: 0142
title: Stanford Diffusion Policy (foundational DP, Chi et al) integration, request for comment from real-stanford maintainers
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

# RFC-0142: Stanford Diffusion Policy (foundational DP, Chi et al) integration, request for comment from real-stanford maintainers

## Summary

URML does not yet ship a Stanford Diffusion Policy fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the foundational Diffusion Policy paper from Stanford / Columbia / TRI (Cheng Chi et al) over [`real-stanford/diffusion_policy`](https://github.com/real-stanford/diffusion_policy) (MIT), and **requests review and feedback from the real-stanford maintainers**. No spec change.

This RFC is the architectural-reference companion to [RFC-0140 (Amazon Spherical-DP)](0140-amazon-spherical-diffusion-policy-outreach.md) and [RFC-0141 (MoDE-DP)](0141-intuitive-robots-mode-diffusion-policy-outreach.md). Stanford Diffusion Policy is the foundational paper the 2025-era variants extend; URML's outreach engages the lineage at the canonical root.

## Motivation

Stanford / Columbia / TRI's Cheng Chi et al published the foundational Diffusion Policy paper (RSS 2023 best paper). The repo at [`real-stanford/diffusion_policy`](https://github.com/real-stanford/diffusion_policy) (MIT, 4.2k stars, Issues enabled, last commit `2024-12-24`) is the architectural reference for every downstream DP variant.

The repo was **referenced in Move-2 RFC-0054 (TRI-LBM) notes as prior art** but never directly engaged. Move #11 corrects this; Diffusion Policy deserves its own RFC because the architecture-reference engagement is distinct from the TRI-LBM model-program engagement.

Push-date staleness is real (`>17 months` from 2026-05-28); the architecture is foundational rather than actively-iterating.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `stanford_dp_cell.yaml` fixture)

| URML field | Maps to Stanford DP attribute |
|---|---|
| `name` | Deployment handle (`stanford_dp_default`) |
| `controller_class: custom` (`diffusion_policy`) | Declares the foundational DP architecture is in the loop |
| `controller_class: custom` (`diffusion_steps`) | Number of denoising steps |
| `controller_class: custom` (`action_horizon`) | Multi-step action chunk |
| `controller_class: custom` (`input_modalities`) | Image-only or state+image |
| `controller_class: custom` (`backbone`) | UNet1D / Transformer / etc. |

### What URML v0.1 does not yet express for Stanford DP

1. **Diffusion-policy class declaration.** URML's manifest does not today declare diffusion-step count, action-horizon, or backbone class. Spec RFC for diffusion-policy class declaration queued; shared gap with RFC-0140 (Spherical-DP equivariance angle) and RFC-0141 (MoDE MoE-routing angle).
2. **Action-chunk horizon declaration.** Same gap as RFC-0139 Octo.
3. **Closed-form vs learned backbone declaration.** URML's manifest does not today distinguish; diffusion policies are learned-only.

### Compatibility notes

- **Vendor / lab.** Stanford / Columbia / TRI Cheng Chi et al; research-lab-direct.
- **Flagship repo.** [`real-stanford/diffusion_policy`](https://github.com/real-stanford/diffusion_policy) — MIT, 4.2k stars, Issues enabled, last commit 2024-12-24 (`>17 months` stale; foundational architecture).
- **Origin.** Stanford / Columbia / TRI, US. Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Architectural reference; foundational paper anchor.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; diffusion-policy class declaration Spec RFC queued in parallel (shared with RFC-0140 / RFC-0141).
- Reference runtime: future `reference/vla-bridge/DiffusionPolicyBridge` is a candidate; URML's bridge composes above the validated manifest.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **>17 months staleness.** Engagement may yield slow / no response; foundational-paper-anchored repos often plateau.
- **Diffusion-policy class Spec RFC prerequisite** (shared with RFC-0140 / RFC-0141).
- **Move-2 RFC-0054 cross-reference.** Stanford DP was named as prior art in the TRI-LBM RFC; direct engagement now is a slight overlap with TRI's existing thread but the architecture surface is distinct.

## Alternatives considered

1. **Skip Stanford DP because it's already cross-cited in RFC-0054.** Rejected. Cross-citation in notes ≠ direct engagement; the architecture authors deserve their own thread for the diffusion-policy class Spec RFC input.
2. **Bundle Stanford DP + Spherical-DP + MoDE-DP into one diffusion-policy RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.
3. **Engage Cheng Chi directly via email.** Considered. URML's outreach is repo-direct first; email is fallback if repo engagement stalls.

## Prior art

- [`real-stanford/diffusion_policy`](https://github.com/real-stanford/diffusion_policy) — the upstream repo.
- [RFC-0054 (TRI-LBM)](0054-tri-lbm-outreach.md) — Move-2 RFC where Stanford DP was cross-cited as prior art.
- [RFC-0140 (Amazon Spherical-DP)](0140-amazon-spherical-diffusion-policy-outreach.md), [RFC-0141 (MoDE-DP)](0141-intuitive-robots-mode-diffusion-policy-outreach.md) — Move-11 diffusion-policy lineage siblings.

## Unresolved questions

For the real-stanford / Cheng Chi et al maintainers:

1. **Repository status.** Is `real-stanford/diffusion_policy` actively maintained, dormant-but-supported, or has the active development moved to a successor (`real-stanford/diffusion_policy_v2`, etc.)?
2. **Diffusion-policy class manifest fields.** URML's v0.1 has no `diffusion_policy` declaration. A Spec RFC adding it is queued, shared with RFC-0140 (SE(3) angle) and RFC-0141 (MoE angle). What manifest fields would the foundational-DP perspective expect (diffusion-step count, action-horizon, backbone class, input-modality declaration)?
3. **Action-chunk horizon semantics.** Same question as RFC-0139 Octo. Manifest declaration shape?
4. **Bridge home.** URML repo (`reference/vla-bridge/`), Stanford-maintained, or external?
5. **Conformance listing.** Would the maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships?
6. **Anything else.**

## Implementation note

RFC-0142 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml). Cross-reference noted to [RFC-0054 TRI-LBM](0054-tri-lbm-outreach.md) prior-art citation.

## How to respond

`real-stanford/diffusion_policy` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of push-date staleness.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 4.2k stars, Issues enabled, last commit 2024-12-24, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (>17mo staleness, diffusion-policy Spec-RFC prerequisite, Move-2 cross-reference noted).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Stanford / Columbia / TRI US; default policy passes.
- [x] CLAUDE.md compliance check passed.
