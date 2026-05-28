---
rfc: 0190
title: Toyota Research Institute HSR (Human Support Robot) integration, request for comment from ToyotaResearchInstitute maintainers — canonical-engagement-surface ask
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

# RFC-0190: Toyota Research Institute HSR integration — canonical-engagement-surface ask (completes Move-14)

## Summary

URML does not yet ship an HSR manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest **cross-citation** for the Toyota HSR (Human Support Robot) over [`ToyotaResearchInstitute/hsr_description`](https://github.com/ToyotaResearchInstitute/hsr_description) (BSD-3-Clause-Clear), and **requests review and feedback from the ToyotaResearchInstitute maintainers**. **Canonical-engagement-surface ask** is the gating item — TRI is the research-direct surface, but Toyota Japan owns the HSR platform itself. No spec change.

**Completes the 7 Move-14 engageable RFCs.**

## Motivation

The Toyota HSR (Human Support Robot) is a research-grade mobile manipulator widely used in robotics-competition contexts (RoboCup@Home, World Robot Summit) and assistive-robotics research. URML's mobile-manipulator class declaration applies cleanly to HSR's mobile-base + arm + display-head composition.

Repo at [`ToyotaResearchInstitute/hsr_description`](https://github.com/ToyotaResearchInstitute/hsr_description) (BSD-3-Clause-Clear, 37 stars, Issues enabled, last commit `2024-05-05` — **stale 753 days from cutoff 2026-05-28**, **not archived**). This is a URDF/mesh-asset repo only — not the primary robot stack.

URML's engagement angle is the canonical-engagement-surface ask. TRI is Toyota's US research-direct surface (Cambridge MA / Los Altos CA); Toyota Japan owns HSR's primary engineering. The public URDF repo is the asset-only surface. URML's RFC asks where the active engagement happens in 2026 — TRI-side, Toyota-Japan-side, or via a competition / research consortium.

## Detailed design

### URML v0.1 capability-manifest mapping (cross-citation framing, planned `toyota_hsr_cell.yaml` fixture)

| URML field | Maps to HSR attribute |
|---|---|
| `name` | `toyota_hsr` (HSRB Mark 1, HSRB Mark 2 variants) |
| `mobility.drive_type: omnidirectional` | HSR omnidirectional mobile base (clean v0.1 fit) |
| `actuators` | 5-DoF arm + display-head pan-tilt |
| `cameras` | Wide-angle head camera + grip-camera (HSR's distinguishing feature) |
| `topology: custom` (`mobile_base_plus_arm_plus_display_head`) | Same composite topology class as RFC-0184 / RFC-0188 |
| `research_consortium_class: custom` (`toyota_hsr_research`) | Manifest field for research-program-only platforms |

### What URML v0.1 does not yet express for HSR

1. **Mobile-manipulator topology declaration.** Same shared gap as RFC-0184 Hello Robot Stretch + RFC-0188 Fetch Robotics.
2. **Research-consortium-class platform declaration.** HSR is distributed via Toyota's HSR research-program to selected academic labs; URML's manifest cannot today declare research-program-only distribution.
3. **Grip-camera declaration.** HSR's distinguishing perception feature is a camera mounted on the gripper itself; URML's `cameras` block doesn't today declare end-effector-mounted cameras.

### Compatibility notes

- **Vendor / research org.** [`ToyotaResearchInstitute`](https://github.com/ToyotaResearchInstitute) — Toyota Research Institute, US (Cambridge MA / Los Altos CA).
- **Anchor repo.** [`ToyotaResearchInstitute/hsr_description`](https://github.com/ToyotaResearchInstitute/hsr_description) — BSD-3-Clause-Clear, 37 stars, Issues enabled, last commit 2024-05-05 (**stale 753 days**), **not archived**.
- **Origin.** TRI (US) / Toyota Japan (parent). Passes US-federal default policy.
- **License fit.** BSD-3-Clause-Clear cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Stale URDF/mesh-asset repo; engagement is partly a canonical-surface ask.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; mobile-manipulator topology (shared with RFC-0184 / RFC-0188) + research-consortium-class + end-effector-mounted-camera Spec RFCs queued.
- Reference runtime: cross-citation framing recommended given the URDF/mesh-asset-only scope of the public repo.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Staleness >2 years on the public repo.** Engagement may yield slow / no response.
- **URDF/mesh-asset-only public scope.** The primary HSR robot stack is closed; URML's adapter pattern composes at the URDF + standard-message-types boundary.
- **TRI vs Toyota-Japan split.** Engagement-channel guidance is the primary ask.
- **Research-consortium distribution.** HSR isn't commodity-purchasable; URML deployments depend on Toyota's research-program access.

## Alternatives considered

1. **Engage Toyota Japan directly.** Considered. TRI is the GitHub-visible surface; Toyota Japan engagement is off-GitHub. URML's RFC asks for redirect if needed.
2. **Skip HSR as research-program-only.** Rejected. Active RoboCup@Home + World Robot Summit deployments + URDF-asset-only public surface make a cross-citation engagement worth the light-touch cost.
3. **Bundle HSR with sibling Move-14 mobile-manipulator RFCs.** Rejected. Per-vendor RFCs.

## Prior art

- [`ToyotaResearchInstitute/hsr_description`](https://github.com/ToyotaResearchInstitute/hsr_description) — the upstream URDF/mesh-asset repo.
- [RFC-0184 (Hello Robot Stretch)](0184-hello-robot-stretch-outreach.md), [RFC-0188 (Fetch Robotics)](0188-fetchrobotics-fetch-ros-outreach.md) — sibling Move-14 mobile-manipulator RFCs sharing the topology Spec-RFC gap.
- [RFC-0054 (TRI-LBM)](0054-tri-lbm-outreach.md) — Move-2 prior RFC engaging TRI broader (Large Behavior Models program); this RFC is HSR-specific.

## Unresolved questions

For the ToyotaResearchInstitute (and Toyota Japan, if reachable) maintainers:

1. **Canonical engagement surface.** Is TRI the canonical engagement surface for HSR research, or does Toyota Japan own the primary engineering?
2. **Repository status.** Stale 753 days — actively maintained on slower cadence, dormant-but-supported, or has the engagement moved to a research-consortium channel (RoboCup@Home, etc.)?
3. **Mobile-manipulator topology manifest fields.** Same shared question as RFC-0184 / RFC-0188.
4. **Research-consortium-class platform declaration.** Should URML's manifest declare research-program-only distribution for downstream operator awareness?
5. **Grip-camera declaration.** Manifest field for end-effector-mounted cameras?
6. **Adapter home.** Cross-citation only (recommended given URDF-only scope), URML repo, or TRI-maintained?
7. **Conformance listing.** Would TRI consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
8. **Anything else.**

## Implementation note

RFC-0190 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml). **Completes the 7 Move-14 engageable RFCs.**

## How to respond

`ToyotaResearchInstitute/hsr_description` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of the URDF-asset-only scope + TRI-vs-Toyota-Japan canonical-surface ask.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause-Clear, 37 stars, Issues enabled, last commit 2024-05-05 stale 753d, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (staleness, URDF-only scope, TRI vs Toyota-Japan split, research-program distribution).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: TRI US / Toyota Japan parent; default policy passes.
- [x] CLAUDE.md compliance check passed.
