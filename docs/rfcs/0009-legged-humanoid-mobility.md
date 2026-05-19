---
rfc: 0009
title: Legged and humanoid mobility in the capability manifest
author: URML Maintainers (maintainers@urml.dev)
state: Implemented
created: 2026-05-17
updated: 2026-05-19
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

# RFC-0009: Legged and humanoid mobility in the capability manifest

## Summary

The Layer-1 capability manifest's `mobility.drive_type` enumeration has no value for legged platforms. This RFC adds two values — `quadruped` and `biped` — so that four-legged robots (Boston Dynamics Spot, ANYbotics ANYmal, Ghost Vision 60) and bipedal humanoids (Agility Digit, and the manifest-only humanoids Tesla Optimus, Figure, Apptronik Apollo, 1X NEO) can declare a schema-valid manifest. The change is additive and backward compatible.

## Motivation

URML now ships reference adapters for legged and humanoid robots: the legged runtime (`SpotAdapter`, `AnymalAdapter`) and the humanoid runtime (`DigitAdapter`). Each adapter implements the `ROSAdapter` Protocol and passes its hermetic suite. None of them can be exercised through the conformance suite, because a conformance fixture needs a capability manifest and a legged robot cannot author one: `mobility.drive_type` is a closed `Literal` of nine wheeled/aerial/manipulator values with no legged member.

```yaml
mobility:
  drive_type: quadruped   # rejected: not a member of the Literal
  max_velocity: 1.6
  station_keeping: true
```

This is the single blocker called out as "deferred, RFC-gated" in the legged (#64) and humanoid (#65) PRs. Until it is closed, the legged/humanoid families have unit coverage but zero conformance coverage, and no compliant per-vendor manifest can be written.

## Detailed design

Add `quadruped` and `biped` to the `Mobility.drive_type` `Literal` in `reference/validator/src/urml_validator/schemas/manifest.py`. Two values, not one per brand: `drive_type` describes the *locomotion class* the runtime must reason about (gait, station-keeping, fall recovery), not the vendor. Spot and ANYmal are both `quadruped`; Digit, Optimus, Apollo, NEO are all `biped`. Vendor identity already lives in `provenance.components[].vendor`; duplicating it in `drive_type` would be redundant and would make the enum unbounded.

`humanoid` is deliberately *not* added as a separate value. A humanoid is a biped with arms; the legs are `biped` and the arms are declared in the existing `manipulation` block. Adding `humanoid` would conflate locomotion with manipulation and create an ambiguous choice for every two-legged robot.

`station_keeping` keeps its existing meaning. A legged robot that actively balances sets `station_keeping: true` (Spot and Digit do); this already gates `hover` correctly with no change.

### Spec changes

- **Layer 1** (`spec/layer-1-hal/`): document `quadruped` and `biped` in the `drive_type` table, with the "legs are mobility, arms are manipulation" rule and the `station_keeping` note. No other layer changes — Layer 2/3/4 never branch on `drive_type`.

### Validator changes

One enum widened. No new pass, no changed logic. A manifest using the new values parses and flows through Passes 1–5 unchanged; the compliance pass (RFC-0004) already keys on `provenance`, not `drive_type`, so a denylisted-vendor legged robot is rejected exactly as a wheeled one is.

### Reference runtime changes

None required. The adapters already exist and do not read `drive_type`; the value is consumed by the validator and by deployment tooling, not the dispatch path.

### Conformance suite changes

- New `conformance/fixtures/quadruped/01_patrol_positive.yaml` — a nav-only patrol on a `quadruped` manifest, proving the new enum end-to-end (passes hermetically against `MockROSAdapter` and adapter-agnostically against `SpotAdapter`/`AnymalAdapter`).
- New `conformance/fixtures/quadruped/02_unitree_vendor_denied.yaml` — a `quadruped` manifest whose critical component vendor is `unitree` (FCC Covered List); rejected with `policy.vendor_denied`. This exercises the new enum *and* confirms Unitree is treated exactly like DJI under the bundled US-federal default policy, consistent with the founder's prior decision.
- New canonical manifests `spot_quadruped` and `unitree_quadruped_denied` in the manifest registry.

The per-vendor compliant manifests for ANYmal (Switzerland), Digit (US), and the manifest-only humanoids (Tesla/Figure/Apptronik/1X, all US) are mechanical follow-ups now unblocked by this RFC — each is the `spot_quadruped`/`industrial_cell` provenance pattern with a different `country_of_origin`/`vendor`. They are not enumerated here to keep the RFC's diff reviewable.

## Backward compatibility

Fully compatible. The change is purely additive to a pre-v1.0 enum: every manifest valid before this RFC is valid after it. No existing fixture, runtime, or program changes behavior.

## Drawbacks

`drive_type` now mixes "how many contact points / what gait" granularity (`quadruped`, `biped`) with the existing wheeled granularity (`differential`, `ackermann`, …). A purist taxonomy might prefer an orthogonal `locomotion: {legs: 4}` structure. That is heavier than the problem warrants today and would itself be a breaking restructure; the flat enum stays consistent with the existing nine values and can be revisited in a post-v1.0 mobility-model RFC if real need appears.

## Alternatives considered

1. **One value per brand (`spot`, `anymal`, `digit`, …).** Rejected: unbounded enum, vendor identity duplicated with `provenance.vendor`, and the runtime does not care about the brand, only the locomotion class.
2. **A single `legged` value.** Rejected: quadruped and biped have materially different stability and fall-recovery semantics that deployment tooling and future envelope checks will need to distinguish; collapsing them discards information that is expensive to re-add later (a one-way door, per the manifesto's primitive-economy principle applied to enums).
3. **Add `humanoid` alongside `biped`.** Rejected: a humanoid is a `biped` plus `manipulation`; a separate value creates an ambiguous choice and conflates two manifest concerns.
4. **A free-form `drive_type: str`.** Rejected: it deletes the validator's ability to reject typos and unknown classes, which is the point of a closed enum.

## Prior art

`differential`/`ackermann` follow the ros2_control and Nav2 drive-type vocabulary. The legged/biped split mirrors the platform taxonomy in the Boston Dynamics Spot SDK, ANYbotics API, and the `legged_control` / `humanoid` MuJoCo/Isaac model families. URML-internal prior art: RFC-0002 (primitive economy — "adding is a one-way door") motivates keeping two precise values rather than one lossy one or many vendor ones.

## Unresolved questions

- Whether a future RFC should add an orthogonal whole-body/bimanual manipulation block (the humanoid runtime's v0.1 deliberately scopes to the locomotion subset). Out of scope here; tracked by the humanoid runtime README.
- Whether `service_ceiling`-style fields need a legged analog (e.g., max step height). Not needed by any v0.1 primitive; deferred until one needs it.

## Implementation note

One PR (this branch): the enum change + RFC + the two quadruped fixtures + the two registry manifests + verification via the conformance suite. The per-vendor compliant manifests (ANYmal/Digit/Tesla/Figure/Apptronik/1X) follow as a mechanical PR once this lands. No coordinated multi-layer change — Layer 1 only.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case (the #64/#65 adapters cannot get conformance coverage).
- [x] At least one alternative is genuinely considered and rejected with reasons.
- [x] Backward compatibility is explicit (additive, fully compatible, pre-v1.0).
- [x] The change is the minimum that closes the blocker (one enum widened, no logic change).
