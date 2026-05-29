---
rfc: 0215
title: OpenSSF SLSA (supply-chain provenance levels) cross-citation, request for comment from SLSA maintainers
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

# RFC-0215: OpenSSF SLSA supply-chain provenance cross-citation

## Summary

URML's default-policy file (RFC-0003) embeds US-federal alignment (NDAA Section 889, EO 14307, FCC Covered List) for robotics-substrate procurement. EO 14028 (Improving the Nation's Cybersecurity) and its successor frameworks add a supply-chain-provenance layer; SLSA (Supply-chain Levels for Software Artifacts) is the OpenSSF / Linux Foundation framework that operationalizes that layer. This RFC documents the proposed URML v0.1 cross-citation with SLSA, engaged via [`slsa-framework/slsa`](https://github.com/slsa-framework/slsa) (Other / OSI-aligned), and **requests review and feedback from the SLSA maintainers**. No spec change.

## Motivation

URML's default-policy file embeds US-federal alignment that determines which robotics substrates pass the `urml validate --policy` gate. The current set covers NDAA 889 (PRC-domiciled substrate exclusion), EO 14307 (designated entities), and the FCC Covered List. It does not yet cover supply-chain provenance — the question of whether a substrate's build process meets SLSA L1, L2, L3, or L4 evidence requirements. SLSA L3 is the EO 14028-cited supply-chain provenance level for federal-procurement-eligible open-source software.

Repo at [`slsa-framework/slsa`](https://github.com/slsa-framework/slsa) (Other / OSI-aligned, issues enabled, last push `2026-05-18`, 1.8k stars, **not archived**). OpenSSF / Linux Foundation US governance.

URML benefits from documenting the engagement because:

1. **Federal-procurement story strengthens.** URML's default-policy file already cites NDAA 889 / EO 14307 / FCC Covered List; SLSA L3 provenance is the natural fourth pillar for the federal-procurement story.
2. **Substrate-side SLSA-L3 attestation is the right pattern.** URML's manifest could declare a `provenance.slsa_level` field for the substrate; the validator can enforce manifest-vs-attestation at validate time.
3. **OpenSSF / Linux Foundation alignment.** SLSA + Scorecard (sibling RFC-0216) are two OpenSSF-tooling engagements for the same supply-chain-alignment story; engaging both makes URML's federal-procurement narrative coherent.

## Detailed design

### URML v0.1 cross-citation proposal

| URML surface | Maps to / cross-cites SLSA |
|---|---|
| Default-policy file (RFC-0003) | Cross-citation with SLSA L1-L4 provenance levels |
| Future `provenance.slsa_level` manifest field | Substrate's claimed SLSA L1/L2/L3/L4 level (future Spec RFC) |
| Future `provenance.attestation_url` manifest field | Link to substrate's SLSA attestation (future Spec RFC) |
| `urml validate --policy` gate (future) | Validator could enforce manifest-vs-attestation match for SLSA-required deployments |

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Cross-citation in URML default-policy docs** — URML's default-policy file documentation references SLSA L1-L4 as the supply-chain provenance framework URML expects to integrate.
2. **Future Spec RFC for `provenance.slsa_level` field.** Out of scope here; would be a Spec RFC (not Outreach RFC) adding a manifest field. This RFC surfaces the requirement; the field design is a follow-up.
3. **Reciprocal cross-citation (maintainer-discretion)** — SLSA project references URML as one example of an open-spec project consuming SLSA L1-L4 evidence at the substrate boundary.

### Compatibility notes

- **Vendor org.** [`slsa-framework`](https://github.com/slsa-framework) — OpenSSF / Linux Foundation US.
- **Engagement repo.** [`slsa-framework/slsa`](https://github.com/slsa-framework/slsa) — Other / OSI-aligned, issues enabled, last push 2026-05-18, 1.8k stars, **not archived**.
- **Companion repos.** `slsa-framework/slsa-source-poc`, `slsa-framework/slsa-verifier`, `slsa-framework/slsa-github-generator` — the SLSA tooling family.
- **Origin.** OpenSSF / Linux Foundation US. Passes US-federal default policy.
- **License fit.** OSI-aligned; URML can compose at the citation level cleanly.
- **Maintainer signal.** Active commits; v1.1 stable, v1.2 in development.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** Future Spec RFC for `provenance.slsa_level` manifest field is queued.
- Reference runtime: future validator integration with SLSA L3 attestation verification is candidate work.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Substrate SLSA-L3 adoption is uneven.** Major robotics substrates (PX4, ROS 2, MoveIt 2) have varying SLSA-readiness; URML's manifest field would surface a real-world fragmentation.
- **Federal-procurement story coupling.** Tighter SLSA alignment strengthens URML's federal-procurement narrative but does not eliminate the founder-Israel domicile question for actual US federal grant pursuit.
- **OpenSSF + LF engagement load.** SLSA + Scorecard (sibling RFC-0216) are two engagements in the same wave; conversation may converge to OpenSSF / LF Foundation level.

## Alternatives considered

1. **Skip SLSA; rely on default-policy file's existing NDAA / EO 14307 / FCC posture.** Rejected. SLSA L3 is the EO 14028-cited supply-chain provenance level; ignoring it leaves URML's federal-procurement narrative incomplete.
2. **Add `provenance.slsa_level` field directly via Spec RFC without an Outreach RFC.** Rejected. The field design benefits from SLSA-maintainer review before URML commits to the manifest shape.
3. **Bundle SLSA + Scorecard in a single OpenSSF tooling RFC.** Rejected. Different tools, different focus (provenance vs health-scoring); per-tool RFCs let conversation thread per group. Sibling RFC-0216 covers Scorecard.

## Prior art

- [`slsa-framework/slsa`](https://github.com/slsa-framework/slsa) — the upstream SLSA stack (engagement anchor).
- [SLSA L1-L4 specification](https://slsa.dev/spec/v1.0/levels) — the L1/L2/L3/L4 evidence framework.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — URML's US-federal default-policy posture.
- [RFC-0216 (OpenSSF Scorecard outreach)](0216-openssf-scorecard-outreach.md) — sibling Move-17 Sub-wave A engagement at the OpenSSF health-scoring layer.

## Unresolved questions

For the SLSA maintainers:

1. **`provenance.slsa_level` manifest field design.** What's the SLSA maintainers' preferred shape for a downstream consumer declaring "this substrate is SLSA-L3-attested" in a manifest? Single-level enum (`l1`/`l2`/`l3`/`l4`), attestation URL, or both?
2. **Multi-component substrate attestation.** Robotics substrates often compose multiple OSS projects (ROS 2 = rclcpp + rclpy + rmw + multiple plugins); how should URML's manifest declare provenance for a composite substrate?
3. **Validator-side attestation verification.** URML's planned validator integration would fetch and verify the substrate's SLSA attestation at validate time. Are there SLSA-maintainer preferences for which verification path URML should use (`slsa-verifier`, in-toto verifier, custom)?
4. **EO 14028 cross-citation.** URML's default policy already cites NDAA 889 / EO 14307 / FCC Covered List; adding SLSA L3 + EO 14028 — preferred citation language?
5. **Industrial-side robotics SLSA adoption.** What's the SLSA-side view of robotics-substrate adoption today (ROS 2 / PX4 / MoveIt 2)? URML's manifest field would surface real-world gaps.
6. **Conformance listing.** Would SLSA / OpenSSF consider a README cross-link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once URML's manifest field integrates SLSA-level declaration?
7. **Anything else.**

## Implementation note

RFC-0215 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

`slsa-framework/slsa` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the federal-procurement-narrative + manifest-field-design framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Other / OSI-aligned, issues enabled, last push 2026-05-18, 1.8k stars, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (substrate SLSA adoption fragmentation, federal-procurement story coupling, engagement-load).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: OpenSSF / Linux Foundation US; default policy passes.
- [x] CLAUDE.md compliance check passed.
