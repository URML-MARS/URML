---
rfc: 0684
title: Aerial-delivery extension for the drone profile
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-29
updated: 2026-08-29
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

# RFC-0684: Aerial-delivery extension for the drone profile

## Summary

A drone that carries a parcel and lets it go is the most common aerial task after taking pictures, and URML cannot say it cleanly today. The drone profile keeps `manipulation` off aerial manifests, so `release` is unavailable, and the shipped parcel-delivery example ([`examples/drone/parcel-delivery.urml.yaml`](../../examples/drone/parcel-delivery.urml.yaml)) rides RFC-0017 `set_output` against `outputs.lines` instead. That works and validates, but it says "drive a line" where the operator means "let the parcel go". This RFC proposes the smallest additive change that lets the drone profile express delivery as intent: two new `release` modes, a payload-mechanism declaration that is not `manipulation`, a drop-height ceiling in the envelope, payload mass on `carrying`, and spatial targets for the primitives the geofence pass currently ignores. No new primitive.

## Problem statement

1. **The verb is wrong.** `set_output(output: winch, value: true)` is what the hardware does, not what the operator intends. The natural-language layer has to teach an LLM that "release the parcel" means a boolean line write, which is the kind of substrate leak URML exists to prevent.
2. **The mechanism is undeclared as such.** `outputs.lines` says "digital line"; it does not say "this line lowers a payload 15 m on a tether". The validator cannot check that a release happens at a sane height, that the aircraft is over the declared drop point, or that the payload is within `max_payload`.
3. **Timing is hand-written.** ArduPilot acknowledges a winch command on acceptance, not on completion. The example brackets the winch with `hover` pauses sized by hand from `deliver_length_m / rate_m_s`. The program and the adapter config must agree and nothing checks that they do.
4. **The geofence pass has a blind spot.** `_spatial_targets` in the validator emits targets only for `move_to` and `scan`. `set_output`, `hover` without `over`, `release(at:)`, and `land(at:)` contribute nothing, so a drop point outside the fence is caught only through the preceding `move_to`.
5. **`max_payload` is never checked against a carried object.** The `carrying` binding has no mass field; the ceiling is consulted only for learned-policy training ranges and as a runtime monitor signal.

## Proposal

### Manifest: `payload_mechanisms`

A new optional top-level block on drone-profile manifests, deliberately not `manipulation`:

```yaml
payload_mechanisms:
  - name: winch
    kind: winch
    max_line_m: 20.0
    rate_m_s: 0.5
    max_payload_kg: 1.5
  - name: latch
    kind: latch          # servo-driven hook or gripper-style latch
    max_payload_kg: 1.5
```

`kind` is `winch | latch | parachute`. A drone-profile manifest may declare `payload_mechanisms`; it still may not declare `manipulation`.

### Primitive: `release` on the drone profile

`release` gains two modes usable only when `payload_mechanisms` is declared:

```yaml
- release:
    mode: winch          # lower on the tether, open the latch, retract
    mechanism: winch
    latch: latch         # optional; the latch that opens at the bottom
    height: 0.5          # metres above ground the payload is set down
- release:
    mode: latch          # open the latch where the aircraft is
    mechanism: latch
```

`mode: drop | place | hand_to_user` keep their current meaning and remain unavailable on the drone profile. The executor lowers `mode: winch` to the substrate's winch-deliver, latch-open, winch-retract sequence and owns the wait, using the mechanism's declared `max_line_m` and `rate_m_s`. The program no longer hand-times it.

### `carrying` gains a mass

`move_to.carrying` may be an inline object declaration as well as a `$ref`:

```yaml
- move_to:
    location: dropoff
    carrying: { name: parcel, mass_kg: 0.8 }
```

Pass 2 rejects `mass_kg` above the strictest of `mobility.max_payload`, `envelope.max_payload`, and the mechanism's `max_payload_kg`.

### Envelope: `max_drop_height`

```yaml
max_drop_height: 3.0
```

Pass 3 rejects a `release(mode: latch)` whose preceding altitude exceeds it, and a `release(mode: winch)` whose `height` exceeds it.

### Validator: spatial targets

`_spatial_targets` emits the current position for `release`, `set_output`, and `hover` (with or without `over`) and the declared location for `land(at:)`, so the geofence and people-occupancy passes cover the moment the payload leaves the aircraft.

## Alternatives considered

1. **Keep `set_output` as the delivery verb.** Rejected as the end state; kept as the shipping path today. It is honest about the hardware but leaks the substrate into the language.
2. **Allow `manipulation` on drone manifests.** Rejected. A winch is not an arm, and the drone profile's exclusion protects the `grasp` / `release` semantics the home and industrial profiles depend on.
3. **A new `deliver` primitive.** Rejected. Adding a primitive is a one-way door; `release` with new modes covers the intent without widening the vocabulary.
4. **A separate aerial-delivery profile.** The drone profile README names this as the likely home. Deferred: a profile is heavier than a block plus two modes, and real demand should decide.

## Prior art

- RFC-0017 (`set_output`): the bounded line-write this RFC builds on for the mechanism binding.
- RFC-0002 §release: the existing `drop | place | hand_to_user` semantics and the drop-height ceiling that was specified but never enforced.
- ArduPilot `MAV_CMD_DO_WINCH` / `MAV_CMD_DO_GRIPPER`: the substrate surface `reference/ardupilot-runtime` already maps (ArduCopter 4.6 implements only the relaxed / relative-length / rate winch actions; `WINCH_DELIVER` and `WINCH_RETRACT` return FAILED, so the adapter sends signed relative lengths).
- [`examples/drone/parcel-delivery.urml.yaml`](../../examples/drone/parcel-delivery.urml.yaml): the program this RFC would simplify.

## Implementation plan

1. Schema: `PayloadMechanism`, `payload_mechanisms` on the manifest; `release.mechanism`, `release.latch`, new modes; inline `carrying` object; `max_drop_height` on the envelope.
2. Validator: Pass 2 mechanism / mass checks; Pass 3 drop-height and the widened `_spatial_targets`.
3. Runtime: `exec_release` lowering for `winch` / `latch` with the executor-owned wait; `ArduCopterAdapter` gains `send_payload_release` alongside the existing `set_output_line` path.
4. Conformance: fixtures for accepted delivery, mass over cap, drop above `max_drop_height`, and drop point outside the fence.
5. Examples: rewrite `parcel-delivery.urml.yaml` on the new verb; keep the `set_output` variant as the RFC-0017 example.

## Open questions

1. Should `parachute` be a mechanism kind in v1, or wait for a real airframe?
2. Does `release(mode: winch)` need a `retract: false` option for tethered sensor drops?
3. Should the executor-owned winch wait be bounded by a declared `max_line_m / rate_m_s` only, or also by a substrate completion signal where one exists (ArduPilot `WINCH_STATUS`)?

## Self-review (Phase 1)

- [x] No new primitive; two modes on an existing verb plus declarative blocks.
- [x] Purely additive; existing drone artifacts validate unchanged.
- [x] Substrate-neutral: nothing here names MAVLink in the schema.
- [x] Core Commitment untouched.
- [x] No em-dashes; one thought per paragraph.
