---
rfc: 0212
title: Eclipse SDV Blueprints (Eclipse Foundation Software-Defined Vehicle WG) cross-citation, request for comment from SDV maintainers
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

# RFC-0212: Eclipse SDV Blueprints cross-citation

## Summary

URML's drone-runtime and industrial-arm-runtime tracks reference safe-vehicle-software composition patterns that the Eclipse Foundation Software-Defined Vehicle (SDV) Working Group has been formalizing across automotive, commercial-vehicle, and (newly in 2026) aerospace blueprints. This RFC documents the proposed URML v0.1 cross-citation between URML's substrate-neutral runtime composition and Eclipse SDV's blueprint patterns, engaged via [`eclipse-sdv-blueprints/blueprints-website`](https://github.com/eclipse-sdv-blueprints/blueprints-website) (EPL-2.0), and **requests review and feedback from the Eclipse SDV maintainers**. No spec change.

**This is the opening RFC of Move-17 Sub-wave A** — Move-17 engages governance bodies rather than substrate / vendor maintainers, and Sub-wave A is the GitHub-Issue-postable slice. Sub-wave B (founder-action: OSRA, JDF, IEEE, NIST EL, ASTM F45, IIA, euRobotics, ADRA, JTC 21, DIN/DKE, AFNOR, BSI, OECD) requires non-GitHub channels.

## Motivation

The Eclipse SDV Working Group has published blueprint patterns covering vehicle-software platforms — Eclipse Kuksa (vehicle abstraction), Eclipse Velocitas (cloud-native development), Eclipse Chariott (service mesh), Eclipse Sommr (data orchestration). The 2026 expansion brings commercial-vehicle, next-gen-mobility, and aerospace blueprint extensions. URML's drone and industrial-arm runtime tracks face structurally similar problems: substrate-neutrality, safe composition, declarative intent, and validator-gated execution.

Repo at [`eclipse-sdv-blueprints/blueprints-website`](https://github.com/eclipse-sdv-blueprints/blueprints-website) (EPL-2.0, issues enabled, last push `2026-05-05`, **not archived**). Eclipse Foundation Brussels AISBL governance. 2026 hackfests in Esslingen + Friedrichshafen; new member wave 2026 across automotive / commercial-vehicle / next-gen-mobility / aerospace.

URML benefits from documenting the engagement because:

1. **Cross-citation strengthens URML's safe-by-construction narrative.** Eclipse SDV blueprint patterns are widely-reviewed safe-composition references; URML's substrate-neutral framing benefits from explicit cross-citation rather than parallel-but-disconnected reinvention.
2. **Eclipse Foundation alignment.** Eclipse SDV is the fourth Eclipse Foundation engagement (Cyclone DDS RFC-0204, Zenoh RFC-0209, iceoryx RFC-0210 in Move-16; SDV here). Engagement at SDV across-WG opens a potential Eclipse Foundation-level conversation.
3. **EPL-2.0 → adapter-boundary cross-citation.** URML's Apache-2.0 reference runtimes cannot embed EPL-2.0 source, but can compose at the API boundary cleanly. The pattern is established by URML's Move-16 Cyclone DDS engagement.

## Detailed design

### URML v0.1 cross-citation proposal

| URML surface | Maps to / cross-cites Eclipse SDV |
|---|---|
| `reference/drone-runtime/` | Cross-citation with SDV vehicle-abstraction patterns (Kuksa-like manifest declaration) |
| `reference/industrial-arm-runtime/` | Cross-citation with SDV service-mesh patterns (Chariott-like dispatcher composition) |
| `safety_envelope` manifest field | Cross-citation with SDV safety-blueprint patterns (vehicle-side envelope-binding) |
| `validator` static-verification stage | Parallel to SDV's declarative-blueprint validation step |
| Cross-WG aerospace blueprint extension | URML drone profile (RFC-0008) provides a substrate-neutral robotics-intent layer for safe-aerospace-software composition |

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Cross-citation in URML reference-runtime READMEs** — URML's drone and industrial-arm reference-runtime READMEs link to Eclipse SDV blueprint patterns as related-art references.
2. **Reciprocal cross-citation in Eclipse SDV blueprints** (optional, maintainer-discretion) — Eclipse SDV blueprint patterns reference URML as a substrate-neutral robotics-intent-language sibling for aerospace / commercial-vehicle / industrial-mobility blueprint extensions.
3. **Eclipse Foundation-level conversation** — URML's three Move-16 engagements (Cyclone DDS, Zenoh, iceoryx) + this Sub-wave A engagement may converge to a Foundation-level discussion; this RFC flags that channel as open.

### Compatibility notes

- **Vendor org.** [`eclipse-sdv-blueprints`](https://github.com/eclipse-sdv-blueprints) — Eclipse Foundation Brussels AISBL.
- **Engagement repo.** [`eclipse-sdv-blueprints/blueprints-website`](https://github.com/eclipse-sdv-blueprints/blueprints-website) — EPL-2.0, issues enabled, last push 2026-05-05, **not archived**. 12 sister repos in the org also active.
- **Companion projects.** Eclipse Kuksa (vehicle abstraction), Eclipse Velocitas (cloud-native dev), Eclipse Chariott (service mesh), Eclipse Sommr (data orchestration) — the SDV ecosystem.
- **Origin.** Eclipse Foundation Brussels AISBL. NATO-allied; passes US-federal default policy.
- **License fit.** EPL-2.0 → API-boundary cross-citation (URML's Apache-2.0 adapter source does not embed EPL-2.0 source but composes cleanly at the API boundary).
- **Maintainer signal.** Active commits; 2026 hackfests scheduled; new member wave across automotive / commercial-vehicle / next-gen-mobility / aerospace.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** This RFC proposes cross-citation only.
- Reference runtime: future README updates may add a "Related art" section pointing at Eclipse SDV blueprint patterns. No code change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Cross-WG fit risk** — Eclipse SDV is automotive-coded; URML's robotics scope is broader. The cross-citation may be at the conceptual level (safe-composition patterns) rather than substrate-level.
- **Aerospace-blueprint extension is in early formation in 2026** — URML's cross-citation timing is opportunistic but may be too early.
- **Eclipse Foundation engagement load** — fourth Eclipse engagement in two moves. Per-project Issue threads work; a Foundation-level conversation is more efficient if maintainers prefer.

## Alternatives considered

1. **Skip Eclipse SDV; engage only at the Eclipse Foundation meta level.** Rejected. The blueprints repo is the engaged surface where active maintainers are. A meta-Eclipse conversation can stay open as escalation.
2. **Bundle SDV with Cyclone DDS / Zenoh / iceoryx in a single Eclipse Foundation cross-citation RFC.** Rejected. SDV is a different Working Group with different blueprint patterns; per-WG engagement is the right shape.
3. **Defer Eclipse SDV cross-citation until URML has shipped aerospace-specific blueprint material.** Rejected. The cross-citation is a positioning move, not an artifact-shipping move. Engaging now while SDV's aerospace extension is in early formation preserves an alignment window.

## Prior art

- [`eclipse-sdv-blueprints/blueprints-website`](https://github.com/eclipse-sdv-blueprints/blueprints-website) — the upstream Eclipse SDV blueprints (engagement anchor).
- Eclipse Kuksa, Eclipse Velocitas, Eclipse Chariott, Eclipse Sommr — the SDV blueprint family.
- [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md), [RFC-0209 (Zenoh outreach)](0209-zenoh-outreach.md), [RFC-0210 (iceoryx outreach)](0210-iceoryx-outreach.md) — prior Move-16 Eclipse Foundation engagements.
- [RFC-0008 (drone profile)](0008-drone-profile.md), [RFC-0013 (industrial profile)](0013-industrial-profile.md) — URML profiles that compose onto SDV-aligned safe-composition patterns.

## Unresolved questions

For the Eclipse SDV / Eclipse Foundation maintainers:

1. **Cross-citation framing preference.** Should URML's reference-runtime READMEs cite Eclipse SDV blueprints by name, by repo URL, or by Foundation-level reference?
2. **Aerospace-blueprint extension scope.** When does the aerospace extension reach the URML-drone-profile audience? Is there a working-group surface where URML's drone profile (RFC-0008) is reviewable as a related-art reference?
3. **Cross-WG citation conventions.** Are there Eclipse Foundation conventions for cross-WG citation (e.g., how Eclipse Cyclone DDS cites Eclipse iceoryx) that URML should follow?
4. **Foundation-level conversation.** With four Eclipse Foundation engagements now active (Cyclone DDS / Zenoh / iceoryx from Move-16 + SDV here), would the Eclipse Foundation prefer to convene a single project-collaboration conversation rather than per-project Issue threads?
5. **Member-track question.** URML is single-maintainer Phase-1; what's the Eclipse Foundation path for a future-foundation candidate that may eventually want to join Eclipse Foundation? (Asking for orientation only; this is a future-foundation question, not a Phase-1 ask.)
6. **Conformance listing.** Would Eclipse SDV consider a blueprints-website link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once cross-citation stabilizes?
7. **Anything else.**

## Implementation note

RFC-0212 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

`eclipse-sdv-blueprints/blueprints-website` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the cross-citation + Foundation-level framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (EPL-2.0, issues enabled, last push 2026-05-05, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (cross-WG fit risk, aerospace-extension timing, Eclipse engagement load).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Eclipse Foundation Brussels AISBL; NATO-allied; default policy passes.
- [x] CLAUDE.md compliance check passed.
