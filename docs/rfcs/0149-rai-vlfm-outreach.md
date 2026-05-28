---
rfc: 0149
title: RAI Institute VLFM (Vision-Language Frontier Maps for navigation) integration, request for comment from rai-opensource maintainers
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

# RFC-0149: RAI Institute VLFM (Vision-Language Frontier Maps) integration, request for comment from rai-opensource maintainers

## Summary

URML does not yet ship a VLFM manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for VLFM — Vision-Language Frontier Maps for VLM-based robot navigation — over [`rai-opensource/vlfm`](https://github.com/rai-opensource/vlfm) (MIT), and **requests review and feedback from the rai-opensource maintainers**. No spec change.

This RFC is the navigation-substrate companion to [RFC-0148 (RAI Theia)](0148-rai-theia-outreach.md). Both are vendor-direct from the Boston Dynamics AI Institute (RAI Institute); both engage at the perception / navigation substrate layer one step above URML's primitive vocabulary.

## Motivation

`rai-opensource/vlfm` is the ICRA 2024 publication of VLM-based navigation using frontier-map exploration. MIT license, 749 stars, Issues enabled, last commit `2025-11-12` (~6mo from 2026-05-28 cutoff; just at edge of URML's recency window), **not archived**.

URML's mobility primitives (`move_to`, `dock`, `scan`) compose with VLM-based frontier-map navigation cleanly: URML declares the navigation-substrate class in the manifest; VLFM dispatches the actual exploration; URML's validator gates the manifest-aware constraints (operating zones, safety envelopes per RFC-0012).

VLFM's distinct contribution is **language-conditioned navigation**. The robot operator says "find the kitchen and inspect the stove"; VLFM uses a vision-language model to ground the language in the frontier map; URML's primitive vocabulary executes the dispatched waypoint sequence.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `rai_vlfm_navigation_cell.yaml` fixture)

| URML field | Maps to VLFM attribute |
|---|---|
| `name` | Deployment handle (`rai_vlfm_default`) |
| `navigation_substrate: custom` (`rai_vlfm`) | Declares VLFM is the navigation substrate |
| `navigation_substrate.input_modality: rgb+language` | VLFM consumes RGB + natural-language goals |
| `navigation_substrate.exploration_class: frontier_map` | VLFM's frontier-map exploration semantics |
| `mobility.drive_type` | URML's existing mobility class the VLFM-dispatched waypoints execute on |

### What URML v0.1 does not yet express for VLFM

1. **Navigation-substrate declaration.** URML's manifest does not today have a `navigation_substrate` field. Spec RFC queued (companion to vision-foundation-model substrate from RFC-0148).
2. **Language-conditioned navigation declaration.** URML's `move_to` primitive consumes coordinates; VLFM-style language-conditioned navigation needs a higher-level binding URML's primitive vocabulary doesn't yet declare.
3. **Frontier-map state declaration.** VLFM maintains exploration state (frontier coverage); URML's manifest cannot today declare this stateful substrate dependency.

### Compatibility notes

- **Vendor / lab.** [`rai-opensource`](https://github.com/rai-opensource) — RAI Institute vendor-direct.
- **Flagship repo.** [`rai-opensource/vlfm`](https://github.com/rai-opensource/vlfm) — MIT, 749 stars, Issues enabled, last commit 2025-11-12 (just at recency edge), **not archived**.
- **Origin.** RAI Institute (US). Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** ICRA 2024 publication anchor; cleaner license than RFC-0148 Theia.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; navigation-substrate + language-conditioned-navigation Spec RFCs queued.
- Reference runtime: future `reference/navigation-runtime/VlfmAdapter` is a candidate; composes above URML's mobility primitives.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Two Spec-RFC prerequisites** (navigation-substrate + language-conditioned-navigation).
- **Stateful substrate dependency.** Frontier-map state is across-call persistent; URML's manifest is currently stateless.
- **Just-at-edge recency.** Last commit ~6mo; light-touch expected.

## Alternatives considered

1. **Bundle VLFM + Theia (RFC-0148) into one RAI Institute RFC.** Rejected. Per-repo RFCs let conversation thread per flagship.
2. **Defer until language-conditioned navigation Spec RFC lands.** Rejected. VLFM maintainer input shapes the Spec RFC.
3. **Engage RAI Institute broader instead of per-repo.** Considered. Per-flagship engagement is the cleaner shape; broader engagement can follow.

## Prior art

- [`rai-opensource/vlfm`](https://github.com/rai-opensource/vlfm) — the upstream repo.
- [RFC-0148 (RAI Theia)](0148-rai-theia-outreach.md) — sibling RAI Institute RFC at the vision-foundation-model layer.
- [RFC-0043 (Spot)](0043-spot-outreach.md) — Move-2 engaged Tim Perkins on rai-opensource COLLABORATOR side (different repo, different maintainer).

## Unresolved questions

For the rai-opensource vlfm maintainers:

1. **Navigation-substrate manifest fields.** URML's v0.1 has no `navigation_substrate` declaration. Spec RFC queued. Manifest field expectations?
2. **Language-conditioned navigation primitive declaration.** Should URML's manifest declare which language-grounded navigation primitives VLFM supports?
3. **Frontier-map state declaration.** Stateful substrate dependency manifest fields?
4. **Bridge home.** URML repo (`reference/navigation-runtime/VlfmAdapter`), RAI-maintained, or external?
5. **Conformance listing.** Would the maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships?
6. **Anything else.**

## Implementation note

RFC-0149 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`rai-opensource/vlfm` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 749 stars, Issues enabled, last commit 2025-11-12, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (two Spec-RFC prerequisites, stateful substrate, recency at edge).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: RAI Institute US; default policy passes.
- [x] CLAUDE.md compliance check passed.
