---
rfc: 0028
title: FANUC integration — request for comment from FANUC-CORPORATION/fanuc_driver maintainers
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

# RFC-0028: FANUC integration — request for comment from FANUC-CORPORATION/fanuc_driver maintainers

## Summary

URML ships `FanucAdapter` compiling URML programs onto FANUC arms via the FANUC ROS-Industrial driver (`FANUC-CORPORATION/fanuc_driver` — the vendor-direct repo). This RFC documents the v0.1 primitive-to-driver mapping and **requests review and feedback from the FANUC-CORPORATION GitHub maintainers**. No spec change.

## Motivation

FANUC is one of the "big four" industrial-arm vendors globally and a founding member of the ROS-Industrial Consortium. The `FANUC-CORPORATION/fanuc_driver` repo is **vendor-direct** (not community-only) — Issues are open, though Discussions are not currently enabled. The R-30iA / R-30iB / R-30iB Plus controller lineage powers FANUC's enormous automotive-assembly installed base, plus the CRX collaborative-arm line. URML had a `FanucAdapter` from Track A but no brand-named manifest fixture (one of the "original six" gaps — UR / Yaskawa / KUKA / FANUC / ABB / Franka all rode the generic `industrial_cell.yaml` before this RFC).

## Detailed design

Descriptive of existing URML artifacts plus the new brand-named manifest + fixture this PR adds. No spec text changes.

### URML v0.1 → FANUC driver primitive mapping

`FanucAdapter` composes `RclpyAdapter`. Gripper-server default: `_BRAND_GRIPPER_SERVER["fanuc"]` = `/fanuc/gripper/gripper_cmd`. Mapping shape identical to the industrial-arm pattern (see RFC-0023 / 0025 / 0026 / 0027): `move_to` / `grasp` / `release` / `measure` / `wait_for` / `wait` / `report` → Protocol methods; `dock` / `detect` / `scan` / `capture` / `speak` / `listen` → `not_supported_on_industrial_arm[fanuc]` sentinels; RFC-0013 industrial primitives compose Layer-3 sequences.

The FANUC-specific routing: MoveIt 2 plans a trajectory; the `fanuc_driver` translates `control_msgs/FollowJointTrajectory` to the R-30iA / R-30iB / R-30iB Plus controller (typically via FANUC's Ethernet/IP option or PNS / Stream Motion); the controller's TP (Teach Pendant) program or KAREL program executes the motion. Gripper commands route to `/fanuc/gripper/gripper_cmd`.

A FANUC cell (M-10iD / LR Mate 200iD / CRX-10iA cobot with a 2-finger or vacuum gripper + wrist RGB) with RFC-0013 industrial primitives is expressible today through `FanucAdapter` and ACCEPTS under the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) — Japan (JP) is allied; `fanuc` is not on the denylist.

### Compatibility notes

- **Controller line.** `FANUC-CORPORATION/fanuc_driver` targets the R-30iA / R-30iB / R-30iB Plus controllers. Legacy R-J3iC controllers may not be covered.
- **CRX cobot subfamily.** FANUC's CRX collaborative arms (CRX-5iA / 10iA / 25iA) share controller architecture with the classical line and use the same driver path; `FanucAdapter` covers both.
- **TP / KAREL invocation.** FANUC's on-controller programming languages are TP (Teach Pendant, a structured tablet UI) and KAREL (Pascal-derived script). [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed binding for both.
- **PNS / Stream Motion.** FANUC's two real-time control protocols — PNS (Program Number Select) for discrete program launches and Stream Motion for continuous trajectory streaming — map to different URML semantics: PNS is closer to `call_program` (Draft RFC-0015), Stream Motion is closer to `FollowJointTrajectory` direct dispatch.
- **Origin.** FANUC CORPORATION, Yamanashi, Japan; passes the US-federal default policy without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Manifest fixture (NEW): `reference/validator/tests/fixtures/manifests/fanuc_cell.yaml` — brand-named manifest closing the original-six gap.
- Conformance fixture (NEW): `conformance/fixtures/industrial/<NN>_fanuc_cell_positive.yaml` exercising the RFC-0013 pick_from/place_at happy path.
- `MANIFEST_REGISTRY` entry (NEW): `fanuc_cell`.

## Backward compatibility

Pre-v1.0; purely additive.

## Drawbacks

- **No Discussions venue.** `FANUC-CORPORATION/fanuc_driver` has Issues but not Discussions enabled, which makes the "post an RFC link as a Discussion" pattern unavailable. The fallback is to open an Issue with the RFC link — a higher-friction venue, but still public and trackable.
- **TP / KAREL niche.** Same general property as VAL 3 / KRL / MELFA-BASIC V — vendor-specific on-controller languages are not portable; `call_program` (Draft RFC-0015) is the binding-layer answer.

## Alternatives considered

1. **Defer FANUC until Discussions are enabled.** Rejected: the artifact is the product (per Phase-0 posture); Issues-only is enough for the warm-touch hook.
2. **Skip the brand-named manifest** (since FANUC didn't have one before). Rejected: the original-six symmetry gap should close here while we're touching the area.
3. **Combine with Yaskawa / KUKA into a "ROS-Industrial big-three Asian arm" omnibus RFC.** Rejected for the same reason as RFC-0025/0026/0027.

## Prior art

- `FANUC-CORPORATION/fanuc_driver` — the upstream driver.
- FANUC's KAREL programming reference and TP teach-pendant docs.
- ROS-Industrial Consortium per-vendor driver tracks.
- RFC-0023 / 0024 / 0025 / 0026 / 0027 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending FANUC-CORPORATION/fanuc_driver maintainer feedback:

1. **Discussions enablement.** Would FANUC-CORPORATION consider enabling Discussions on the driver repo to make community engagement (including URML's) lower friction?
2. **TP vs KAREL binding.** Should [RFC-0015](0015-control-program-invocation.md) `call_program` bind to a TP program launch, a KAREL routine, or both via a parameterized handle?
3. **PNS vs Stream Motion.** Which path should URML's adapter prefer for continuous motion commands?
4. **CRX cobot.** Are there CRX-specific manifest fields URML should support (collaborative force limits, soft-stop parameters)?
5. **Conformance listing.** Would FANUC CORPORATION list `FanucAdapter` per [RFC-0014](0014-substrate-conformance.md)?

## Implementation note

RFC-0028 ships as a single PR with the RFC + new `fanuc_cell.yaml` manifest + new conformance fixture + `MANIFEST_REGISTRY` entry. Hermetic conformance suite + validator suite must remain green. Draft state.

## Requested feedback (from FANUC-CORPORATION maintainers)

1. **Correctness of the mapping description.**
2. **Discussions enablement.**
3. **TP / KAREL binding for Draft [RFC-0015](0015-control-program-invocation.md).**
4. **PNS vs Stream Motion preference.**
5. **CRX-specific manifest fields.**
6. **Conformance listing interest per [RFC-0014](0014-substrate-conformance.md).**
7. **Anything else.**

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Or open an Issue on `FANUC-CORPORATION/fanuc_driver` linking back. Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in vendor-direct GitHub presence + big-four industrial-arm scope.
- [x] Detailed design names every affected component (existing `FanucAdapter` referenced; new manifest + fixture introduced).
- [x] At least one alternative considered (three are).
- [x] Drawbacks are real (no Discussions; TP/KAREL niche).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
