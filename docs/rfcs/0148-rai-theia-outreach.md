---
rfc: 0148
title: RAI Institute Theia (vision foundation model) integration, request for comment from rai-opensource maintainers
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

# RFC-0148: RAI Institute Theia (vision foundation model) integration, request for comment from rai-opensource maintainers

## Summary

URML does not yet ship a Theia manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest cross-citation for Theia — RAI Institute's vision foundation model for robotics — over [`rai-opensource/Theia`](https://github.com/rai-opensource/Theia), and **requests review and feedback from the rai-opensource maintainers**. **License clarification ask:** the repo's license is listed as "Other" by the GitHub API; an explicit OSI declaration is the gating ask. No spec change.

This RFC is **distinct from RFC-0043 (Spot / rai-opensource COLLABORATOR engagement)** in Move-2. RFC-0043 engaged Tim Perkins (rai-opensource COLLABORATOR, *not* Boston Dynamics-employed); Theia is a separate RAI repo, vendor-direct from the Boston Dynamics AI Institute.

## Motivation

`rai-opensource/Theia` is RAI Institute's vision foundation model for robotics. 276 stars, Issues enabled, last commit `2025-11-06` (~7mo from 2026-05-28 cutoff), **not archived**. RAI Institute (Boston Dynamics AI Institute) is a vendor-direct surface; Theia is the perception foundation model URML's adapter could declare as the vision substrate.

The URML-fit framing is cross-citation: Theia is a learned vision substrate; URML's manifest declares which vision-foundation-model class is active; the actual model weights / inference call live outside URML.

License clarification is the gating fact. Apache-2.0 / MIT / BSD compatible would unlock adapter-grade bundling; "Other" blocks Apache-2.0 downstream reuse until clarified.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `rai_theia_cell.yaml` fixture, cross-citation framing)

| URML field | Maps to Theia attribute |
|---|---|
| `name` | Deployment handle (`rai_theia_default`) |
| `vision_substrate: custom` (`rai_theia`) | Declares Theia is the vision foundation model |
| `vision_substrate.input_modality: rgb` | Theia consumes RGB |
| `vision_substrate.output: visual_features` | Theia emits visual feature representations |

### What URML v0.1 does not yet express for Theia

1. **Vision-foundation-model substrate declaration.** URML's manifest does not today have a `vision_substrate` field. Spec RFC queued.
2. **Feature-representation output declaration.** Vision foundation models emit representations (embeddings, feature maps); URML's manifest does not today declare downstream-consumable feature representations.
3. **License clarification.** "Other" upstream blocks Apache-2.0 reuse.

### Compatibility notes

- **Vendor / lab.** [`rai-opensource`](https://github.com/rai-opensource) — Boston Dynamics AI Institute (RAI Institute) vendor-direct surface.
- **Flagship repo.** [`rai-opensource/Theia`](https://github.com/rai-opensource/Theia) — license "Other" (clarification ask), 276 stars, Issues enabled, last commit 2025-11-06, **not archived**.
- **Origin.** RAI Institute (US). Passes US-federal default policy.
- **License fit.** Pending clarification.
- **Maintainer signal.** Vendor-direct; RAI Institute publishes research code via this org.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; vision-foundation-model substrate declaration Spec RFC queued.
- Reference runtime: cross-citation framing recommended pending license clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate.** "Other" upstream license blocks Apache-2.0 downstream reuse.
- **Vision-foundation-model Spec RFC prerequisite.**
- **Move-2 RFC-0043 thread distinction.** Spot/rai-opensource COLLABORATOR engagement is on a separate repo and separate maintainer; this RFC must be explicit that it's not a Spot follow-up.

## Alternatives considered

1. **Bundle RAI Theia + VLFM (RFC-0149) into one RAI-Institute RFC.** Considered. Per-repo RFCs let conversation thread per flagship; VLFM is sibling RFC.
2. **Defer until license clarifies.** Rejected. The RFC engagement is the license-clarification ask.
3. **Cross-citation only with no manifest mapping.** Considered. Manifest mapping is the artifact maintainers can evaluate; cross-citation alone is too thin.

## Prior art

- [`rai-opensource/Theia`](https://github.com/rai-opensource/Theia) — the upstream repo.
- [RFC-0043 (Spot)](0043-spot-outreach.md) — Move-2 engaged Tim Perkins on rai-opensource COLLABORATOR side; different repo + different maintainer.
- [RFC-0149 (RAI VLFM)](0149-rai-vlfm-outreach.md) — sibling RAI Institute RFC.

## Unresolved questions

For the rai-opensource Theia maintainers:

1. **License clarification.** Can `rai-opensource/Theia` get an explicit OSI license declaration (Apache-2.0 / MIT / BSD-3-Clause)?
2. **Vision-foundation-model substrate manifest fields.** URML's v0.1 has no `vision_substrate` declaration. Spec RFC queued. Manifest field expectations from the Theia perspective?
3. **Engagement-thread distinction from Spot/rai-opensource (RFC-0043).** Should URML treat the two as completely separate or as related RAI engagements?
4. **Bridge home.** Cross-citation only (recommended pending license), URML repo (`reference/vla-bridge/`), or RAI-maintained?
5. **Conformance listing.** Would RAI Institute consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

## Implementation note

RFC-0148 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`rai-opensource/Theia` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license: Other, 276 stars, Issues enabled, last commit 2025-11-06, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-clarification gate, vision-foundation-model Spec-RFC prerequisite, RFC-0043 distinction).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: RAI Institute US; default policy passes.
- [x] CLAUDE.md compliance check passed.
