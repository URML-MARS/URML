---
rfc: 0287
title: Open Roberta Lab (classroom programming environment) integration, request for comment from Open Roberta / Fraunhofer IAIS maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-31
updated: 2026-05-31
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

# RFC-0287: Open Roberta Lab (classroom programming environment) integration, request for comment from Open Roberta / Fraunhofer IAIS maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

URML already ships an educational profile (RFC-0011) and an `edu-runtime` that targets LEGO SPIKE / Mindstorms, micro:bit, and Thymio — the same classroom platforms Open Roberta Lab programs through its NEPO block language. This RFC proposes a mapping from URML v0.1 to the Open Roberta world and **requests review and feedback from the Open Roberta / Fraunhofer IAIS maintainers**. The framing is the classroom *programming-environment* layer, not a device SDK: this is deliberately distinct from the VEX (RFC-0236) and Pybricks (RFC-0235) device-toolchain threads. No spec change.

## Motivation

Open Roberta Lab ([`OpenRoberta/openroberta-lab`](https://github.com/OpenRoberta/openroberta-lab), Apache-2.0, ~143 stars, Issues enabled, active, **not archived**, verified 2026-05-31) is one of the most widely deployed open classroom robot-programming environments in Europe and beyond. It lets students program many of the same low-cost platforms URML's educational profile already targets, through the NEPO visual block language, with a clean separation between the editor and per-robot plugins.

Three things make this concrete rather than aspirational:

1. **Platform overlap is exact.** URML's `edu-runtime` already drives LEGO, micro:bit, and Thymio; Open Roberta programs those same families. The two projects describe the same hardware from different angles (URML: a validated capability manifest plus typed intent primitives; Open Roberta: NEPO blocks plus a robot plugin).
2. **Layer fit, not competition.** URML is an intent and validation layer above the substrate, and a natural-language front door. Open Roberta is a block-authoring environment. A plain-English sentence that becomes a *validated* URML program, which in turn could export to a NEPO-compatible target, is a complementary on-ramp, not a replacement editor.
3. **Shared values.** Both are Apache-2.0, both are aimed squarely at beginners and classrooms, both are vendor-neutral across platforms. The license composes cleanly.

## Detailed design

### What URML already ships for this audience

- **Educational profile (RFC-0011):** conservative defaults (gentle grip ceiling, slow speed cap, abort-and-report on error, fail-closed `detect`).
- **`reference/edu-runtime/`:** zero-ROS adapters for VEX, LEGO SPIKE, Thymio, Marty, Petoi, CircuitPython.
- **Worked classroom examples and a lesson:** `examples/educational/` (`hello-square`, `classroom-patrol`, `fetch-the-block`) plus [Tutorial 5](../tutorials/05-teaching-urml.md).
- **`microbit_edu` manifest fixture (RFC-0018):** the canonical URML pattern for a micro-class robot, the same micro:bit family Open Roberta supports.

### Proposed relationship (request for comment, not a commitment)

| URML concept | Open Roberta concept | Proposed relationship |
|---|---|---|
| Capability manifest (Layer 1) | Robot plugin capability descriptor | A mapping so a manifest can be derived from, or aligned with, an Open Roberta robot plugin's declared actuators/sensors. |
| Intent primitives (Layer 2: `move_to`, `grasp`, `detect`, ...) | NEPO motion / sensor blocks | A documented primitive↔block correspondence for the shared platforms. |
| Natural-language layer (Layer 4) | (none today) | URML's English→validated-intent front door as an optional on-ramp into a block program. |
| Educational profile safety envelope | Robot plugin limits | Align URML's conservative defaults with Open Roberta's per-robot constraints. |

### What URML v0.1 does not yet express

1. **Block-environment-as-substrate declaration.** URML's manifest cannot today declare "this deployment authors via NEPO / Open Roberta." Relevant if a URML→NEPO export path is interesting. (Spec RFC candidate, not proposed here.)
2. **Plugin-derived manifests.** Auto-deriving a URML manifest from an Open Roberta robot plugin is unspecified.

### Spec / validator / reference-runtime / conformance changes

None in this RFC. Any export path or manifest-derivation work would be a separate, additive Spec RFC after maintainer signal.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No code lands with this RFC.
- **Layer-boundary ambiguity.** "Complementary on-ramp vs overlapping editor" is exactly the question to ask the maintainers, not to assert.
- **Export-path Spec-RFC prerequisite.** A real URML→NEPO export needs a block-environment substrate declaration first.

## Alternatives considered

1. **Pitch a device SDK instead.** Rejected: the VEX and Pybricks device-toolchain threads (RFC-0236, RFC-0235) already covered that layer and both declined. Open Roberta is the environment/curriculum layer, a genuinely different audience and ask.
2. **Bundle all classroom environments (MakeCode, Snap!, Open Roberta) into one RFC.** Rejected: per-project RFCs let each maintainer group thread its own conversation.
3. **Cross-citation only.** Rejected: the platform overlap is concrete enough to warrant direct engagement.

## Prior art

- [`OpenRoberta/openroberta-lab`](https://github.com/OpenRoberta/openroberta-lab) — the NEPO authoring environment.
- [RFC-0011 (educational profile)](0011-educational-profile.md), [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md).
- Sibling environment RFCs: [RFC-0288 (Microsoft MakeCode)](0288-makecode-outreach.md), [RFC-0289 (Snap!)](0289-snap-outreach.md).
- Device-toolchain prior threads (different layer): [RFC-0235 (Pybricks)](0235-pybricks-outreach.md), [RFC-0236 (PROS/VEX)](0236-pros-vex-outreach.md).

## Unresolved questions

For the Open Roberta / Fraunhofer IAIS maintainers:

1. **Layer fit.** Is a plain-language, validated-intent front door that could export to a NEPO-compatible target interesting, or does it overlap your roadmap?
2. **Capability descriptor.** Could a URML manifest be aligned with, or derived from, an Open Roberta robot plugin's capability descriptor? What is the most useful grain?
3. **Shared platforms.** Are LEGO / micro:bit / Thymio the right first platforms to align on, or others?
4. **Adapter home.** If a bridge ships, should it live in URML's `reference/edu-runtime/` or be Open-Roberta-side?
5. **Anything else.**

## Implementation note

RFC-0287 ships as a single RFC document. Ledger entry in [`examples/lighthouses/outreach-move19.yaml`](../../examples/lighthouses/outreach-move19.yaml).

## How to respond

`OpenRoberta/openroberta-lab` has Issues enabled (Discussions are not). URML's planned channel: a single Issue pointing to this RFC, framed as a request for comment, with the platform-overlap point and the `edu-runtime` / educational-profile links explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-31 (Apache-2.0, ~143 stars, Issues enabled, active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, layer-boundary ambiguity, export-path Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Fraunhofer IAIS, Germany; default policy passes (NATO/EU ally).
- [x] CLAUDE.md compliance check passed (educational scope; no commercial surface).
