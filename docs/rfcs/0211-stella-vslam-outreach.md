---
rfc: 0211
title: Stella VSLAM (community fork of OpenVSLAM) cross-citation, request for comment from stella-cv maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0211: Stella VSLAM (community fork of OpenVSLAM) cross-citation

## Summary

URML's visual-SLAM enum (sibling [RFC-0206 ORB-SLAM3](0206-orb-slam3-outreach.md)) covers the canonical academic reference, but the originally-archived OpenVSLAM lives on as the maintained community fork Stella VSLAM. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Stella VSLAM substrate, engaged at the stella-cv community layer via [`stella-cv/stella_vslam`](https://github.com/stella-cv/stella_vslam) (Other — license clarification needed), and **requests review and feedback from the stella-cv maintainers**. No spec change.

**License clarification is the gating fact.** The repo is GitHub-classified as Other; OpenVSLAM history was BSD-2-Clause-derivative with a license dispute that prompted the archive. Stella VSLAM's continuation license posture needs clarity for URML adapter posture.

## Motivation

OpenVSLAM was a popular ORB-SLAM2-derivative visual-SLAM library; it was archived upstream in 2019 due to a license dispute (DBoW2 vocabulary derivation). Stella VSLAM is the community fork that resumed development. Production users with deployed OpenVSLAM infrastructure migrated to Stella VSLAM. URML's visual-SLAM enum needs to include Stella VSLAM as an alternative to ORB-SLAM3 for these production users.

Repo at [`stella-cv/stella_vslam`](https://github.com/stella-cv/stella_vslam) (Other — license clarification needed, 1.2k stars, Issues enabled, last commit `2026-05-27`, **not archived**). Community fork (originally JP origin from National Institute of Advanced Industrial Science and Technology / AIST).

URML benefits from documenting the engagement because:

1. **Community-fork continuity in visual-SLAM enum.** Production users with OpenVSLAM deployments need a non-archived migration target; URML's manifest enum should reflect the lived reality.
2. **License clarification ask.** The OpenVSLAM archive event was license-driven; Stella VSLAM's continuation license posture needs to be explicit for URML adapter posture.
3. **AIST academic origin (Japan).** US-federal default policy passes for Japan (NATO-allied via Indo-Pacific framework, key US ally per FY26 NDAA); engagement is policy-clean.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `stella_vslam_cell.yaml` fixture, pending license clarification)

| URML field | Maps to Stella VSLAM attribute |
|---|---|
| `name` | Deployment handle (`stella_vslam_stereo`) |
| `perception.slam_substrate: stella_vslam` | URML's visual-SLAM enum value (community-fork tier) |
| `perception.slam_substrate.lineage: openvslam` | URML's first lineage-declaration field (community-fork lineage) |
| `perception.slam_mode: monocular` / `stereo` / `rgbd` | Stella VSLAM sensor topology mode |
| `perception.vocabulary_path` | ORB vocabulary file reference |
| `perception.camera_config_yaml` | Camera-calibration YAML reference |
| `pose_frame.map_frame` | Stella VSLAM map frame |

### What URML v0.1 does not yet express for Stella VSLAM

1. **Lineage-declaration field.** Community-fork lineage (Stella VSLAM ← OpenVSLAM archived) is novel; URML's manifest could declare `lineage` for archived-upstream history.
2. **Three-mode enumeration** (monocular / stereo / RGB-D) — overlap with ORB-SLAM3 enum (sibling RFC-0206); URML's manifest could share the enum or per-substrate-specialize.
3. **Vocabulary file declaration** — same field family as ORB-SLAM3 sibling RFC-0206.
4. **License-clarification manifest hint.** Until upstream license clarifies, URML's manifest could mark the substrate as `license_status: clarification_pending`.

### Compatibility notes

- **Vendor org.** [`stella-cv`](https://github.com/stella-cv) — community fork; originally AIST / Japan origin.
- **Engagement repo.** [`stella-cv/stella_vslam`](https://github.com/stella-cv/stella_vslam) — Other (license-clarification needed), 1.2k stars, Issues enabled, last commit 2026-05-27, **not archived**.
- **Companion repos.** `stella-cv/stella_vslam_ros2` (ROS 2 binding) — the maintained binding.
- **Upstream archive.** OpenVSLAM (AIST, archived 2019); Stella VSLAM is the community continuation.
- **Origin.** Japan (key US ally per FY26 NDAA, Indo-Pacific framework); academic-lineage community fork. Passes US-federal default policy.
- **License fit.** Pending clarification; URML adapter posture is cross-citation-only by default until upstream declares.
- **Maintainer signal.** Active commits; the maintained OpenVSLAM continuation.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; lineage-declaration + license-status-hint + visual-SLAM enum sharing Spec RFCs queued.
- Reference runtime: no in-repo adapter pending license clarification; URML cites Stella VSLAM at the API boundary.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate** — adapter-grade reuse is blocked until upstream license clarifies.
- **Community-fork-lineage novelty** — URML's first `lineage` declaration; archived-upstream provenance is new manifest territory.
- **OpenVSLAM-license-dispute history** — Stella VSLAM inherited a license-dispute history; URML's engagement must navigate it carefully.

## Alternatives considered

1. **Skip Stella VSLAM; declare only ORB-SLAM3.** Rejected. Production OpenVSLAM users migrated to Stella VSLAM; URML's manifest enum should reflect lived reality.
2. **Wait for license clarification before engaging.** Rejected. RFC engagement is itself the license-clarification ask; engagement-driven clarity is the established pattern (see RFC-0135 Cerulean Sonar precedent).
3. **Bundle Stella VSLAM with ORB-SLAM3 in a single visual-SLAM RFC.** Rejected. Different governance (community fork vs academic lab), different licenses (pending clarification vs GPL-3.0); per-vendor RFCs let conversation thread per group.

## Prior art

- [`stella-cv/stella_vslam`](https://github.com/stella-cv/stella_vslam) — the upstream Stella VSLAM stack (engagement anchor).
- [`stella-cv/stella_vslam_ros2`](https://github.com/stella-cv/stella_vslam_ros2) — the ROS 2 binding.
- OpenVSLAM (AIST, archived 2019) — the archived upstream; Stella VSLAM is the community continuation.
- [RFC-0205 (Cartographer outreach)](0205-cartographer-outreach.md), [RFC-0206 (ORB-SLAM3 outreach)](0206-orb-slam3-outreach.md), [RFC-0207 (RTAB-Map outreach)](0207-rtabmap-outreach.md) — sibling Move-16 batch-3 RFCs; alternative SLAM substrates.

## Unresolved questions

For the Stella VSLAM / stella-cv maintainers:

1. **License clarification.** Can the repo declare an explicit OSI license (BSD-3-Clause / Apache-2.0 / similar), or is the cross-citation-only posture the right default?
2. **Lineage-declaration field.** URML's first `lineage` manifest field — preferred shape for declaring the OpenVSLAM-derived continuation?
3. **SLAM-substrate enum value.** URML's manifest enum value preference (`stella_vslam`, `stella-vslam`, `stellavslam`)?
4. **Three-mode enumeration sharing.** Should URML's `slam_mode` enum be shared across Stella VSLAM and ORB-SLAM3 (single visual-SLAM enum), or per-substrate-specialized?
5. **Vocabulary file declaration.** ORB vocabulary reference — manifest-field convention preference?
6. **AIST / academic-lineage attribution.** Does the Stella VSLAM team want URML to declare AIST academic-lineage attribution in the manifest itself?
7. **Conformance listing.** Would stella-cv consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once license clarifies?
8. **Anything else.**

## Implementation note

RFC-0211 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`stella-cv/stella_vslam` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification + community-fork-lineage framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Other — license clarification needed, 1.2k stars, Issues enabled, last commit 2026-05-27, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-clarification gate, community-fork-lineage novelty, OpenVSLAM-license-dispute history).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Japan (key US ally per FY26 NDAA); academic-lineage community fork; default policy passes.
- [x] CLAUDE.md compliance check passed.
