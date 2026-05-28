---
rfc: 0189
title: PAL Robotics (TIAGo / TALOS / ARI) integration, request for comment from pal-robotics maintainers — canonical-engagement-surface + license-clarification asks
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

# RFC-0189: PAL Robotics (TIAGo / TALOS / ARI) integration — canonical-engagement-surface + license-clarification asks

## Summary

URML does not yet ship a PAL Robotics manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest **cross-citation** for PAL Robotics' TIAGo (mobile manipulator) + TALOS (humanoid) + ARI (social robot) over [`pal-robotics/tiago_tutorials`](https://github.com/pal-robotics/tiago_tutorials), and **requests review and feedback from the pal-robotics maintainers**. **Canonical-engagement-surface ask + license-clarification ask** are the gating items. No spec change.

## Motivation

PAL Robotics (Barcelona, Spain) is one of Europe's most established robotics OEMs — TIAGo mobile manipulator, TALOS full-body humanoid, ARI social robot, and the legacy REEM platform. URML's `cobot-runtime` and `humanoid-runtime` fixture patterns imply PAL-class support that this RFC closes the loop on.

Repo at [`pal-robotics/tiago_tutorials`](https://github.com/pal-robotics/tiago_tutorials) (no SPDX visible — clarification ask, 87 stars, Issues enabled, last commit `2024-02-29` — **stale 818 days from cutoff 2026-05-28**, **not archived**).

Two engagement asks frame this RFC:

1. **Canonical-engagement-surface ask.** PAL has multiple repos at `pal-robotics`; `tiago_tutorials` is one of many and the most-stale of the visible ones. URML's RFC asks the maintainers which repo (or off-GitHub channel) is the canonical engagement surface in 2026.
2. **License-clarification ask.** No SPDX on the tutorials repo; URML's adapter-grade reuse depends on per-surface clarity across the PAL repo catalog.

Cross-citation framing is appropriate pending those clarifications.

## Detailed design

### URML v0.1 capability-manifest mapping (cross-citation framing, planned `pal_tiago_cell.yaml` + `pal_talos_cell.yaml` + `pal_ari_cell.yaml` fixtures)

| URML field | Maps to PAL attribute |
|---|---|
| `name` | Specific platform (`pal_tiago`, `pal_talos`, `pal_ari`) |
| `mobility.drive_type` | TIAGo: differential; TALOS: biped; ARI: differential |
| `actuators` | Per-platform (TIAGo arm + torso lift; TALOS full-body; ARI minimal) |
| `cameras` | Per-platform sensor inventory |
| `topology: custom` (`mobile_base_plus_arm_plus_head` for TIAGo; `full_body_humanoid` for TALOS; `social_robot_compact` for ARI) | Composite topology declarations |

### What URML v0.1 does not yet express for PAL

1. **Mobile-manipulator + humanoid + social-robot topology declarations.** TIAGo / TALOS / ARI exercise three distinct topology classes. Spec RFCs queued (mobile-manipulator topology shared with RFC-0184 Hello Robot + RFC-0188 Fetch; humanoid platform refinement shared with RFC-0187 1X; social-robot topology is a new class).
2. **Multi-platform-org engagement scope.** PAL has at least three distinct platforms with one engagement org; URML's manifest cannot today declare which platform within a multi-product OEM is the active deployment.
3. **License clarification.** No SPDX upstream blocks Apache-2.0 downstream bundling.

### Compatibility notes

- **Vendor org.** [`pal-robotics`](https://github.com/pal-robotics) — PAL Robotics, Barcelona Spain.
- **Engagement anchor.** [`pal-robotics/tiago_tutorials`](https://github.com/pal-robotics/tiago_tutorials) — license: none visible (clarification ask), 87 stars, Issues enabled, last commit 2024-02-29 (**stale 818 days**), **not archived**.
- **Other PAL repos (per-platform).** `tiago_robot`, `talos_*`, `ari_*`, `pal_*` patterns. URML's RFC asks for canonical-engagement-surface guidance across this catalog.
- **Origin.** PAL Robotics, Barcelona, Spain (ES). Passes US-federal default policy (NATO+EU).
- **License fit.** Pending clarification.
- **Maintainer signal.** Stale tutorials repo + multi-platform catalog; engagement-channel guidance is the primary ask.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; mobile-manipulator topology + humanoid platform refinement + social-robot topology + multi-platform-org engagement Spec RFCs queued.
- Reference runtime: cross-citation framing pending license + canonical-surface clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Staleness >2 years on the tutorials repo.** Engagement may yield slow / no response; partly a pulse-check.
- **License-clarification gate.**
- **Multi-platform scope** — URML's RFC encompasses TIAGo + TALOS + ARI in one engagement, which may be too broad; the canonical-surface ask is partly an ask-for-redirect.

## Alternatives considered

1. **Engage per-platform with three separate RFCs.** Considered. Without canonical-surface guidance, three RFCs would multiply the engagement cost without proportional information. One RFC asking for guidance + cross-citation framing is the leaner shape.
2. **Engage PAL Robotics off-GitHub via their developer portal.** Possible. URML's outreach is GitHub-first; if maintainers redirect, URML follows.
3. **Skip PAL Robotics as the surface is stale.** Rejected. PAL is one of Europe's most established robotics OEMs; URML's outreach should engage even at light-touch depth.

## Prior art

- [`pal-robotics/tiago_tutorials`](https://github.com/pal-robotics/tiago_tutorials) — the upstream tutorials repo (engagement anchor).
- [RFC-0184 (Hello Robot Stretch)](0184-hello-robot-stretch-outreach.md), [RFC-0188 (Fetch Robotics)](0188-fetchrobotics-fetch-ros-outreach.md) — sibling Move-14 mobile-manipulator RFCs sharing the topology Spec-RFC gap.
- [RFC-0187 (1X Technologies)](0187-1x-technologies-eve-outreach.md) — sibling Move-14 humanoid RFC sharing the humanoid platform refinement gap.

## Unresolved questions

For the pal-robotics maintainers:

1. **Canonical engagement surface.** Which PAL repo (or off-GitHub channel) is the canonical engagement surface in 2026?
2. **License clarification.** Can the active engagement-surface repo get an explicit OSI license declaration?
3. **Multi-platform-org engagement scope.** Should URML engage per-platform (separate RFCs for TIAGo / TALOS / ARI), or per-org with manifest-side platform identifiers?
4. **Mobile-manipulator + humanoid + social-robot topology manifest fields.** Three Spec RFCs queued. Manifest field expectations from the PAL perspective?
5. **Adapter home.** Cross-citation only (recommended pending clarifications), URML repo, or PAL-maintained?
6. **Conformance listing.** Would PAL Robotics consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
7. **Anything else.**

## Implementation note

RFC-0189 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml).

## How to respond

`pal-robotics/tiago_tutorials` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of the staleness + canonical-engagement-surface ask.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license none visible, 87 stars, Issues enabled, last commit 2024-02-29 stale 818d, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (staleness, license gate, multi-platform scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: PAL Robotics ES Barcelona; default policy passes.
- [x] CLAUDE.md compliance check passed.
