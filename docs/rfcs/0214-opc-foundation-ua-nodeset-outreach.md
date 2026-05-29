---
rfc: 0214
title: OPC Foundation UA-Nodeset (OPC UA Robotics Companion Spec) cross-citation, request for comment from OPC Foundation maintainers
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

# RFC-0214: OPC Foundation UA-Nodeset cross-citation

## Summary

URML's industrial-runtime track targets manipulation primitives that, on the OPC-UA-Robotics substrate, dispatch through the OPC UA Robotics Companion Specification. This RFC documents the proposed URML v0.1 cross-citation with the OPC Foundation's UA Robotics work, engaged via [`OPCFoundation/UA-Nodeset`](https://github.com/OPCFoundation/UA-Nodeset) (license verification pending), and **requests review and feedback from the OPC Foundation maintainers**. No spec change.

OPC UA Robotics has existed as a Companion Specification since 2018, and the OPC Foundation announced new Companion Specifications for AI / Agentic AI in 2026. URML's intent + capability-manifest model is structurally close to the OPC UA NodeSet semantic for declaring machine capabilities; cross-citation is the natural relationship.

## Motivation

The OPC UA Robotics Companion Specification defines a NodeSet for declaring robot capabilities, state, and command interfaces over OPC UA. URML's Layer-1 HAL + Layer-2 primitives are substrate-neutral declarations that, when targeting an OPC-UA-Robotics-compliant deployment, would dispatch through the OPC UA NodeSet. The relationship is parallel-and-composable rather than competing.

Repo at [`OPCFoundation/UA-Nodeset`](https://github.com/OPCFoundation/UA-Nodeset) (license TBD verify, issues enabled, last push `2026-05-09`, 268 stars, **not archived**). OPC Foundation (US + DE multi-national) governance.

URML benefits from documenting the engagement because:

1. **Industrial-runtime composition.** URML's industrial profile (RFC-0013) targets `pick_from`, `place_at`, `swap_tool` primitives that, on OPC-UA-Robotics deployments, would compose against the UA Robotics NodeSet. Cross-citation makes the composition explicit.
2. **Manifest-NodeSet alignment opportunity.** URML's capability-manifest declares what the robot can do; OPC UA NodeSet declares what the OPC UA server exposes. These are structurally close. Cross-citation may surface mapping opportunities (URML manifest field ↔ OPC UA NodeSet attribute).
3. **2026 AI / Agentic AI Companion Specs.** OPC Foundation's 2026 announcement extends Companion Specs to AI / Agentic AI. URML's NL-to-primitive translation + validator-gated execution is a concrete agentic-AI pattern relevant to those Companion Specs.

## Detailed design

### URML v0.1 cross-citation proposal

| URML surface | Maps to / cross-cites OPC UA Robotics |
|---|---|
| Layer-1 HAL (capability manifest) | Cross-citation with OPC UA Robotics NodeSet declaration |
| `manipulation.dispatch: opc_ua_robotics` (future enum) | Manifest enum value for OPC-UA-Robotics dispatcher |
| `pick_from`, `place_at`, `swap_tool` primitives (RFC-0013) | Compose against OPC UA Robotics NodeSet command interfaces |
| `safety_envelope` manifest field | Parallel to OPC UA Robotics safety-NodeSet pattern |
| Future URML — OPC UA Robotics NodeSet mapping | Out-of-scope for this RFC; future Spec RFC if cross-citation surfaces concrete mapping |

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Cross-citation in URML industrial-profile docs** — URML's industrial profile docs reference OPC UA Robotics as a substrate URML can compose against.
2. **License clarification ask.** The UA-Nodeset repo's license is not OSI-declared on the repo surface (verify at draft time). For URML's adapter posture, explicit OSI license on UA-Nodeset would unlock in-repo URML adapter framing; cross-citation works regardless.
3. **2026 AI / Agentic AI Companion Spec input.** URML offers its NL-translation + validator-gated-execution pattern as a related-art reference for the OPC Foundation's emerging AI / Agentic AI Companion Specs.

### Compatibility notes

- **Vendor org.** [`OPCFoundation`](https://github.com/OPCFoundation) — OPC Foundation (US-headquartered + DE branch).
- **Engagement repo.** [`OPCFoundation/UA-Nodeset`](https://github.com/OPCFoundation/UA-Nodeset) — license TBD verify, issues enabled, last push 2026-05-09, 268 stars, **not archived**.
- **Companion repos.** UA-Specification, UA-CompliancePlugin, UA-.NETStandard, UA-Java, UA-NodeSetSchema — the OPC UA family.
- **Origin.** OPC Foundation (US + DE multi-national). Passes US-federal default policy.
- **License fit.** OPC UA NodeSet license is repo-undeclared on UA-Nodeset surface; cross-citation works regardless. Adapter posture pending license verification.
- **Maintainer signal.** Active commits; 2026 AI / Agentic AI Companion Specs announced.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Cross-citation only.
- Reference runtime: future `reference/industrial-runtime/OPCUARoboticsAdapter` is a candidate when URML's industrial-runtime track ships; out of scope for this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-verification gating.** UA-Nodeset license is repo-undeclared; adapter-grade reuse depends on explicit OSI declaration or upstream clarification.
- **Manifest-NodeSet semantic mapping is non-trivial.** Real cross-citation may surface mapping-effort the maintainer groups need to scope jointly; this RFC does not propose the mapping itself.
- **OPC UA Robotics adoption is industrial-arm-specific.** URML's drone / mobile-base profiles do not compose against OPC UA Robotics; the cross-citation is scoped to industrial-arm.

## Alternatives considered

1. **Skip OPC Foundation; engage only at the UA-Nodeset technical level via Issues.** Rejected. The OPC Foundation governance layer is the right engagement for cross-citation framing; the technical Issue is the channel.
2. **Bundle UA-Robotics + 2026 AI / Agentic AI Companion Spec in a single RFC.** Considered. UA-Robotics is the existing surface; the 2026 AI Companion Specs are emerging. Engaging UA-Robotics first preserves a clean precedent for the 2026 AI Companion Spec input.
3. **Defer until URML ships an industrial-runtime adapter.** Rejected. The cross-citation is a positioning move that benefits from happening before the adapter, so adapter design can incorporate maintainer feedback.

## Prior art

- [`OPCFoundation/UA-Nodeset`](https://github.com/OPCFoundation/UA-Nodeset) — the upstream UA-Nodeset (engagement anchor).
- [OPC UA Robotics Companion Specification](https://opcfoundation.org/markets-collaboration/robotics/) — the canonical OPC UA Robotics spec.
- [RFC-0013 (industrial profile)](0013-industrial-profile.md) — URML's industrial profile (`pick_from`, `place_at`, `swap_tool`) that composes against OPC-UA-Robotics-compliant substrates.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md) — sibling industrial-manipulation engagement at the ROS 2 layer.

## Unresolved questions

For the OPC Foundation maintainers:

1. **License clarification.** Can the UA-Nodeset repo declare an explicit OSI license (or document its current license model in the README) to unlock URML adapter-grade reuse?
2. **Manifest-NodeSet mapping interest.** Is there OPC Foundation interest in scoping a URML-manifest ↔ OPC UA Robotics NodeSet semantic mapping? If yes, what's the channel — UA Robotics Working Group, joint working group, or per-Issue thread?
3. **2026 AI / Agentic AI Companion Spec input.** Does the OPC Foundation accept community input on emerging Companion Specs? URML's NL-translation + validator-gated-execution pattern is offered as a related-art reference for the AI / Agentic AI Companion Spec work.
4. **Industrial-arm scope.** URML's cross-citation is scoped to industrial-arm deployments; is OPC UA Robotics scope likewise industrial-arm, or does it extend to mobile-base / outdoor robotics?
5. **Cross-citation discipline.** URML proposes cross-citation in industrial-profile docs; preferred attribution shape from the OPC Foundation side?
6. **Conformance listing.** Would the OPC Foundation consider a UA-Robotics README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once URML's industrial-runtime adapter ships?
7. **Anything else.**

## Implementation note

RFC-0214 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

`OPCFoundation/UA-Nodeset` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the cross-citation + license-clarification asks explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (license TBD verify, issues enabled, last push 2026-05-09, 268 stars, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-verification gating, manifest-NodeSet mapping non-trivial, industrial-arm scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: OPC Foundation (US + DE multi-national); default policy passes.
- [x] CLAUDE.md compliance check passed.
