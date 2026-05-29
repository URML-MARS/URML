---
rfc: 0216
title: OpenSSF Scorecard (open-source security health scoring) cross-citation, request for comment from Scorecard maintainers
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

# RFC-0216: OpenSSF Scorecard health-scoring cross-citation

## Summary

URML's reference runtimes (`reference/ros2-runtime/`, planned `reference/drone-runtime/`, etc.) should publish security health posture using federally-cited tooling. OpenSSF Scorecard is the canonical open-source security health-scoring tool (SBOM / provenance / dependency-update / branch-protection / SAST / CII-Best-Practices signals). This RFC documents the proposed URML v0.1 adoption of Scorecard for URML reference runtimes, engaged via [`ossf/scorecard`](https://github.com/ossf/scorecard) (Apache-2.0), and **requests review and feedback from the Scorecard maintainers**. No spec change.

Sibling to RFC-0215 (SLSA). Together they form URML's OpenSSF tooling adoption layer; SLSA covers supply-chain provenance, Scorecard covers ongoing security health.

## Motivation

URML's reference runtimes ship from the URML repo (and future companion-package repos). Each repo's security posture (branch protection, dependency-update cadence, signed releases, SBOM availability, SAST coverage) is currently undocumented; downstream consumers cannot easily assess URML reference-runtime security health.

Scorecard publishes a 0-10 score per repo across ~18 security signals. The score is consumed by federal-procurement teams via the OpenSSF Best Practices Badge program and other federally-cited tooling. URML reference-runtime adoption of Scorecard would publish URML's security posture in a federally-recognized format.

Repo at [`ossf/scorecard`](https://github.com/ossf/scorecard) (Apache-2.0, issues enabled, last push `2026-05-25`, 5.5k stars, **not archived**). OpenSSF / Linux Foundation US governance.

URML benefits from documenting the engagement because:

1. **Federal-procurement narrative.** Sibling RFC-0215 establishes URML's SLSA provenance posture; this RFC establishes URML's Scorecard health-scoring posture. Together they cover the federal-procurement security narrative.
2. **Reference-runtime quality discipline.** Adopting Scorecard publishes URML's security posture and surfaces gaps URML can address concretely (branch protection, signed releases, dependency-update cadence).
3. **Substrate-side Scorecard cross-reference.** URML's manifest could declare `provenance.scorecard_min_score` as a substrate quality gate; the validator can enforce manifest-vs-substrate at validate time.

## Detailed design

### URML v0.1 cross-citation proposal

| URML surface | Maps to / cross-cites Scorecard |
|---|---|
| URML repo + reference-runtime repos | Adopt Scorecard GitHub Action; publish score badge in README |
| Future `provenance.scorecard_min_score` manifest field | Substrate's minimum-acceptable Scorecard score (future Spec RFC) |
| Default-policy file (RFC-0003) cross-reference | Documentation reference to Scorecard alongside SLSA + NDAA + EO 14307 + FCC Covered List |
| `urml validate --policy` gate (future) | Validator could enforce manifest-vs-substrate Scorecard threshold for security-sensitive deployments |

### What URML proposes (not a spec change, but does propose a concrete adoption step)

This RFC does not propose a URML spec change. It proposes:

1. **URML repo adopts Scorecard.** The URML main repo enables the Scorecard GitHub Action and publishes the score badge in README. Reference-runtime companion repos follow when they ship.
2. **Cross-citation in URML default-policy docs** — URML's default-policy file documentation references Scorecard alongside SLSA L1-L4.
3. **Future Spec RFC for `provenance.scorecard_min_score` manifest field.** Out of scope here; surfaces the requirement for a follow-up Spec RFC.

### Compatibility notes

- **Vendor org.** [`ossf`](https://github.com/ossf) — OpenSSF / Linux Foundation US.
- **Engagement repo.** [`ossf/scorecard`](https://github.com/ossf/scorecard) — Apache-2.0, issues enabled, last push 2026-05-25, 5.5k stars, **not archived**.
- **Companion repos.** `ossf/scorecard-action`, `ossf/scorecard-webapp` — the Scorecard tooling family.
- **Origin.** OpenSSF / Linux Foundation US. Passes US-federal default policy.
- **License fit.** Apache-2.0. Clean fit.
- **Maintainer signal.** Active commits; canonical OSS-security-health tool.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** Future Spec RFC for `provenance.scorecard_min_score` manifest field is queued.
- Reference runtime: URML repo and reference-runtime repos to adopt the Scorecard GitHub Action (concrete adoption step; implementation issue, not spec change).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only on the spec side; adoption step on the implementation side.** The Scorecard GitHub Action adoption is concrete (add a workflow); the implementation side is real if minor.
- **Score-management overhead.** Publishing a Scorecard badge means the score becomes a visible metric; URML must commit to addressing gaps the score surfaces (branch protection, signed releases, dependency-update cadence).
- **Substrate Scorecard adoption is uneven.** Major robotics substrates may not have Scorecard adoption; URML's manifest field would surface real-world gaps.
- **OpenSSF engagement load.** SLSA (sibling RFC-0215) + Scorecard are two OpenSSF engagements; conversation may converge to OpenSSF Foundation level.

## Alternatives considered

1. **Skip Scorecard; rely on URML's existing security disclosure docs.** Rejected. URML's security disclosure is repo-internal; Scorecard is federally-cited external scoring that downstream consumers can verify automatically.
2. **Adopt Scorecard but don't publish the badge.** Rejected. The badge in README is what makes the score visible to downstream consumers; adopting without publishing defeats the federal-procurement-narrative goal.
3. **Bundle Scorecard + SLSA in a single OpenSSF tooling RFC.** Rejected. Different tools, different focus (health-scoring vs supply-chain provenance); per-tool RFCs let conversation thread per group. Sibling RFC-0215 covers SLSA.

## Prior art

- [`ossf/scorecard`](https://github.com/ossf/scorecard) — the upstream Scorecard stack (engagement anchor).
- [Scorecard checks documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md) — the ~18-signal evaluation framework.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — URML's US-federal default-policy posture.
- [RFC-0215 (OpenSSF SLSA outreach)](0215-openssf-slsa-outreach.md) — sibling Move-17 Sub-wave A engagement at the OpenSSF supply-chain layer.

## Unresolved questions

For the OpenSSF Scorecard maintainers:

1. **Robotics-specific signal extensions.** Are there robotics-substrate-specific security signals (manifest declaration, validator coverage, capability-attestation) that would benefit Scorecard, or are the existing ~18 signals sufficient for URML's reference-runtime repos?
2. **`provenance.scorecard_min_score` manifest field design.** What's the Scorecard maintainers' preferred shape for a downstream consumer declaring "this substrate must score >= N" in a manifest? Single-threshold-number, per-signal-threshold, or other?
3. **Multi-component substrate scoring.** Robotics substrates often compose multiple OSS projects (ROS 2 = rclcpp + rclpy + rmw + plugins); how should URML's manifest declare an aggregate Scorecard threshold for a composite substrate?
4. **Adoption recommendation for URML reference-runtime repos.** Are there Scorecard-recommended adoption patterns for multi-runtime-repo projects (single Scorecard run vs per-runtime-repo)?
5. **Reciprocal cross-citation.** Would Scorecard reference URML as one example of an open-spec project consuming Scorecard at the substrate boundary?
6. **OpenSSF / LF engagement convergence.** With SLSA (RFC-0215) + Scorecard (RFC-0216) active concurrently, should URML pursue an OpenSSF / LF Foundation-level conversation rather than per-project Issue threads?
7. **Conformance listing.** Would Scorecard / OpenSSF consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0216 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). URML repo adoption of the Scorecard GitHub Action is a separate implementation issue (not part of this RFC).

## How to respond

`ossf/scorecard` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the URML-repo-adoption + manifest-field-design framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0, issues enabled, last push 2026-05-25, 5.5k stars, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (score-management overhead, substrate adoption gaps, engagement-load).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: OpenSSF / Linux Foundation US; default policy passes.
- [x] CLAUDE.md compliance check passed.
