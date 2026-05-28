---
rfc: 0150
title: Microsoft PSI (Platform for Situated Intelligence) integration, request for comment from microsoft psi maintainers
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

# RFC-0150: Microsoft PSI (Platform for Situated Intelligence) integration, request for comment from microsoft psi maintainers

## Summary

URML does not yet ship a PSI manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Microsoft's Platform for Situated Intelligence — a temporal-streams + offline-replay framework for multi-modal sensor fusion — over [`microsoft/psi`](https://github.com/microsoft/psi), and **requests review and feedback from the microsoft psi maintainers**. **License clarification ask:** the repo's license is listed as "Other" by the GitHub API; an explicit OSI declaration is the gating ask. No spec change.

## Motivation

`microsoft/psi` is Microsoft's open-source framework for building situated agents over real-time multi-modal streams. License listed as "Other" (clarification ask), 570 stars, Issues + Discussions both enabled, last commit `2026-05-15` very active, **not archived**.

The URML-fit framing is **temporal-streams substrate declaration**. URML's manifest declares sensors individually; PSI provides the cross-sensor temporal-alignment + offline-replay infrastructure that downstream URML adapters can compose with. The manifest would declare `temporal_streams_substrate: microsoft_psi` to make the PSI binding observable.

URML's outreach is light-touch (Microsoft corporate research; the PSI team is small and the framework is general-purpose, not robot-specific). Engagement asks whether the manifest declaration fits PSI's design model.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `microsoft_psi_cell.yaml` fixture)

| URML field | Maps to PSI attribute |
|---|---|
| `name` | Deployment handle (`microsoft_psi_default`) |
| `temporal_streams.substrate: custom` (`microsoft_psi`) | Declares PSI is the temporal-streams framework |
| `temporal_streams.execution_model: online_or_offline_replay` | PSI supports both live and replay modes |
| `temporal_streams.clock_class` | PSI's deterministic clock model |
| `sensors` block | Individual sensor declarations remain unchanged; PSI consumes them as streams |

### What URML v0.1 does not yet express for PSI

1. **Temporal-streams substrate declaration.** URML's manifest does not today have a `temporal_streams` field. Spec RFC queued.
2. **Offline-replay execution-mode declaration.** PSI's distinguishing feature is record-and-replay; URML's manifest cannot today declare whether a deployment is live, replay, or both.
3. **Cross-sensor synchronization declaration.** PSI manages temporal alignment across sensors; URML's manifest declares sensors independently. The cross-sensor binding is implicit.
4. **License clarification.** "Other" upstream blocks Apache-2.0 reuse.

### Compatibility notes

- **Vendor org.** [`microsoft`](https://github.com/microsoft) — vendor-direct (Microsoft Research, Redmond).
- **Flagship repo.** [`microsoft/psi`](https://github.com/microsoft/psi) — license "Other" (clarification ask), 570 stars, Issues + Discussions both enabled, last commit 2026-05-15 active, **not archived**.
- **Origin.** Microsoft, Redmond, WA, US. Passes US-federal default policy.
- **License fit.** Pending clarification.
- **Maintainer signal.** Active surface with both Issues and Discussions; Microsoft Research engagement.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; temporal-streams substrate declaration Spec RFC queued.
- Reference runtime: cross-citation framing pending license clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate.** "Other" upstream license blocks Apache-2.0 downstream reuse.
- **Temporal-streams substrate Spec RFC prerequisite.**
- **General-purpose framework not robotics-specific.** URML-fit is "one temporal-streams substrate among many"; light-touch engagement.

## Alternatives considered

1. **Defer PSI until license clarifies.** Rejected. The RFC engagement is the clarification ask.
2. **Bundle PSI + CogACT (RFC-0151) into one Microsoft-broader RFC.** Rejected. PSI is temporal-streams infrastructure; CogACT is a VLA. Different layers, different teams.
3. **Cross-citation only with no manifest mapping.** Considered. Manifest mapping shape is concrete enough to evaluate; cross-citation alone is too thin.

## Prior art

- [`microsoft/psi`](https://github.com/microsoft/psi) — the upstream repo.
- [RFC-0151 (Microsoft CogACT)](0151-microsoft-cogact-outreach.md) — sibling Microsoft research engagement (different layer).
- [RFC-0048 (Anthropic MCP)](0048-anthropic-mcp-outreach.md) — Move-2 engaged adjacent corporate-research framework.

## Unresolved questions

For the microsoft psi maintainers:

1. **License clarification.** Can `microsoft/psi` get an explicit OSI license declaration?
2. **Temporal-streams substrate manifest fields.** URML's v0.1 has no `temporal_streams` declaration. Spec RFC queued. Manifest field expectations from PSI perspective (clock class, replay-mode declaration, cross-sensor sync semantics)?
3. **Bridge home.** Cross-citation only (recommended pending license), URML repo, or Microsoft-maintained?
4. **Conformance listing.** Would the PSI maintainers consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
5. **Anything else.**

## Implementation note

RFC-0150 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`microsoft/psi` has Issues + Discussions both enabled. Discussions is the preferred surface for design-discussion. URML's planned channel: open a single Discussion in Ideas, pointing to this RFC, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license: Other, 570 stars, Issues + Discussions enabled, last commit 2026-05-15 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license gate, temporal-streams Spec-RFC prerequisite, general-purpose framework fit).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Microsoft Redmond US; default policy passes.
- [x] CLAUDE.md compliance check passed.
