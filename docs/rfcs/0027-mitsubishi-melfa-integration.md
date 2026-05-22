---
rfc: 0027
title: Mitsubishi MELFA integration — request for comment from Mitsubishi-Electric-Asia/melfa_ros2_driver maintainers
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

# RFC-0027: Mitsubishi MELFA integration — request for comment from Mitsubishi-Electric-Asia/melfa_ros2_driver maintainers

## Summary

URML ships `MitsubishiAdapter` (`reference/industrial-arm-runtime/.../adapter.py`) compiling URML programs onto Mitsubishi Electric MELFA arms via `Mitsubishi-Electric-Asia/melfa_ros2_driver` + MoveIt 2. This RFC documents the v0.1 primitive-to-driver mapping and **requests review and feedback from the Mitsubishi-Electric-Asia maintainers**. No spec change.

## Motivation

Mitsubishi Electric is a top-tier industrial-arm vendor in Asia with strong factory-automation / electronics-assembly market share. The `Mitsubishi-Electric-Asia/melfa_ros2_driver` is a **vendor-direct GitHub repo** (not community-only) with Discussions enabled — exactly the kind of high-credibility public engagement venue URML's Move #1 program targets. The MELFA SQ/RV/F-series + the newer FR-series controllers (CR800, CR860) constitute one of the most-deployed Asian industrial arm lines outside the FANUC/Yaskawa duopoly.

## Detailed design

Descriptive of existing URML artifacts. No spec text changes.

### URML v0.1 → MELFA driver primitive mapping

`MitsubishiAdapter` composes `RclpyAdapter`. Gripper-server default: `_BRAND_GRIPPER_SERVER["mitsubishi"]` = `/melfa/gripper/gripper_cmd`. Vendor token in provenance is `mitsubishi_electric` to disambiguate from any other Mitsubishi-prefixed entity. Brand class is the standard thin specialization on `IndustrialArmAdapter`.

Mapping shape identical to the industrial-arm pattern (RFC-0023 Yaskawa / 0025 KUKA / 0026 Stäubli): `move_to` / `grasp` / `release` / `measure` / `wait_for` / `wait` / `report` → Protocol methods; `dock` / `detect` / `scan` / `capture` / `speak` / `listen` → `not_supported_on_industrial_arm[mitsubishi]` sentinels with the companion-adapter pattern; RFC-0013 industrial primitives compose Layer-3 sequences.

The MELFA-specific routing: MoveIt 2 plans a trajectory; the `melfa_ros2_driver` translates `control_msgs/FollowJointTrajectory` to the CR800 / CR860 controller; the controller's MELFA-BASIC V application executes the motion. Gripper commands route to `/melfa/gripper/gripper_cmd`.

A MELFA cell (RV-2FR / RV-7FRL / FR-series with a 2-finger gripper + wrist RGB) with RFC-0013 industrial primitives is expressible today through `MitsubishiAdapter` and ACCEPTS under the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) — Japan (JP) is allied; `mitsubishi_electric` is not on the denylist.

### Compatibility notes

- **Controller line.** `Mitsubishi-Electric-Asia/melfa_ros2_driver` targets the CR800 / CR860 controllers (current FR/F generations). Legacy CR1 / CR2 controllers may not be covered.
- **MELFA-BASIC V invocation.** Mitsubishi's on-controller programming language is MELFA-BASIC V (BASIC-derived; analog of KUKA's KRL, Yaskawa's INFORM, Stäubli's VAL 3). [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed binding.
- **RT Toolbox.** Mitsubishi's PC-side development environment (RT Toolbox3 / RT VisualBox) is the typical authoring path for MELFA-BASIC V; URML's `MitsubishiAdapter` does not depend on RT Toolbox — only the runtime driver path is required.
- **Origin.** Mitsubishi Electric Corporation, Tokyo, Japan; passes the US-federal default policy without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `mitsubishi_cell.yaml` + `conformance/fixtures/industrial/12_mitsubishi_cell_positive.yaml` already shipping from Track A.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **MELFA-BASIC V is unfamiliar outside the Mitsubishi base.** Same general property as VAL 3 / KRL / INFORM — vendor-specific on-controller languages are not portable across the big-five industrial-arm vendors; `call_program` (Draft RFC-0015) is the binding-layer answer, not URML adopting any one vendor's language.
- **`Mitsubishi-Electric-Asia/` org scope.** The Asia regional sub-organization may not represent global Mitsubishi Electric DevRel; a parallel slow-build channel to the Tokyo HQ is the institutional path (covered by upcoming RFC-0038 ROS-I Consortium).

## Alternatives considered

1. **Wait for a global Mitsubishi-Electric ROS 2 org.** Rejected: `Mitsubishi-Electric-Asia/melfa_ros2_driver` is active and Discussions-enabled today; a future global org would be a follow-on RFC.
2. **Combine with FANUC / Yaskawa / KUKA into a "big-four industrial arms" omnibus RFC.** Rejected: per-vendor RFCs remain individually citable; the omnibus posture would dilute each vendor's feedback ask.

## Prior art

- `Mitsubishi-Electric-Asia/melfa_ros2_driver` — the upstream driver.
- Mitsubishi Electric's MELFA-BASIC V programming reference.
- ROS-Industrial Consortium per-vendor driver tracks.
- RFC-0023 / 0024 / 0025 / 0026 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending Mitsubishi-Electric-Asia/melfa_ros2_driver maintainer feedback:

1. **Global vs Asia-regional scope.** Should the URML adapter docstring reference `Mitsubishi-Electric-Asia/` (current) or anticipate a global org migration?
2. **MELFA-BASIC V invocation.** Should [RFC-0015](0015-control-program-invocation.md) `call_program` bind to a MELFA-BASIC V program launch (via the `melfa_ros2_driver` or a separate path)?
3. **CR1 / CR2 legacy.** Is there community interest in adding legacy-controller support to the driver?
4. **Conformance listing.** Would the Mitsubishi-Electric-Asia maintainers (and through them, Mitsubishi Electric Corporation) consider listing `MitsubishiAdapter` per [RFC-0014](0014-substrate-conformance.md)?

## Implementation note

RFC-0027 ships as a single RFC document PR. No code / manifest / fixture change (all shipping from Track A). Draft state; promotion to Open is Founder-action when the launch gate un-halts.

## Requested feedback (from Mitsubishi-Electric-Asia maintainers)

Asking you for:

1. **Correctness of the mapping description.** Anywhere the description misrepresents the MELFA driver shape, the CR800/CR860 controller behaviour, or the MoveIt 2 integration — please correct.
2. **Global scope.** Is `Mitsubishi-Electric-Asia/` the canonical org to reference?
3. **MELFA-BASIC V binding.** Draft [RFC-0015](0015-control-program-invocation.md), and through which path?
4. **CR1 / CR2 support.** Is there interest in legacy-controller support?
5. **Conformance interest.** Would Mitsubishi Electric list `MitsubishiAdapter` per [RFC-0014](0014-substrate-conformance.md)?
6. **Anything else.** Corrections welcome.

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Categories: **Q&A**, **Ideas**, **Builders & Makers**. Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in a vendor-direct GitHub presence + concrete market segment.
- [x] Detailed design names every affected component (none changed; Track A artifacts referenced).
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real (MELFA-BASIC V niche; Asia-regional vs global scope).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
