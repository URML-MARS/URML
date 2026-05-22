---
rfc: 0025
title: KUKA integration — request for comment from kroshu/kuka_drivers maintainers
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

# RFC-0025: KUKA integration — request for comment from kroshu/kuka_drivers maintainers

## Summary

URML ships `KukaAdapter` (`reference/industrial-arm-runtime/.../adapter.py`) that compiles URML programs onto KUKA arms via the KUKA ROS 2 driver maintained by `kroshu/kuka_drivers` (EKI / RSI / `kuka_external_control_sdk` over `ros2_control` + MoveIt 2). This RFC documents the v0.1 primitive-to-driver mapping, surfaces what the KUKA controller exposes that URML v0.1 cannot yet express, and **requests review and feedback from the `kroshu/kuka_drivers` maintainers** on the mapping's correctness. No spec change.

## Motivation

KUKA is a founding member of the ROS-Industrial Consortium and one of the "big four" industrial-arm vendors. The `kroshu/kuka_drivers` track is the most actively-maintained public ROS 2 driver path for KUKA arms — KUKA-DE-aligned, Discussions enabled, EKI/RSI-based for the KR C4/C5 controller line and `kuka_external_control_sdk` for newer ECI / iiQKA controllers. The case for filing is the same as RFC-0023: correctness review by the actual driver maintainers + an invitation to conformance-listing per [RFC-0014](0014-substrate-conformance.md).

## Detailed design

Descriptive of existing URML artifacts plus a feedback ask. No spec text changes.

### URML v0.1 → KUKA driver primitive mapping

`KukaAdapter` composes `RclpyAdapter` with brand-default config: `move_group=/move_action`, gripper=`_BRAND_GRIPPER_SERVER["kuka"]` = `/kuka/gripper/gripper_cmd`. Brand class is a thin specialization; substrate plumbing is single-sourced through `RclpyAdapter`.

| URML v0.1 primitive | Adapter method | KUKA-side realisation | Notes |
|---|---|---|---|
| `move_to` / `hover` | `send_navigation_goal(location=..., pose=..., frame=...)` | MoveIt 2 plan + `control_msgs/FollowJointTrajectory` over `ros2_control` (EKI / RSI for C4/C5; `kuka_external_control_sdk` for iiQKA / Sunrise) | Named-pose semantics; planner = MoveIt 2. |
| `grasp` / `release` | `send_manipulation_goal(action=..., force_n=...)` | `control_msgs/GripperCommand` on `/kuka/gripper/gripper_cmd` | Scalar `force_n` honoured at v0.1 fidelity; parametric impedance is a SPEC-GAPS item. |
| `measure` | `take_measurement(what=..., target=..., sensor=...)` | One-shot read from `/joint_states` / `/wrench` (FT-enabled wrist) / a sensor topic declared in the manifest | |
| `wait_for` (event / threshold / signal) | `wait_for_condition(...)` | Block on a ROS topic / latched event / signal declared in `declared_events` | |
| `wait` (passive dwell) | `wait_passively(duration_seconds=...)` | Host-side sleep | |
| `report` (structured status upstream) | `emit_report(...)` | Publish on a configured `outputs.named_endpoints` topic (typically a PLC ingest) | |
| `dock` | `send_docking_goal(...)` | Returns `not_supported_on_industrial_arm[kuka]: …no docking station` for a bare arm | Companion-adapter pattern; RFC-0013 `swap_tool` rides this when a tool-change station is declared. |
| `detect`, `scan`, `capture`, `speak`, `listen` | corresponding adapter methods | All return the `not_supported_on_industrial_arm[kuka]` sentinel | Industrial profile uses companion adapters for vision; speech is out of profile. |
| `take_off` / `land` / `return_to_home` | drone-profile methods | All return `not_supported_on_industrial_arm[kuka]: …no flight capability` | Out of profile. |
| `pick_from` / `place_at` / `swap_tool` (RFC-0013) | composed Layer-3 sequences | Same FollowJointTrajectory + GripperCommand pair; `swap_tool` rides `send_docking_goal` when `docking_stations[].services` declares it | No new Protocol method per RFC-0013. |

A bare KUKA cell (KR 6/16/210 + 2-finger gripper + wrist RGB camera) with RFC-0013 industrial primitives is expressible today through `KukaAdapter` and ACCEPTS under the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) — Germany (DE) is allied; `kuka` is not on the denylist.

### Substrate-neutrality

Conformance fixture `conformance/fixtures/industrial/43_kuka_cell_positive.yaml` (added in this PR) passes against `MockROSAdapter` hermetically; `KukaAdapter` exercises the same fixture in the gated `industrial-arm-integration.yml` lane with a sourced ROS 2 environment and `kuka_drivers` installed.

### Compatibility notes

- **Controller line.** `kroshu/kuka_drivers` covers KR C4 (EKI / RSI), KR C5, and the newer iiQKA controllers (`kuka_external_control_sdk`). URML's `KukaAdapter` is controller-agnostic at the URML layer — the controller-specific driver selection lives in `AdapterConfig`.
- **MoveIt 2 dependency.** Recommended (and assumed by `_BRAND_GRIPPER_SERVER["kuka"]` defaults); MoveIt-free trajectory generation (e.g. direct EKI/RSI command streaming) is a deployment choice the adapter does not constrain.
- **KRL invocation.** KUKA Robot Language (KRL) is the on-controller scripting language analog of UR's URScript / Yaskawa's INFORM. [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed binding layer — see Open Questions.
- **Origin.** KUKA Aktiengesellschaft, Augsburg, Germany; passes the US-federal default policy ([RFC-0003](0003-us-alignment.md) / [0004](0004-compliance-policy.md)) without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec: none.
- Validator: none.
- Reference runtime: none. `KukaAdapter` already shipping (Track A).
- Conformance suite: one new positive fixture (`43_kuka_cell_positive.yaml`) + one `MANIFEST_REGISTRY` entry (`kuka_cell`). The KUKA brand-named manifest `kuka_cell.yaml` is added for symmetry with Track-A/I-A brand fixtures (KUKA was a gap before this RFC).

## Backward compatibility

Pre-v1.0; purely additive.

## Drawbacks

- **Driver-track maintainer is community, not vendor-direct.** `kroshu` is community-maintained with strong KUKA alignment, but is not KUKA Aktiengesellschaft itself. Outreach via the kroshu repo is the most active venue; outreach to KUKA AG DevRel directly is a parallel slow-build channel (covered by [RFC-0038 ROS-Industrial Consortium](#) which institutionally covers KUKA via the consortium).
- **KR C4 vs iiQKA driver divergence.** The two controller lines have distinct ROS 2 driver shapes; URML papers over the difference through `AdapterConfig`. If the divergence widens, a single `KukaAdapter` class may need to split — documented here for honesty, deferred for now.

## Alternatives considered

1. **Two RFCs (KR C4 + iiQKA).** Rejected: from URML's perspective the mapping is identical — `AdapterConfig` is the deployment-layer dial. Splitting would dilute the per-vendor feedback ask.
2. **Defer until KUKA-AG-direct DevRel relationship.** Rejected: kroshu is the active venue; a public RFC there reaches the actual driver community today.
3. **Skip the brand-named `kuka_cell.yaml` manifest.** Rejected: every Track-A/I-A brand has one; KUKA was a v0.1-era symmetry gap.

## Prior art

- `kroshu/kuka_drivers` (the umbrella repo), `kroshu/kuka_external_control_sdk`, `kroshu/kuka_kss_drivers`.
- KUKA Aktiengesellschaft's developer materials (KUKA.PLC mxAutomation, KUKA.OfficeLite, KUKA Sim).
- ROS-Industrial Consortium per-vendor driver tracks.
- RFC-0023 (Yaskawa) and RFC-0024 (UR) for the per-vendor RFC pattern.
- [RFC-0014](0014-substrate-conformance.md) for the substrate-neutral runtime contract.

## Unresolved questions

Provisional pending kroshu/kuka_drivers maintainer feedback:

1. **Driver-track scope.** Is `kroshu/kuka_drivers` the right canonical entry-point repo URML should reference, or should the per-controller repos (`kuka_external_control_sdk`, `kuka_kss_drivers`) be referenced individually?
2. **KRL invocation.** Should URML's [RFC-0015](0015-control-program-invocation.md) `call_program` bind to KRL invocation through EKI / RSI / `kuka_external_control_sdk`? Through which path is the most stable?
3. **Realtime / cyclic execution.** Does [RFC-0016](0016-realtime-cyclic-manifest-block.md) (real-time / cyclic manifest block) match the KR C4 / iiQKA execution model in a way kroshu would endorse?
4. **Digital I/O.** [RFC-0017](0017-digital-io-actuation.md) (`set_output`) covers raw digital-I/O tool actuation, which is heavily used on KUKA cells (mxAutomation IO blocks, EKI digital outputs). Does the proposed binding fit?
5. **Conformance listing.** Would kroshu/kuka_drivers — and through them, KUKA Aktiengesellschaft — consider listing `KukaAdapter` in the URML compatible-runtimes registry per [RFC-0014](0014-substrate-conformance.md)?

## Implementation note

RFC-0025 ships as a single PR alongside the new `kuka_cell.yaml` manifest + `conformance/fixtures/industrial/43_kuka_cell_positive.yaml`. Hermetic conformance suite + validator suite must remain green. Draft state; promotion to Open is Founder-action when the Phase-0 launch gate un-halts.

No code change in `KukaAdapter`. No new dependency. No new Protocol method.

## Requested feedback (from kroshu/kuka_drivers maintainers)

If you maintain `kroshu/kuka_drivers` (or contribute to `kuka_external_control_sdk` / `kuka_kss_drivers` / the broader KUKA ROS-Industrial track), URML is asking you for:

1. **Correctness of the mapping table.** Any misrepresentation of the EKI / RSI / external-control-SDK action surface or the MoveIt 2 integration shape — please correct.
2. **Canonical-repo guidance.** Which kroshu repo (or KUKA AG-direct repo, if one is planned) should URML reference as the upstream pointer?
3. **KRL invocation.** Binding for Draft [RFC-0015](0015-control-program-invocation.md), and through which path?
4. **Digital I/O.** Binding for Draft [RFC-0017](0017-digital-io-actuation.md) on EKI digital outputs / mxAutomation IO blocks?
5. **Conformance interest.** Would kroshu — and by extension KUKA AG — list `KukaAdapter` in the URML compatible-runtimes registry?
6. **Anything else.** Corrections and "you got that wrong" are explicitly invited.

## How to respond

Open a thread in the URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Categories that fit best: **Q&A**, **Ideas**, **Builders & Makers**. Substantive spec changes follow a follow-on RFC per [RFC-0001](0001-rfc-process.md).

For private channel before public discussion: contact via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in concrete vendor relationship (kroshu/kuka_drivers + KUKA AG).
- [x] Detailed design names every affected component (none changed).
- [x] At least one genuine alternative considered (three are).
- [x] Drawbacks are real (kroshu-vs-KUKA-direct + driver-line divergence).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added; dual-substrate sketch not required.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No partnership surface; no Apache-2.0 commitment changes; no single-substrate coupling.
