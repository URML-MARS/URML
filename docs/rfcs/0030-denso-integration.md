---
rfc: 0030
title: Denso integration — request for comment from DENSORobot/denso_robot_ros2 maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-05-22
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

# RFC-0030: Denso integration — request for comment from DENSORobot/denso_robot_ros2 maintainers

## Summary

URML ships `DensoAdapter` compiling URML programs onto Denso (DENSO Robotics) arms via `DENSORobot/denso_robot_ros2` + MoveIt 2. This RFC documents the v0.1 primitive-to-driver mapping and **requests review and feedback from the DENSORobot GitHub maintainers**. No spec change.

## Motivation

DENSO Robotics is the robotics division of DENSO Corporation — the Toyota-affiliated tier-1 automotive supplier. Their VS series and COBOTTA collaborative-arm lines target electronics assembly, life-sciences, and automotive sub-assembly. The `DENSORobot/denso_robot_ros2` repo is **vendor-direct** with Issues open. COBOTTA in particular is a high-visibility collaborative arm with a strong educational installed base.

## Detailed design

Descriptive of existing URML artifacts. No spec text changes.

### URML v0.1 → DENSO driver primitive mapping

`DensoAdapter` composes `RclpyAdapter`. Gripper-server default: `_BRAND_GRIPPER_SERVER["denso"]` = `/denso/gripper/gripper_cmd`. Mapping shape identical to the industrial-arm pattern; the DENSO-specific routing involves the b-CAP (binary-CAP) protocol that the `denso_robot_ros2` driver uses to communicate with the RC8 / RC9 controllers.

A DENSO cell (VS-050 / VS-068 classical or COBOTTA cobot + 2-finger gripper + wrist RGB) with RFC-0013 industrial primitives is expressible today through `DensoAdapter` and ACCEPTS under the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) — Japan (JP) is allied; `denso` is not on the denylist.

### Compatibility notes

- **Controller line.** `DENSORobot/denso_robot_ros2` targets RC8 / RC8A controllers (current generation). The b-CAP protocol is the stable communication layer.
- **PacScript invocation.** DENSO's on-controller programming language is PacScript (BASIC-derived). [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed binding.
- **WINCAPS / RC+.** PC-side authoring environments; `DensoAdapter` does not depend on either.
- **COBOTTA Pro.** DENSO's collaborative arm shares the b-CAP communication layer with the classical VS series, so `DensoAdapter` covers both with no separate cobot adapter.
- **Origin.** DENSO Corporation, Kariya, Aichi, Japan; passes the US-federal default policy without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `denso_cell.yaml` + `conformance/fixtures/industrial/13_denso_cell_positive.yaml` already shipping from Track A.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **No Discussions venue** (Issues only); same fallback as FANUC / Kawasaki / Mitsubishi.
- **PacScript niche** — same general property as other vendor-specific on-controller languages.

## Alternatives considered

1. **Defer until Discussions are enabled.** Rejected: Issues sufficient.
2. **Combine with Mitsubishi / FANUC / Kawasaki into a "Japanese big-four arms" omnibus.** Rejected: per-vendor RFCs remain individually citable.

## Prior art

- `DENSORobot/denso_robot_ros2` — the upstream driver.
- DENSO's PacScript programming reference + b-CAP protocol documentation.
- ROS-Industrial Consortium per-vendor driver tracks.
- RFC-0023..0029 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending DENSORobot maintainer feedback:

1. **Discussions enablement.** Would DENSORobot consider enabling Discussions?
2. **PacScript invocation.** Should [RFC-0015](0015-control-program-invocation.md) `call_program` bind to a PacScript program launch over b-CAP?
3. **COBOTTA-specific manifest fields.** Should collaborative-mode parameters (force limits, soft-stop) be in the URML manifest?
4. **Conformance listing.** Would DENSO list `DensoAdapter` per [RFC-0014](0014-substrate-conformance.md)?

## Implementation note

RFC-0030 ships as a single RFC document PR. No code / manifest / fixture change (Track A covered both). Draft state.

## Requested feedback (from DENSORobot/denso_robot_ros2 maintainers)

1. **Correctness of the mapping description.**
2. **Discussions enablement.**
3. **PacScript invocation binding for Draft [RFC-0015](0015-control-program-invocation.md).**
4. **COBOTTA manifest extensions.**
5. **Conformance listing per [RFC-0014](0014-substrate-conformance.md).**
6. **Anything else.**

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Or open an Issue on `DENSORobot/denso_robot_ros2`. Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in vendor-direct GitHub presence + DENSO/Toyota market.
- [x] Detailed design names every affected component (none changed; Track A artifacts).
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real.
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
