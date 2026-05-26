---
rfc: 0102
title: Bear Robotics / Servi integration, research-collab proposal (off-GitHub developer-portal)
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-26
updated: 2026-05-26
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

# RFC-0102: Bear Robotics / Servi integration, research-collab proposal (off-GitHub developer-portal)

## Summary

URML proposes alignment with Bear Robotics (Servi delivery / hospitality cobot, US-domiciled) via the **Bear Cloud API developer portal** at [`cloud.api.bearrobotics.ai`](https://cloud.api.bearrobotics.ai/guides/getting-started/). The ask is **research-collab**: a documented mapping from URML's substrate-neutral primitive vocabulary to Bear's gRPC + REST fleet-orchestration API, with the option of a future `BearAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) once engagement signals confirm the right shape. **Engagement surface is off-GitHub** (the [`bearrobotics`](https://github.com/bearrobotics) GitHub org has 25 repos but no customer-facing product repo with Issues enabled; the only customer-facing surface is the developer portal). RFC-0088 (Imperial PRL) and RFC-0098 (Cornell AgXRP) are the off-GitHub-courtesy precedents. Third Move #8 RFC.

## Motivation

Bear Robotics Servi is the US-domiciled commercial leader in restaurant / hospitality / care-home delivery cobotics. The product is widely deployed (multi-thousand-unit field operations across hospitality and senior-living facilities) and Bear operates a first-class developer portal with gRPC + REST APIs for fleet orchestration. The audience overlap with URML's home-assistance Move #8 wave is partial but real: senior-living facilities, assisted-living homes, and large-residence hospitality all run Servi-class robots as part of a home-assistance continuum.

Verified surface (2026-05-26):
- **Bear Cloud API developer portal** at `cloud.api.bearrobotics.ai`. gRPC + REST surfaces documented; mission / delivery / fleet-management endpoints.
- [`bearrobotics`](https://github.com/bearrobotics) GitHub org: 25 public repos, mostly infrastructure forks (`spatio_temporal_voxel_layer`, `u-boot`, `pcl`, `gcc-toolchain`, `emqx`, etc.). **No customer-facing product repo with Issues enabled.** Engagement surface is the developer portal, not GitHub.
- HQ: Redwood City, CA, USA. $24M Series B context, multi-country deployment.

URML's specific value for Bear Robotics / Servi:
- **Substrate-neutral intent above the Bear Cloud API.** URML programs describe intent ("deliver dish to table 12 and return to staging"); the Bear Cloud API handles the actual fleet dispatch on Servi hardware. URML's substrate-Protocol abstraction sits at the intent layer above gRPC / REST.
- **Cross-platform retargetability for hospitality + care-home operators.** A URML program written against a Servi fleet retargets to a future research-grade delivery robot or to a heterogeneous fleet by manifest swap. The cross-vendor substrate-neutral story is the natural value proposition for senior-living facilities running mixed-vendor robotics.
- **Care-home + senior-living adjacency.** Servi is widely deployed in senior-living dining rooms; URML's home-assistance Move #8 framing treats senior-living as an adjacent home-assistance context. The natural-language layer benefits a senior-living operator authoring fleet behaviour without ML / robotics expertise.

## Detailed design (light, research-collab + off-GitHub)

URML's engagement is off-GitHub by default. The proposal is:

1. **Courtesy outreach via the Bear Cloud API developer portal** ([`cloud.api.bearrobotics.ai/guides/getting-started/`](https://cloud.api.bearrobotics.ai/guides/getting-started/)). URML's identity, motivation, and feedback questions. Light engagement payload; URML's RFC asks who at Bear is the right contact for substrate-neutral-orchestration discussion.
2. **If maintainers respond and a substantive engagement signal appears**, URML proposes a `BearAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) (proposed by [RFC-0100](0100-irobot-roomba-outreach.md)) targeting the gRPC + REST surface. Adapter integration follows the same pattern as RFC-0073 (Robotical Marty): adapter shipped externally in URML's reference runtime with hermetic tests against a fake-SDK injection.
3. **Cross-link to [RFC-0094 (Burro Robotics)](0094-burro-robotics-outreach.md)** + **[RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md)**: URML's substrate-neutral fleet-coordination story spans hospitality (Bear) + agriculture (Burro) + research multi-robot framework (Open-RMF). Documented mapping at the URML-side, not contingent on Bear's response.
4. **Senior-living + care-home framing.** URML's Move #8 home-assistance wave includes Servi specifically for the senior-living adjacency; the conformance discussion is care-home-friendly UX of natural-language fleet authoring.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified GitHub Issue surface for substantive product engagement.** Bear's GitHub org is infrastructure-only. URML's RFC documents this and frames engagement off-GitHub honestly (RFC-0088 / RFC-0098 precedents).
- **Cloud-only API.** Bear Cloud is cloud-based gRPC + REST. URML programs depending on a `BearAdapter` would require network connectivity to Bear's cloud. URML's RFC documents this constraint.
- **API access likely partner-gated.** The Bear Cloud developer portal documents the API but may require a developer agreement or partnership tier for substantive integration. URML's RFC asks for clarification on the access posture.
- **Hospitality / senior-living adjacency is real but not home-proper.** URML's Move #8 wave is "home assistance robotics"; Servi is a commercial-restaurant / senior-living delivery cobot. The adjacency is legitimate (senior-living = assisted-home-care continuum) but URML's RFC names the framing honestly.
- **Light engagement payload.** Off-GitHub courtesy means URML's research-collab proposal carries less detail than a Tier A vendor RFC with a public adapter pre-design. The substantive depth comes from Bear's response, not from this RFC body.

## Alternatives considered

1. **Ship a `BearAdapter` first against the public-documented Bear Cloud API without engaging.** Rejected. The Bear Cloud API may require a developer agreement; URML's adapter integration depends on access clarity. Off-GitHub courtesy is appropriate.
2. **Fold Bear Robotics into [RFC-0094 (Burro Robotics)](0094-burro-robotics-outreach.md) as a generic commercial-cobot-fleet RFC.** Rejected. Different verticals (hospitality / senior-living vs agriculture), different API surfaces, different audiences. Conflating obscures both engagements.
3. **Skip Bear Robotics for Move #8 and revisit in a future hospitality-vertical wave.** Considered but rejected on the senior-living-adjacency reasoning above. URML's Move #8 framing legitimately includes care-home / senior-living delivery as a home-assistance continuum.

## Prior art

- Bear Cloud API developer portal at `cloud.api.bearrobotics.ai`.
- [`bearrobotics`](https://github.com/bearrobotics) GitHub org (25 repos, mostly infrastructure forks).
- [RFC-0094 (Burro Robotics)](0094-burro-robotics-outreach.md): the agricultural commercial-cobot-fleet RFC (Move #7); same substrate-neutral fleet-coordination story.
- [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md): the multi-robot framework RFC; Open-RMF is the open-source counterpart to Bear Cloud's proprietary fleet management.
- [RFC-0088 (Imperial Personal Robotics Lab)](0088-imperial-personal-robotics-outreach.md): off-GitHub courtesy outreach precedent (Move #6).
- [RFC-0098 (Cornell AgXRP)](0098-cornell-agxrp-outreach.md): off-GitHub courtesy outreach precedent (Move #7).
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): the engagement → adapter-shipment pattern URML would follow if Bear engagement signals interest.

## Unresolved questions

For Bear Robotics developer relations:

1. **API access posture.** Is the Bear Cloud API available to integration partners on request, or is a commercial partnership required for substantive integration?
2. **Adapter home.** If URML ships a `BearAdapter`, would `reference/home-runtime/` (URML-side) be appropriate, or would Bear prefer a contributed example in a Bear-operated repo?
3. **Engagement surface.** Is the developer portal Contact form the right channel, a specific dev-relations email, or a different surface?
4. **Senior-living + care-home framing.** Is URML's home-assistance framing for Servi (as a care-home delivery cobot) consistent with Bear's product positioning, or does Bear prefer the hospitality-restaurant framing?
5. **Multi-vendor fleet orchestration.** Is URML's substrate-neutral programming model interesting to Bear's product / engineering side?
6. **Conformance lane.** Open to a URML conformance line in Bear's developer portal documentation?
7. **Anything else.**

## Implementation note

RFC-0102 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Third Move #8 RFC. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`cloud.api.bearrobotics.ai` has a developer-portal contact / signup surface (verified 2026-05-26). URML's planned channel: courtesy outreach via the Bear Cloud developer portal Contact form pointing at this RFC. If Bear responds with a public GitHub Issue surface or a specific dev-relations email, URML pivots accordingly.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub + research-collab framing explicit.
- [x] No verified GitHub Issue surface acknowledged honestly (bearrobotics org is infrastructure-only).
- [x] Care-home / senior-living adjacency framing surfaced honestly (Servi is hospitality-first; senior-living is the home-assistance bridge).
- [x] Cross-link to RFC-0094 (commercial-cobot-fleet precedent) + RFC-0053 (Open-RMF) + RFC-0088 / RFC-0098 (off-GitHub precedents) + RFC-0073 (engagement-to-adapter pattern) explicit.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no GitHub Issue surface, cloud-only, partner-gated access, adjacency framing).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26 (absence of customer-facing GitHub repo documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
