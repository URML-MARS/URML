---
rfc: 0104
title: ROBOTIS Dynamixel integration, request for comment from ROBOTIS-GIT maintainers
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

# RFC-0104: ROBOTIS Dynamixel integration, request for comment from ROBOTIS-GIT maintainers

## Summary

URML proposes alignment with ROBOTIS (Korea-domiciled, KR US-friendly geo) via the [`ROBOTIS-GIT`](https://github.com/ROBOTIS-GIT) GitHub org (80+ public repos, Apache-2.0 predominant, ROS 2 native). The ask is **vendor-style integration**: ROBOTIS Dynamixel is the de facto servo backbone for affordable home / educational / quadruped / arm robotics, and URML's Layer-2 primitive vocabulary composes naturally at the actuator-substrate layer. Anchor repos: [`ROBOTIS-GIT/DynamixelSDK`](https://github.com/ROBOTIS-GIT/DynamixelSDK) (Apache-2.0, 587 stars, 14 open issues, Issues enabled, last commit 2026-05-20) and [`ROBOTIS-GIT/dynamixel_hardware_interface`](https://github.com/ROBOTIS-GIT/dynamixel_hardware_interface) (Apache-2.0, 34 stars, 8 open issues, Issues enabled, last commit 2026-05-15). No spec change on URML's side. Fifth Move #8 RFC; the first servo-vendor RFC in URML's outreach landscape.

## Motivation

ROBOTIS Dynamixel is the most widely deployed servo family in research / educational / consumer humanoid / quadruped / arm robotics globally. The Dynamixel SDK ships in Apache-2.0 with first-class ROS 2 integration; URML's `reference/edu-runtime/` already implicitly depends on Dynamixel for several educational platforms. Surfacing the relationship explicitly with the ROBOTIS maintainers is the first servo-vendor RFC in URML's outreach landscape.

Verified surface (2026-05-26):
- [`ROBOTIS-GIT`](https://github.com/ROBOTIS-GIT) GitHub org: 80+ public repos, Issues enabled, Apache-2.0 predominant.
- Top: `DynamixelSDK` 587 stars, `dynamixel-workbench` (planning controllers), `dynamixel_hardware_interface` 34 stars (ROS 2 hardware-interface bridge), `OpenManipulator`, `turtlebot3`, etc.
- ROS 2 native; active maintenance through May 2026.
- HQ: Seoul, South Korea. KR-friendly geo (RFC-0003 compliance: KR is US-friendly).

URML's specific value for the ROBOTIS ecosystem:
- **URML's actuator-substrate composition.** Dynamixel is the actuator layer; URML's `move_to(joint_pose)` for arm / humanoid platforms decomposes to per-servo position commands dispatched via the Dynamixel SDK. The composition is well-defined: URML at the intent layer, Dynamixel at the actuator layer, with ROS 2 as the canonical intermediate substrate.
- **Apache-2.0 license fit.** URML's `reference/` is Apache-2.0 too; cross-citation, contributed examples, and adapter code can flow both ways without license-fit nuance.
- **Cross-link to URML's existing `reference/edu-runtime/`.** URML's educational runtime already targets several Dynamixel-powered platforms; surfacing the ROBOTIS relationship makes the substrate dependency explicit and benefits the affordable-humanoid / DIY-quadruped audience URML's natural-language layer serves.
- **Strategic positioning vs industrial Move #1.** URML's Move #1 touched industrial component vendors (Ouster, SICK, Festo, SCHUNK). ROBOTIS Dynamixel is the **home-scale / educational / research counterpart** to those industrial Move #1 RFCs; this RFC opens the home-scale-component segment of URML's outreach landscape.

## Detailed design

URML's existing artifacts that feed into a ROBOTIS Dynamixel cross-citation:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`reference/edu-runtime/`](../../reference/edu-runtime/): URML's existing educational-runtime; several adapters implicitly depend on Dynamixel.
- [RFC-0009](0009-legged-humanoid-mobility.md): URML's mobility-capability schema; Dynamixel-driven quadrupeds and humanoids are direct targets.

### Proposed composition (no new sub-package)

The proposal is **not** a new ROBOTIS sub-package in URML's `reference/`. Dynamixel is an actuator substrate; URML's existing per-platform adapters (`reference/edu-runtime/` for educational humanoid / arm targets, future `reference/home-runtime/` adapters for home-scale humanoids) already compose with the Dynamixel SDK at their hardware layer. The proposal is:

1. **Documented cross-citation in URML's `reference/edu-runtime/README.md`** naming Dynamixel as the canonical actuator substrate for several existing adapters.
2. **A Dynamixel-conformance test fixture** in URML's `conformance/` suite that asserts URML's `move_to(joint_pose)` round-trips through the Dynamixel SDK for a representative joint configuration. Hermetic; uses a fake-SDK injection (same pattern as URML's other hardware integrations).
3. **Cross-link to [RFC-0009 (legged + humanoid mobility)](0009-legged-humanoid-mobility.md)**: URML's mobility-capability schema must encode Dynamixel-driven joints; the cross-citation surfaces that dependency.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: documented cross-citation only; no new ROBOTIS sub-package.
- Conformance suite: proposed new Dynamixel-conformance test fixture (hermetic, fake-SDK). Not built in this PR.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.**
- **Component-vendor outreach is indirect.** Unlike Move #1's industrial-component vendors (Ouster, SICK, Festo, SCHUNK) which control a clear substrate boundary, Dynamixel is the actuator layer inside many platforms. URML's value to ROBOTIS is the composition-narrative, not a direct substrate-adapter.
- **Multiple Dynamixel models with different protocol versions.** Protocol 1.0 vs 2.0; XL-320, AX-12A, MX-28, XM-430, XW-540, etc. URML's documented cross-citation should target Protocol 2.0 (the current canonical surface) explicitly.
- **ROBOTIS also operates closed-product lines.** The OpenManipulator and TurtleBot3 are open-source but ROBOTIS also sells closed humanoid products (OP3, etc.); URML's outreach engages the open-source side, not the closed-product side.

## Alternatives considered

1. **Ship a `DynamixelAdapter` directly in URML's `reference/`.** Rejected. Dynamixel is an actuator substrate, not a platform substrate. URML's per-platform adapters (edu-runtime, home-runtime, cobot-runtime) compose with Dynamixel internally; a stand-alone `DynamixelAdapter` would invert the layering.
2. **Engage the ROBOTIS Korean-language community channel.** Rejected; `ROBOTIS-GIT` GitHub is the documented English-language engagement surface; ROBOTIS maintains it actively. URML's RFC posts in English with the option to follow up in Korean if maintainers prefer.
3. **Fold ROBOTIS Dynamixel into a broader actuator-vendor RFC covering Maxon + Faulhaber + Dynamixel.** Rejected. Different audiences (industrial DC + brushless motors vs hobbyist / research smart servos); ROBOTIS specifically warrants its own home-scale-component RFC.

## Prior art

- [`ROBOTIS-GIT`](https://github.com/ROBOTIS-GIT) GitHub org (80+ repos, Apache-2.0 predominant).
- [`ROBOTIS-GIT/DynamixelSDK`](https://github.com/ROBOTIS-GIT/DynamixelSDK) (Apache-2.0, 587 stars).
- [`ROBOTIS-GIT/dynamixel_hardware_interface`](https://github.com/ROBOTIS-GIT/dynamixel_hardware_interface) (Apache-2.0, 34 stars, ROS 2 hardware-interface bridge).
- [`ROBOTIS-GIT/OpenManipulator`](https://github.com/ROBOTIS-GIT/OpenManipulator), [`ROBOTIS-GIT/turtlebot3`](https://github.com/ROBOTIS-GIT/turtlebot3): Apache-2.0 platforms that bundle Dynamixel.
- [`reference/edu-runtime/`](../../reference/edu-runtime/): URML's existing educational-runtime.
- [RFC-0009 (legged + humanoid mobility)](0009-legged-humanoid-mobility.md): mobility-capability schema.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles relevant to Dynamixel-powered platforms.
- [RFC-0031 (SCHUNK)](0031-schunk-integration.md), [RFC-0032 (Ouster)](0032-ouster-integration.md), [RFC-0033 (SICK)](0033-sick-integration.md), [RFC-0034 (Festo)](0034-festo-integration.md): the industrial-component-vendor outreach precedent from Move #1; ROBOTIS Dynamixel is the home-scale counterpart.

## Unresolved questions

For the ROBOTIS-GIT maintainers:

1. **Cross-citation appetite.** Is ROBOTIS open to a documented cross-citation in URML's `reference/edu-runtime/README.md` and in the conformance suite, naming Dynamixel as the canonical actuator substrate for affordable humanoid / arm / quadruped robotics?
2. **Conformance lane.** Open to a URML conformance line on the `DynamixelSDK` or `dynamixel_hardware_interface` README?
3. **Adapter-layering question.** Does ROBOTIS prefer URML's adapters to invoke Dynamixel via the SDK directly, or via the ROS 2 `dynamixel_hardware_interface` (cleaner separation but heavier ROS 2 dependency)?
4. **Educational-profile co-design.** URML's RFC-0011 educational profile would benefit from a ROBOTIS perspective on the right Layer-3 vocabulary for Dynamixel-driven platforms.
5. **OpenManipulator + TurtleBot3 specific manifests.** URML's manifest schema would benefit from authoritative mass / DOF / payload values for ROBOTIS's flagship open platforms.
6. **Korean-language follow-up.** Is English sufficient, or would Korean follow-up be preferred for substantive technical discussion?
7. **Anything else.**

## Implementation note

RFC-0104 ships as a single RFC document PR. No adapter code in this PR. Fifth Move #8 RFC; first servo-vendor RFC. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`ROBOTIS-GIT/DynamixelSDK` has Issues enabled (14 open, verified 2026-05-26). URML's planned channel: open a single Issue on `ROBOTIS-GIT/DynamixelSDK` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC. Optional cross-thread on `dynamixel_hardware_interface` if ROBOTIS prefers a ROS 2-specific surface.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Vendor-style framing explicit (ROBOTIS Dynamixel as the home-scale-component counterpart to Move #1 industrial-vendor RFCs).
- [x] Apache-2.0 license fit acknowledged.
- [x] Cross-link to RFC-0009 (mobility schema) + RFC-0011 / 0012 (profiles) + RFC-0031-0034 (Move #1 component-vendor precedents) explicit.
- [x] Documented cross-citation framing (not a stand-alone adapter) justified.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, indirect composition, multi-model protocol variation, closed-product-line caveat).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: KR`; KR US-friendly; default policy passes.
- [x] CLAUDE.md compliance check passed.
