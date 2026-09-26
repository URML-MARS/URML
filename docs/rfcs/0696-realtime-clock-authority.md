---
rfc: 0696
title: Real-time clock authority and per-controller rate (RFC-0016 refinement)
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-04
updated: 2026-09-04
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

# RFC-0696: Real-time clock authority and per-controller rate (RFC-0016 refinement)

## Summary

[RFC-0016](0016-realtime-cyclic-manifest-block.md) added the `realtime` block (`cyclic_period_ms`, `watchdog_ms`, `requested_packet_interval_ms`, `guarantee`). A Universal Robots maintainer (`urrsk`) reviewing the URML-to-UR mapping ([Universal_Robots_ROS2_Driver discussion #1799](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver/discussions/1799)) raised two things the block cannot currently say. First, a single `cyclic_period_ms` is wrong for part of an installed base: UR evaluates script at 500 Hz on e-Series / PolyScope X but 125 Hz on CB3, so a manifest that hardcodes one rate is already incorrect for the other controller. Second, and more important, the block does not say **which clock is authoritative**: "the external computer runs its own loop at N Hz" and "the external computer is slaved to the robot clock, blocking on the controller's cyclic data" are different claims, and only the second is a pattern a vendor would endorse in general. This RFC refines RFC-0016 by adding an optional `clock_authority` field and clarifying that `cyclic_period_ms` is a per-controller value, not a portable constant. It is a **Draft for maintainer decision**; no schema or validator change lands until it advances.

## Motivation

On the external side of a UR deployment, the recommended pattern is to let the external computer follow the robot clock: block on incoming RTDE data, which is paced by the controller, and send in response. That removes jitter between the robot and the external computer without the external machine having to be real-time in its own right. "The external computer runs at N Hz" is a different and stronger claim, and not one to encode as the general shape.

RFC-0016's `realtime` block cannot distinguish these. A manifest declaring `cyclic_period_ms: 2` (500 Hz) reads identically whether the external computer is self-clocked at 500 Hz or slaved to a 500 Hz controller, yet those are materially different systems with different jitter and failure behavior. And the same manifest is simply wrong on a CB3 (125 Hz). The block should carry which clock is authoritative, and should make explicit that the rate belongs to the specific controller.

This is the same class of gap RFC-0016 itself addressed: a manifest that is not a faithful description of the hardware. It is a capability-declaration refinement, not a behavior change, so it is a manifest-schema RFC and adds no primitive.

## Detailed design

Additive and optional; absent fields reproduce RFC-0016 exactly.

### 1. `clock_authority` on the `realtime` block

```
realtime:
  cyclic_period_ms: 2
  watchdog_ms: 8
  guarantee: soft
  clock_authority: robot_clock | external   # optional; no default (unspecified)
```

- **`robot_clock`** declares that the external computer is slaved to the controller clock: it blocks on the controller's cyclic data and sends in response, so the controller is the pacing authority. This is the endorsed general pattern.
- **`external`** declares that the external computer runs its own loop at `cyclic_period_ms` and is itself the pacing authority. This is a stronger claim about the external machine's real-time behavior and should be used only when that is truly the design.
- **absent** is "unspecified" (today's behavior, unchanged).

The value is recorded in the audit so a reader can see which system was declared. URML does not enforce timing (RFC-0016's honesty stance is unchanged); `clock_authority` makes the *claim* explicit rather than leaving it ambiguous.

### 2. `cyclic_period_ms` is per-controller, not portable

A spec-level clarification: `cyclic_period_ms` (and `watchdog_ms`) describe the **specific controller of the deployment** the manifest represents, and must match it. They are not a value to hardcode into a shared, controller-generation-spanning template. A robot family with different per-controller rates (UR: 500 Hz e-Series / PolyScope X, 125 Hz CB3) needs a manifest per controller generation, or a manifest generated for the controller in hand, not a single baked-in number. No schema change is required for this; it is a documented constraint plus example guidance. (An optional free-text `controller` label on `realtime`, e.g. `"UR e-Series"`, is offered as a way to make the mismatch visible, but it is not load-bearing.)

### 3. Optional coherence signal

An optional, non-blocking validator signal: if `clock_authority: external` is combined with `guarantee: hard`, surface an advisory in the audit (a self-clocked external machine claiming hard real-time is a strong claim worth flagging, not rejecting). This stays advisory to preserve RFC-0016's "describe, do not enforce" posture.

### Spec changes

- **Layer 1**: the `Realtime` model gains optional `clock_authority` (enum) and an optional `controller` label. Additive; defaults reproduce RFC-0016. A spec note records the per-controller-rate constraint.
- **Layer 2/3/4**: none. No primitive branches on this.
- **Validator**: record `clock_authority` / `controller` in the audit; optional advisory for `external` + `hard`. The existing `watchdog_ms >= cyclic_period_ms` coherence check is unchanged.

### Reference runtime changes

None required. A runtime MAY read `clock_authority` to choose its loop structure (a UR adapter would use `robot_clock` to block on RTDE input rather than run a self-timed loop), but is not obligated to in v0.1.

## Backward compatibility

Fully compatible. Both new fields are optional; absent, the block behaves exactly as RFC-0016. Every existing `realtime` manifest is unchanged. Pre-v1.0.

## Drawbacks

- It adds two fields to a block RFC-0016 deliberately kept to four, risking the real-time scope creep RFC-0016 warned about. Mitigation: `clock_authority` is a declaration, not an enforcement, and the per-controller clarification is mostly documentation, not schema.
- `clock_authority` still is not enforced (URML cannot measure the loop), so the documented-vs-enforced hazard remains; the audit record and the `guarantee` field are the honesty knobs.

## Alternatives considered

1. **Leave `realtime` as-is.** Rejected: it cannot distinguish self-clocked from controller-slaved systems and silently mis-describes multi-controller families, which a maintainer surfaced directly.
2. **Infer clock authority from the runtime rather than declare it.** Rejected: the manifest is meant to be a faithful, runtime-independent description; inference hides the claim in code, the opposite of RFC-0016's intent.
3. **Model rate as a per-controller list inside one manifest.** Deferred as heavier than needed: a manifest is per-deployment, so one controller's rate per manifest is the simpler faithful representation; the optional `controller` label plus guidance covers the family case.

## Prior art

RFC-0016 (the block this refines) and RFC-0006 (declare-the-contract staging it follows). The Universal Robots maintainer review on discussion #1799 (`urrsk`) is the direct motivator; the block-on-RTDE-data pattern is the concrete recommendation. Companion to [RFC-0691](0691-control-handover-semantics.md), the other refinement from the same review.

## Unresolved questions

- **Vocabulary.** `robot_clock` / `external` are the two clock-authority values that cover the UR case; whether a third (for example a shared external time source such as PTP/TSN) is worth adding is deferred until a substrate needs it.
- **Whether the `controller` label should be structured** (vendor + generation) rather than free text. Proposed free text for now.

## Implementation note

This RFC is a **Draft**. No schema, validator, or runtime change lands until it advances. On advance it lands additively in the `0.1.x` line like RFC-0016 itself: the optional `clock_authority` and `controller` fields, the audit record, the optional `external` + `hard` advisory, and a spec note plus example guidance on the per-controller-rate constraint. RFC-0024 (the URML-to-UR mapping) is updated to use `clock_authority: robot_clock` in its example once this is accepted.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed and why now.
- [x] The Motivation is grounded in a concrete, named maintainer review, not a hypothetical.
- [x] The Detailed design names the affected spec layer and the (optional) runtime use; adds no primitive, so the substrate-neutrality acid test is N/A.
- [x] At least one alternative is genuinely considered (three are).
- [x] Drawbacks are real: it grows a block kept deliberately small, and it is a declaration not an enforcement.
- [x] Backward compatibility is honest: additive, defaults reproduce RFC-0016.
- [x] The implementation note explains this is a Draft and what lands on advance.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed compliance (no substrate coupling: clock authority is defined substrate-neutrally, UR being the motivating instance).
