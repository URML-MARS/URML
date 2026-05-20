---
rfc: 0020
title: Autoware AV substrate — research-grade autonomous-vehicle profile
author: Ido Yahalomi (ido@jacob-ai.com)
state: Draft
created: 2026-05-20
updated: 2026-05-20
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

# RFC-0020: Autoware AV substrate — research-grade autonomous-vehicle profile

## Summary

Autoware is named in the manifesto's Layer-0 examples and the
manifesto's stretch goals as a *research-grade autonomous-vehicle*
profile (explicitly **not** production safety-certified). Its
operational model — plan a path subject to an HD-map and an operational
design domain (ODD), then follow a precomputed timed trajectory — is
genuinely inexpressible with the frozen v0.1 Protocol. `move_to(named
location)` is "go to a named pose," not "compute a trajectory in a
cost-map and execute it" — they are different verbs with different
validation surfaces. This RFC is filed as a **Draft for maintainer
decision** by the spec-gap loop (RFC-0014); the companion
`feat/autoware-manifest-spec-only` PR ships manifest + spec only, no
green adapter — the no-SDK-humanoid (`ghost_vision60`, `optimus_biped`,
`figure_biped`, `apollo_biped`, `neo_biped`) precedent. The RFC
proposes two new Layer-2 primitives (`plan_path`, `follow_trajectory`)
and a new `av` profile with AV-specific manifest blocks; **none ship
until ratified**.

## Motivation

A green Autoware adapter against the frozen Protocol would have to
pretend `move_to(named_location)` means "drive autonomously across a
mapped urban area to a destination," which is a category lie. The
honest options are: (1) defer the substrate as
manifest-and-spec-only until primitives exist (the no-SDK-humanoid
precedent), or (2) write the primitives down now and ship the adapter
when they ratify. RFC-0020 chooses (1) for this round: the substrate
is too large for a silent adapter, and the AV profile interactions
(HD-map alignment, ODD, Minimum-Risk Maneuver) need careful design.
Filing the RFC + a manifest+spec-only scaffold now records the gap
honestly and lets a future PR land the primitives + adapter on a
ratified foundation. Without this RFC, the silent failure mode is a
greenwashed adapter where `move_to` quietly means path-planning —
exactly the substrate leak RFC-0014 prevents.

## Detailed design

### Two new Layer-2 primitives

```
plan_path:
  from: <location | pose>
  to: <location | pose>
  along: <HD-map identifier>     # optional; constrains the corridor
  store_as: <Identifier>         # bind the planned trajectory
  store_alt_as: <Identifier>     # optional; bind a Minimum-Risk fallback
```

```
follow_trajectory:
  trajectory: $<bound>           # required, from plan_path
  speed_envelope:                # optional; AV-profile envelope tightens
    max_velocity_mps: <number>
    max_accel_mps2: <number>
  on_off_route: abort | replan   # ODD violation response
```

`plan_path` is a *compute* verb: it does not actuate; it returns a
trajectory binding that `follow_trajectory` consumes. This split is
the AV equivalent of `detect` → `grasp($target)` — perception
(detection) is a compute step bound by a variable that the actuation
step consumes — RFC-0002's precedent for separating "decide" from
"do." `follow_trajectory` is the only verb that actuates.

### New `av` profile

A new `spec/profiles/av/README.md` (the *research-grade* AV profile,
distinct from the home/drone/industrial/educational/research profiles).
AV-specific envelope and manifest fields:

- **Manifest extensions**: `hd_map: { format, uri, sha256, frame }`
  (the bound digital map a planner cost-mapped against);
  `odd: { regions: [{name, polygon}], max_velocity_mps, weather }`
  (the operational design domain — where the AV is allowed); `mrm:
  { strategy: pull_over | stop_in_lane | controlled_stop }` (the
  Minimum-Risk Maneuver when ODD is exited or the trajectory aborts).
- **Envelope tightening**: AV envelopes carry HD-map alignment SLA
  (max_drift_m), sensor-fusion latency SLA (max_perception_age_ms),
  and the per-ODD speed cap.

The AV profile is research-grade (`production_safety_certified: false`
is a normative profile attribute, matching the manifesto's stated
scope). The default policy file lands no automotive-specific rules in
this RFC; production-safety certification is a separate concern.

### Substrate binding: Autoware

Autoware on ROS 2 + Autoware Universe is the reference target.
`plan_path` binds to Autoware's planning pipeline
(`mission_planner` → `behavior_planner` → `motion_planner`);
`follow_trajectory` binds to its control stack (`pure_pursuit` /
`MPC` controllers). The non-ROS sketch: Apex.AI's Apex.OS exposes the
same operations through its own ECU runtime (vendor SDK, no ROS) —
the same plan_path/follow_trajectory shape lands against Apex.OS's
service surface using the RFC-0019 pattern (a binding declaration,
not a new primitive).

### Spec changes

- **Layer 1**: optional `hd_map` / `odd` / `mrm` blocks added to the
  capability manifest. Optional means existing manifests are
  unchanged.
- **Layer 2**: two new primitives + JSON Schemas (the additions
  above).
- **Layer 3**: variable binding gains a `trajectory` type tag (same
  pattern as RFC-0013's `object` tag bound by `pick_from`).
- **Layer 4**: NL grammar gains two verb mappings.
- **`spec/profiles/av/`**: new profile spec doc.

### Validator changes

Pass-2: `plan_path` requires a declared HD-map in the manifest;
`follow_trajectory.trajectory` must reference a binding produced by
`plan_path` in the same behavior tree. Pass-3 (envelope): trajectory
speed at every waypoint must be ≤ the ODD speed cap; ODD-exit
triggers `mrm`. Pass-5 (policy): no new automotive-specific rules in
v0.1; the standard provenance/origin rules still apply.

### Reference runtime changes

A future `reference/autoware-runtime/` PR — explicitly *not* in this
RFC's manifest-and-spec-only scaffold — implements the ROS-side
binding. The non-ROS Apex.OS binding is a follow-on demonstrating the
substrate-neutrality acid test.

### Conformance suite changes

The manifest-and-spec-only scaffold (companion PR) lands one
acceptance fixture under a new `conformance/fixtures/research/` dir
(reuses the existing RFC-0012 research profile by Identifier — no
schema for `av` until RFC-0020 ratifies), validating the
`autoware_av_research` manifest under `program: { ... report ... }`.
A future fixture exercises `plan_path` + `follow_trajectory` once
this RFC + the new primitives ratify; not filed here.

## Backward compatibility

Fully compatible at the Layer 1 level (optional new blocks). The new
Layer 2 primitives are additive — pre-existing programs do not use
them. The new `av` profile is opt-in. Pre-v1.0.

## Drawbacks

This is the largest spec surface URML has proposed so far (two new
primitives + a new profile + three new manifest blocks + new
validator checks). Each piece is small in isolation; the *coordination
risk* is real — multi-layer changes are what CLAUDE.md flags as
"suspect." Mitigation: ship in two stages — the RFC + manifest+spec
scaffold first (this batch), the validator changes + Layer 2
primitives + adapter as a coordinated second PR after this RFC
ratifies. A second drawback: AV safety semantics could pull URML into
implying it certifies AV systems. The profile's `production_safety_
certified: false` and the manifesto's research-grade framing are the
mitigation, but they are mitigations, not vanishings — they require
discipline at every adopter touchpoint.

## Alternatives considered

1. **No AV substrate (defer indefinitely).** Rejected: the manifesto
   names Autoware as a target; deferring forever leaves the
   "everywhere" claim aspirational. The honest middle is to file the
   RFC now and stage the implementation, which this RFC does.
2. **Reuse RFC-0015 `call_program` for AV operations** (the AUTOSAR
   pattern from RFC-0019). Rejected: `call_program` is intentionally
   opaque — its drawback is "every hard mapping becomes call_program."
   `plan_path` / `follow_trajectory` are *typed*, *validatable*
   primitives whose envelope checks (speed cap, ODD bound) require
   the validator to see inside the operation. The opaque-vs-typed
   tradeoff is the same one RFC-0017 already made for `set_output`
   over `call_program`.
3. **One combined `drive_to(destination)` primitive instead of
   plan/follow split.** Rejected: it conflates compute (planning) and
   actuation (following) — the validator could not surface a
   "planned trajectory exceeds ODD speed" error, because planning
   would not produce a typed artifact. RFC-0002's precedent (detect →
   grasp) is the right model.
4. **A green adapter against the frozen Protocol with `move_to` as
   the AV verb.** Rejected: that is exactly the substrate leak
   RFC-0014 prevents and the no-SDK-humanoid precedent rejects.

## Prior art

Autoware Universe (planning + control pipelines); Apex.AI / Apex.OS
(non-ROS automotive substrate); ROS 2 Nav2 (the analog of Autoware
for ground robots — already covered by `move_to` + the existing
mobile-runtime); ISO 21448 SOTIF (the ODD concept); UNECE R157
Automated Lane Keeping Systems (the MRM concept). URML-internal:
RFC-0002 (primitive economy — why split plan and follow), RFC-0011
(the profile-declares-its-own-defaults pattern), RFC-0017 (the
typed-over-opaque tradeoff this RFC inherits), the no-SDK-humanoid
precedent (`ghost_vision60.yaml` → manifest-and-spec-only when
adapter is premature).

## Unresolved questions

- `plan_path` cost model: cost-map URI in the manifest, or a per-call
  preset? Probably preset (`comfort | sport | conservative`) to keep
  the program simple; the cost-map binding is deployment config.
- HD-map format: bound to Lanelet2 (Autoware's choice) or kept
  format-neutral via `format` field? Lean: format-neutral, validator
  checks the bound file exists.
- Whether `av` should be a *profile* (declared in `program.profile`)
  or a *manifest section* (declared in `capability_manifest.av`).
  Lean profile, mirroring the existing five (home/drone/industrial/
  educational/research).
- Profile name: `av` vs `autonomous_vehicle` vs `automotive` — left
  for the maintainer to choose during RFC review (flagged in the
  approved plan).

Each is small enough to settle before Open → Accepted.

## Implementation note

This is a Draft-only RFC. A companion PR
`feat/autoware-manifest-spec-only` ships the `autoware_av_research`
manifest fixture + a `conformance/fixtures/research/` acceptance
fixture (under the existing `research` profile, since the `av` profile
does not exist until this RFC ratifies; the fixture's program is a
single `report` so it passes the frozen Protocol). No
`reference/autoware-runtime/` package lands until after RFC-0020
ratification + a follow-up PR adds the validator changes, the two
primitives, the `av` profile spec, the validator checks, and the
adapter. That is a coordinated multi-layer change, hence correctly an
RFC.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test). — **YES**: this RFC adds *two* primitives; **ROS sketch** = bind to Autoware Universe's `mission_planner`/`behavior_planner`/`motion_planner` (`plan_path`) and `pure_pursuit`/`MPC` controllers (`follow_trajectory`); **non-ROS sketch** = bind to Apex.AI/Apex.OS service operations using the RFC-0019 binding pattern. Both sketches in §Detailed design → Substrate binding.
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
