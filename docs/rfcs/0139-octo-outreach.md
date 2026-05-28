---
rfc: 0139
title: Octo (UC Berkeley generalist diffusion-transformer policy) integration, request for comment from octo-models maintainers
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

# RFC-0139: Octo (UC Berkeley generalist diffusion-transformer policy) integration, request for comment from octo-models maintainers

## Summary

URML does not yet ship an Octo manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Octo, the UC Berkeley generalist diffusion-transformer policy trained on the 800k-trajectory Open X-Embodiment dataset, over [`octo-models/octo`](https://github.com/octo-models/octo) (MIT), and **requests review and feedback from the octo-models maintainers**. No spec change.

This RFC pairs with [RFC-0138 (OpenVLA)](0138-openvla-outreach.md) on URML's action-head-class Spec-RFC gap. OpenVLA and Octo are the two foundational open generalist policies from the Sergey Levine lab lineage; their architectures are distinct (autoregressive VLA vs diffusion-transformer) and both inform URML's manifest declaration of learned-controller class.

## Motivation

Octo is the UC Berkeley research-lab-direct diffusion-transformer policy. Repo at [`octo-models/octo`](https://github.com/octo-models/octo) (MIT, 1.7k stars, Issues enabled, last commit `2024-07-31` — stale per URML's 6-month rule, foundational architecture). Trained on the 800k-trajectory Open X-Embodiment dataset (URML's Move-2 RFC-0046 already engaged Open-X data; Octo is the policy trained on that data).

The push-date staleness is real but the architecture is the canonical diffusion-policy generalist. URML's outreach is light-touch and engages with explicit acknowledgement of the cadence — the RFC may itself be the nudge that reactivates the repo, or yield a vendor-redirect to a successor (`octo-2`, etc.) we cannot see from outside.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `octo_generalist_cell.yaml` fixture)

Same gap shape as RFC-0138 OpenVLA — URML's v0.1 has no native `vla_model` / learned-controller declaration. The `custom` escape-hatch covers it:

| URML field | Maps to Octo attribute |
|---|---|
| `name` | Deployment handle (`octo_small`, `octo_base`) |
| `controller_class: custom` (`diffusion_transformer_policy`) | Declares the diffusion-transformer policy is in the loop |
| `controller_class: custom` (`pretraining_data: open_x_embodiment`) | Declares the pretraining-data class (cross-link to RFC-0046) |
| `controller_class: custom` (`action_horizon`) | Declares the action-prediction horizon (Octo predicts action chunks) |
| `controller_class: custom` (`input_modalities: rgb+language`) | Declares supported input modalities |

### What URML v0.1 does not yet express for Octo

1. **Diffusion-transformer policy declaration.** Same gap shape as RFC-0138; action-head class declaration Spec RFC queued.
2. **Action-chunk horizon declaration.** Octo predicts multi-step action sequences (chunks); URML's primitive vocabulary is per-action. Manifest cannot today declare the chunk semantics.
3. **Pretraining-data provenance.** Octo's behavior is shaped by which subset of Open-X was used; URML's manifest cannot today declare this provenance.

### Compatibility notes

- **Vendor / lab.** UC Berkeley research-lab-direct (Sergey Levine lab).
- **Flagship repo.** [`octo-models/octo`](https://github.com/octo-models/octo) — MIT, 1.7k stars, Issues enabled, last commit 2024-07-31 (>22 months stale; foundational architecture).
- **Origin.** UC Berkeley, US. Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Stale push date is the engagement-risk signal; the architecture remains the open diffusion-transformer reference.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; action-head class declaration Spec RFC queued in parallel (shared with RFC-0138 / RFC-0151).
- Reference runtime: future `reference/vla-bridge/OctoBridge` is a candidate; the bridge composes above URML's `reference/llm-bridge/` similarly to OpenVLA.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Repo staleness >22 months.** Engagement may yield slow / no response, or redirect to a successor project. Engagement is light-touch and expects this.
- **Action-head Spec RFC prerequisite** (shared with RFC-0138 / RFC-0151).
- **Action-chunk-horizon semantics** are a v0.1 manifest gap.

## Alternatives considered

1. **Skip Octo as duplicate with OpenVLA.** Rejected. The diffusion-transformer architecture is structurally distinct from autoregressive VLAs; two vendor inputs sharpen the Spec RFC.
2. **Engage UC Berkeley broader (Sergey Levine lab) instead of octo-models.** Rejected. URML's outreach is repo-direct first; the Levine lab is the lineage but not the engagement surface.
3. **Bundle Octo + diffusion-policy lineage (RFC-0140 / RFC-0141 / RFC-0142) into one diffusion RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.

## Prior art

- [`octo-models/octo`](https://github.com/octo-models/octo) — the upstream repo.
- [RFC-0138 (OpenVLA)](0138-openvla-outreach.md) — sibling generalist-VLA RFC sharing the action-head-class Spec-RFC gap.
- [RFC-0046 (Open-X-Embodiment)](0046-open-x-embodiment-outreach.md) — Move-2 engaged the data; Octo is the policy trained on it.
- [RFC-0140 (Amazon Spherical-DP)](0140-amazon-spherical-diffusion-policy-outreach.md), [RFC-0141 (MoDE-DP)](0141-intuitive-robots-mode-diffusion-policy-outreach.md), [RFC-0142 (Stanford DP)](0142-stanford-diffusion-policy-outreach.md) — Move-11 diffusion-policy lineage siblings.

## Unresolved questions

For the octo-models maintainers:

1. **Repository status.** Is `octo-models/octo` actively maintained, dormant-but-supported, or has the active development moved to a successor? Where does engagement live in 2026?
2. **Action-head + action-chunk-horizon manifest fields.** URML's v0.1 has no `diffusion_transformer_policy` declaration. Manifest expectations for action-horizon, action-space, pretraining-data provenance?
3. **Bridge shape.** URML's bridge sits above Octo's output (validates against manifest pre-publish) or below the NL input (compiles to typed primitives Octo's planner consumes)? Levine lab perspective on the validator boundary?
4. **Bridge home.** URML repo (`reference/vla-bridge/`), `octo-models/octo-urml-bridge`, or external?
5. **Conformance listing.** Would Octo's maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships?
6. **Anything else.**

## Implementation note

RFC-0139 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`octo-models/octo` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of push-date staleness.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 1.7k stars, Issues enabled, last commit 2024-07-31, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (>22mo staleness, action-head Spec-RFC prerequisite, action-chunk-horizon gap).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: UC Berkeley US; default policy passes.
- [x] CLAUDE.md compliance check passed.
