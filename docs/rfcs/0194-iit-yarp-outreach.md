---
rfc: 0194
title: IIT YARP middleware (alternate-substrate sibling to URML's ros2-runtime) integration, request for comment from robotology maintainers
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

# RFC-0194: IIT YARP middleware — alternate-substrate sibling to URML's ros2-runtime

## Summary

URML does not yet ship a YARP-substrate adapter. This RFC documents the proposed URML v0.1 capability-manifest **cross-citation** for YARP (Yet Another Robot Platform) — IIT's alternate-substrate robot middleware — over [`robotology/yarp`](https://github.com/robotology/yarp), and **requests review and feedback from the robotology maintainers**. **LGPL license** classes this as Tier B with cross-citation framing (URML's Apache-2.0 stance composes carefully with LGPL). No spec change.

This RFC is the **middleware sibling** to RFC-0192 IIT iCub. iCub runs on YARP; URML's engagement at the platform layer composes with YARP at the substrate layer. The two RFCs are independent but mutually informative.

## Motivation

YARP (Yet Another Robot Platform) is IIT's open-source middleware for robotics — a network-transparent inter-process communication framework predating ROS, used extensively in iCub and across IIT's research stack. It's a structural alternate to ROS 2 for substrate-level message passing and component coordination.

Repo at [`robotology/yarp`](https://github.com/robotology/yarp) (LGPL — Other-classified, 592 stars, Issues enabled, last commit `2026-05-18` very active — 10 days from cutoff, **not archived**).

URML benefits from documenting YARP as an alternate substrate because:

1. **URML's substrate-neutral claim depends on declaring more than one substrate.** URML's existing `reference/ros2-runtime/` adapter targets ROS 2. YARP is the sibling middleware; declaring it makes URML's substrate-neutrality concrete in the manifest.
2. **Medical-research / European-research deployments often use YARP.** iCub (RFC-0192) and IIT's broader stack run on YARP; URML's manifest needs to declare these substrates cleanly.
3. **LGPL is the gating fact for adapter shape.** LGPL allows linking from non-LGPL code if the LGPL library is unmodified; URML's adapter pattern composes at the API boundary without modifying YARP, which is the LGPL-compatible posture.

## Detailed design

### URML v0.1 capability-manifest mapping (cross-citation framing for `iit_yarp_substrate_cell.yaml` fixture)

| URML field | Maps to YARP attribute |
|---|---|
| `substrate.middleware: custom` (`yarp`) | Declares YARP as the inter-process middleware (alternate to ROS 2) |
| `substrate.middleware_version` | YARP release version pin |
| `substrate.network_transport` | YARP TCP / UDP / shared-memory transport class |
| `substrate.license_class: custom` (`lgpl_linkable`) | Declares LGPL substrate; URML's manifest can carry this constraint visibly |

### What URML v0.1 does not yet express for YARP

1. **Alternate-substrate middleware declaration.** URML's v0.1 manifest implicitly assumes ROS 2 at the substrate layer. Spec RFC for alternate-substrate declaration queued.
2. **LGPL substrate declaration.** URML's manifest doesn't today declare substrate license-class. Spec RFC for license-class manifest field queued.
3. **YARP-vs-ROS-2 deployment composition.** Some IIT deployments use YARP exclusively; some bridge YARP↔ROS-2. URML's manifest cannot today declare the bridging topology.

### Compatibility notes

- **Research lab / org.** [`robotology`](https://github.com/robotology) — Italian Institute of Technology (IIT), Genoa.
- **Flagship repo.** [`robotology/yarp`](https://github.com/robotology/yarp) — LGPL (Other-classified by GitHub), 592 stars, Issues enabled, last commit 2026-05-18 very active, **not archived**.
- **Companion repo.** `robotology/icub-main` (BSD-3-Clause) — primary YARP downstream user; engaged via RFC-0192.
- **Origin.** Italian Institute of Technology (IIT), Genoa, Italy. Passes US-federal default policy (NATO+EU).
- **License fit.** LGPL — linkable from URML's Apache-2.0 adapter without license contamination if URML's adapter does not modify YARP. Cross-citation framing recommended.
- **Maintainer signal.** Very active substrate maintenance; foundational European robotics middleware.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; alternate-substrate middleware + substrate-license-class + YARP↔ROS-2 bridging declarations Spec RFCs queued.
- Reference runtime: future `reference/yarp-runtime/` subdirectory is a candidate; sibling to `reference/ros2-runtime/`. Cross-citation framing pending Spec RFC + LGPL-boundary clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **LGPL substrate declaration is novel manifest territory.**
- **Multiple Spec-RFC prerequisites** (alternate-substrate, license-class, bridging-topology).
- **URML's existing substrate assumption is implicit ROS 2.** Engagement may surface architectural rework if YARP-substrate URML deployments warrant first-class declaration.

## Alternatives considered

1. **Engage YARP only as iCub's substrate, via RFC-0192.** Rejected. YARP is a substrate platform in its own right with non-iCub deployments; per-target RFC at the middleware layer is the cleaner shape.
2. **Treat YARP as out-of-scope because URML is ROS-2-first.** Rejected. URML's substrate-neutral claim depends on declaring more than ROS 2; YARP is the most-mature alternate URML's outreach surfaced.
3. **Cross-citation only (no manifest mapping).** Tier B framing keeps cross-citation as recommended posture pending LGPL + Spec RFC clarification.

## Prior art

- [`robotology/yarp`](https://github.com/robotology/yarp) — the upstream YARP middleware.
- [`robotology/icub-main`](https://github.com/robotology/icub-main) — iCub humanoid (engaged via RFC-0192) is the primary YARP downstream.
- URML's existing `reference/ros2-runtime/` — the sibling-layer adapter YARP would be alternate to.

## Unresolved questions

For the robotology YARP maintainers:

1. **Alternate-substrate middleware manifest declaration.** URML's v0.1 has no `substrate.middleware: yarp` declaration. Spec RFC queued. Manifest field expectations from the YARP perspective (version, transport class, port naming convention)?
2. **LGPL substrate license-class declaration.** Should URML's manifest declare LGPL-linkable substrate as a first-class field for downstream operator awareness?
3. **YARP↔ROS-2 bridging declaration.** Some deployments bridge between YARP and ROS 2; manifest field for declaring bridging topology?
4. **Bridge home.** Cross-citation only (recommended pending LGPL framing), URML repo (`reference/yarp-runtime/`), or IIT-maintained `robotology/yarp-urml-bridge`?
5. **Conformance listing.** Would IIT consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

## Implementation note

RFC-0194 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move15.yaml`](../../examples/lighthouses/outreach-move15.yaml).

## How to respond

`robotology/yarp` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit cross-citation framing + LGPL boundary acknowledgement.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (LGPL, 592 stars, Issues enabled, last commit 2026-05-18 very active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (LGPL substrate novelty, multiple Spec-RFC prerequisites, ROS-2-first substrate assumption).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Italian Institute of Technology IT Genoa; default policy passes.
- [x] CLAUDE.md compliance check passed.
