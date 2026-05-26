---
rfc: 0105
title: Luxonis OAK-D / DepthAI integration, request for comment from luxonis maintainers
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

# RFC-0105: Luxonis OAK-D / DepthAI integration, request for comment from luxonis maintainers

## Summary

URML proposes alignment with Luxonis (US-domiciled) via the [`luxonis`](https://github.com/luxonis) GitHub org. Anchor repos: [`luxonis/depthai-ros`](https://github.com/luxonis/depthai-ros) (MIT, 346 stars, 205 open issues, Issues enabled, last commit 2026-05-18) and [`luxonis/depthai-python`](https://github.com/luxonis/depthai-python) (MIT, 429 stars, 93 open issues, Issues + Discussions enabled, last commit 2026-05-23). The ask is **research-collab**: a documented mapping from URML's `measure` + `wait_for` primitives to DepthAI's perception streams (depth, IMU, AI inference). No spec change on URML's side. Sixth Move #8 RFC.

Luxonis is the open-source 3D-perception counterpart for affordable home / educational / research robotics. Where the OAK-D camera ships, URML's perception-driven primitives have a natural substrate.

## Motivation

OAK-D is the de facto affordable 3D-perception module for home / educational / research robotics. The combination of stereo depth + inertial fusion + on-device AI inference at the OAK-D price point covers the perception layer that URML's `measure(depth)` and `wait_for(object_detected)` primitives target. DepthAI ships with first-class ROS 2 + Python bindings, both MIT-licensed.

Verified surface (2026-05-26):
- [`luxonis/depthai-ros`](https://github.com/luxonis/depthai-ros): MIT, 346 stars, 205 open issues, Issues enabled, last commit 2026-05-18 (active).
- [`luxonis/depthai-python`](https://github.com/luxonis/depthai-python): MIT, 429 stars, 93 open issues, Issues + Discussions enabled, last commit 2026-05-23 (active).
- Hardware schematics partially open via [`luxonis/oak-hardware`](https://github.com/luxonis/oak-hardware).
- HQ: Westminster, CO, USA.

URML's specific value for the Luxonis / DepthAI ecosystem:
- **URML's perception-substrate composition.** OAK-D streams depth + IMU + AI-inference output; URML's `measure(depth)` + `measure(orientation)` + `wait_for(object_detected)` primitives compose directly. The substrate-neutral story: a URML program written against OAK-D retargets to a future ZED or RealSense by manifest swap.
- **MIT license fit.** URML's `reference/` is Apache-2.0; MIT is compatible. Cross-citation, contributed examples, and adapter code can flow without license-fit nuance.
- **Home + educational + research audience overlap.** OAK-D ships in academic labs, makers' workshops, and Tier B research-grade home robots. The audience overlaps directly with URML's Move #3 (educational), Move #6 (university labs), and the current Move #8 (home assistance) waves.
- **Strategic positioning vs industrial Move #1 perception vendors.** Move #1 touched Ouster (industrial LiDAR) and SICK (industrial safety scanners). Luxonis OAK-D is the **home-scale / educational / research counterpart** at the perception layer; this RFC opens the home-scale-perception segment of URML's outreach landscape (sibling to [RFC-0104 (ROBOTIS Dynamixel)](0104-robotis-dynamixel-outreach.md) on the actuator side).

## Detailed design

URML's existing artifacts that feed into a Luxonis OAK-D cross-citation:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives (including `measure`).
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles relevant to OAK-D's audience.

### Proposed composition (no new sub-package)

Like [RFC-0104 (ROBOTIS Dynamixel)](0104-robotis-dynamixel-outreach.md), this RFC proposes **documented cross-citation rather than a stand-alone adapter**. OAK-D is a perception substrate; URML's per-platform adapters compose with DepthAI internally at the perception layer. The proposal is:

1. **Documented cross-citation in URML's `reference/` runtimes**, naming OAK-D as a candidate perception substrate for affordable home / educational / research robots.
2. **A DepthAI-conformance test fixture** in URML's `conformance/` suite that asserts URML's `measure(depth, ...)` round-trips through DepthAI's depth stream for a representative configuration. Hermetic; uses a recorded `.bag` file or a fake-SDK injection.
3. **Cross-link to URML's existing edu-runtime + future home-runtime**: the URML-side composition narrative.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: documented cross-citation only; no new Luxonis sub-package.
- Conformance suite: proposed new DepthAI-conformance test fixture (hermetic). Not built in this PR.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.**
- **Component-vendor outreach is indirect.** Like RFC-0104 ROBOTIS, Luxonis is a substrate vendor (perception module inside platforms), not a platform vendor. URML's value to Luxonis is the composition-narrative.
- **Multiple OAK-D variants.** OAK-D, OAK-D Pro, OAK-D-Lite, OAK-D S2, OAK-4, etc., with different sensor modalities. URML's documented cross-citation should target a primary variant (OAK-D S2 or OAK-4 likely).
- **High open-issue count on `depthai-ros`.** 205 open issues at verification time signals active community + significant maintenance load. URML's RFC respects the maintainer bandwidth and frames the ask lightly.
- **MIT license + Apache-2.0 patent grant asymmetry.** MIT does not include the Apache-2.0 patent grant; legal review for any contributed code is non-trivial but tractable.

## Alternatives considered

1. **Ship a `LuxonisAdapter` directly in URML's `reference/`.** Rejected; perception modules sit inside platform adapters, not alongside them. Stand-alone perception adapters invert the layering.
2. **Engage Intel RealSense instead.** Rejected; the Intel RealSense team was largely disbanded in 2021 (engineers absorbed into Apple / Microsoft); the librealsense org migration to `realsenseai` is still in progress and engagement signal is low. Luxonis is the active counterpart.
3. **Engage Stereolabs ZED instead.** Considered but held back for a possible perception-focused Move #9. ZED hardware is more closed than OAK-D and the OAK-D price point is closer to URML's home-assistance Move #8 audience.

## Prior art

- [`luxonis`](https://github.com/luxonis) GitHub org (20+ repos).
- [`luxonis/depthai-ros`](https://github.com/luxonis/depthai-ros) (MIT, 346 stars).
- [`luxonis/depthai-python`](https://github.com/luxonis/depthai-python) (MIT, 429 stars, Discussions enabled).
- [`luxonis/oak-hardware`](https://github.com/luxonis/oak-hardware) (partially open hardware schematics).
- [`reference/edu-runtime/`](../../reference/edu-runtime/): URML's existing educational-runtime; OAK-D is a candidate perception substrate.
- [RFC-0032 (Ouster)](0032-ouster-integration.md), [RFC-0033 (SICK)](0033-sick-integration.md): the industrial-perception-vendor outreach precedent from Move #1; Luxonis OAK-D is the home-scale counterpart.
- [RFC-0104 (ROBOTIS Dynamixel)](0104-robotis-dynamixel-outreach.md): the actuator-substrate sibling in the same Move #8 wave.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For the `luxonis` maintainers:

1. **Cross-citation appetite.** Is Luxonis open to a documented cross-citation in URML's `reference/` runtimes and conformance suite, naming OAK-D as a candidate perception substrate?
2. **Primary-variant manifest.** Which OAK-D variant (OAK-D S2, OAK-D Pro, OAK-4) is the right primary target for URML's documented mapping?
3. **DepthAI v3 trajectory.** Is DepthAI v3 (the next-generation Python API) the right substrate target, or should URML's cross-citation target v2 for stability?
4. **Conformance lane.** Open to a URML conformance line on `depthai-ros` or `depthai-python` README?
5. **Educational + research profile co-design.** RFC-0011 / RFC-0012 raised the broader profile-design discussion; Luxonis's perspective from the affordable-perception side would inform the future Spec RFC.
6. **GitHub Discussions vs Issues.** `depthai-python` has Discussions enabled; would Luxonis prefer URML's research-collab thread there rather than as an Issue?
7. **Anything else.**

## Implementation note

RFC-0105 ships as a single RFC document PR. No adapter code in this PR. Sixth Move #8 RFC. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`luxonis/depthai-python` has Discussions enabled (verified 2026-05-26). URML's planned channel: open a single Discussion on `luxonis/depthai-python` (Discussions surface preferred over Issues for research-collab framing), pointing to this RFC. Optional cross-thread on `depthai-ros` if Luxonis prefers a ROS 2-specific surface.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] MIT license fit acknowledged.
- [x] Cross-link to RFC-0032 / RFC-0033 (Move #1 perception-vendor precedents) + RFC-0104 (actuator-substrate sibling in Move #8) explicit.
- [x] Documented cross-citation framing (not a stand-alone adapter) justified.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, indirect composition, multi-variant ambiguity, high open-issue count, MIT-Apache patent-grant asymmetry).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
