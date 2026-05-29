---
rfc: 0213
title: ELISA wg-automotive (Linux Foundation safety-Linux project) cross-citation, request for comment from ELISA maintainers
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

# RFC-0213: ELISA wg-automotive cross-citation

## Summary

URML's `safety_envelope` manifest field and validator-gated execution model align with ELISA's safe-construction-from-Linux thesis. This RFC documents the proposed URML v0.1 cross-citation with the ELISA Project, engaged via [`elisa-tech/wg-automotive`](https://github.com/elisa-tech/wg-automotive) (multi-OSI licenses), and **requests review and feedback from the ELISA maintainers**. No spec change.

ELISA (Enabling Linux In Safety Applications) is a Linux Foundation project chartered to make it easier for companies to build and certify Linux-based safety-critical applications. Founding members include KUKA, Toyota, BMW, and Arm — URML-adjacent industrial and automotive robotics primes.

## Motivation

URML's reference runtimes (`reference/ros2-runtime/`, planned `reference/drone-runtime/`, etc.) execute on Linux substrates that face the same safety-construction problem ELISA was chartered to solve: how does an open-source Linux-based stack reach safety-certification readiness without giving up the open-source posture? URML's manifest-validated dispatch + validator static-verification stage is one concrete pattern for declaring the safe-construction boundary explicitly; ELISA's body of work is the broader framework that pattern composes within.

Repo at [`elisa-tech/wg-automotive`](https://github.com/elisa-tech/wg-automotive) (multi-OSI, issues enabled, last push `2026-05-27`, **not archived**). Linux Foundation US governance. wg-aerospace + Safety_Architecture_WG also active in the org (26 repos total, all pushed within 6 weeks).

URML benefits from documenting the engagement because:

1. **Safe-by-construction narrative cross-citation.** ELISA's safety-Linux body of work is the broader framework URML's manifest-validated dispatch composes within. Cross-citation strengthens URML's safe-construction story without URML having to reinvent ELISA's analysis.
2. **Founding-member adjacency.** ELISA founding members (KUKA / Toyota / BMW / Arm) are URML-adjacent — KUKA is an industrial-arm OEM, Toyota and BMW are automotive primes whose robotics arms intersect URML's drone and industrial-arm runtime tracks.
3. **wg-aerospace + wg-automotive cross-coverage.** ELISA's working-group expansion to aerospace + automotive aligns with URML's drone and industrial-arm runtime tracks.

## Detailed design

### URML v0.1 cross-citation proposal

| URML surface | Maps to / cross-cites ELISA |
|---|---|
| `safety_envelope` manifest field | Cross-citation with ELISA Safety_Architecture_WG patterns |
| `validator` static-verification stage | Parallel to ELISA's certification-readiness verification framing |
| `reference/ros2-runtime/` | Cross-citation with ELISA wg-automotive Linux-base patterns |
| Planned `reference/drone-runtime/` | Cross-citation with ELISA wg-aerospace patterns |
| URML's "execute only after static verification" boundary (per CLAUDE.md) | Parallel to ELISA's safe-construction boundary |

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Cross-citation in URML safety-related docs** — URML's manifest-validator documentation references ELISA's safe-Linux body of work as a related-art framework.
2. **Reciprocal cross-citation (maintainer-discretion)** — ELISA wg-automotive / wg-aerospace patterns reference URML as a substrate-neutral robotics-intent-language sibling for declarative-intent + validator-gated-execution patterns.
3. **Working-group cross-attendance.** URML maintainer monitors ELISA wg-automotive / Safety_Architecture_WG calls (open per project charter) for safety-Linux work relevant to URML's reference runtimes.

### Compatibility notes

- **Vendor org.** [`elisa-tech`](https://github.com/elisa-tech) — Linux Foundation ELISA Project.
- **Engagement repo.** [`elisa-tech/wg-automotive`](https://github.com/elisa-tech/wg-automotive) — multi-OSI, issues enabled, last push 2026-05-27 (active), **not archived**.
- **Companion repos.** `elisa-tech/wg-aerospace`, `elisa-tech/Safety_Architecture_WG`, 23 more — the ELISA ecosystem.
- **Origin.** Linux Foundation US. Founding members KUKA / Toyota / BMW / Arm; member organizations include Horizon Robotics, NVIDIA, Red Hat, Codethink, Huawei.
- **License fit.** Multiple OSI licenses; safety-frame compatible with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily-to-weekly commit cadence; the canonical safety-Linux open-source project.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** This RFC proposes cross-citation only.
- Reference runtime: future safety-docs may reference ELISA's body of work. No code change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Safety-certification gap.** URML is not safety-certified and does not claim to be; cross-citation must not be read as a certification claim.
- **Member-organization scale.** ELISA's body of work is shaped by member-organization needs (KUKA / Toyota / BMW / Arm); URML's substrate-neutral stance must remain distinct from any single member-track.
- **Founding-member adjacency does not equal alignment.** KUKA / Toyota / BMW being ELISA founding members does not automatically extend URML adjacency to them; URML's relationship with those primes (if any) is independent.

## Alternatives considered

1. **Skip ELISA; rely on URML's own safety-envelope documentation.** Rejected. ELISA's broader safe-Linux framework strengthens URML's safe-construction narrative; cross-citation is cheaper than reinvention.
2. **Engage at Linux Foundation meta level rather than per-WG.** Considered. Per-WG engagement is the lowest-friction first-contact; LF-meta conversation stays open as escalation.
3. **Bundle wg-automotive with wg-aerospace in a single ELISA cross-citation RFC.** Rejected. The two WGs have different blueprint patterns aligned with URML's industrial-arm and drone runtime tracks respectively; per-WG framing is cleaner.

## Prior art

- [`elisa-tech/wg-automotive`](https://github.com/elisa-tech/wg-automotive) — the upstream ELISA wg-automotive stack (engagement anchor).
- [`elisa-tech/wg-aerospace`](https://github.com/elisa-tech/wg-aerospace) — aerospace working-group sibling.
- [`elisa-tech/Safety_Architecture_WG`](https://github.com/elisa-tech/Safety_Architecture_WG) — the cross-WG safety architecture work.
- [RFC-0008 (drone profile)](0008-drone-profile.md), [RFC-0013 (industrial profile)](0013-industrial-profile.md) — URML profiles that compose against ELISA-aligned safe-Linux substrates.
- [RFC-0212 (Eclipse SDV outreach)](0212-eclipse-sdv-blueprints-outreach.md) — sibling Move-17 Sub-wave A engagement at the SDV layer.

## Unresolved questions

For the ELISA maintainers:

1. **Cross-citation framing preference.** Should URML's safety-docs cite ELISA by Project name, by specific WG (wg-automotive / wg-aerospace / Safety_Architecture_WG), or both?
2. **Working-group cross-attendance.** Are ELISA WG calls open to non-member attendees? URML maintainer would benefit from monitoring safety-Linux work relevant to URML's reference runtimes.
3. **Aerospace + automotive scope mapping.** URML's drone profile (RFC-0008) and industrial profile (RFC-0013) compose against substrates relevant to wg-aerospace and wg-automotive respectively; is the per-WG cross-citation mapping appropriate?
4. **Safety-claim discipline.** URML does not claim safety certification; cross-citation is for safe-construction-framework alignment. Are there ELISA guidelines for how non-certified open-source projects should cross-cite without misrepresenting certification status?
5. **Linux Foundation member-track question.** URML is single-maintainer Phase-1; what's the LF/ELISA path for a future-foundation candidate? (Orientation question only; not a Phase-1 ask.)
6. **Conformance listing.** Would ELISA consider a wg-automotive / wg-aerospace README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once cross-citation stabilizes?
7. **Anything else.**

## Implementation note

RFC-0213 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

`elisa-tech/wg-automotive` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the safe-construction cross-citation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (multi-OSI, issues enabled, last push 2026-05-27, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (safety-certification gap, member-organization scale, founding-member-adjacency-vs-alignment).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation US; founding members KUKA / Toyota / BMW / Arm; default policy passes.
- [x] CLAUDE.md compliance check passed.
