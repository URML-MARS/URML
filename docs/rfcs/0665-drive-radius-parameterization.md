---
rfc: 0665
title: Radius parameterization for drive arcs
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-04
updated: 2026-07-04
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

# RFC-0665: Radius parameterization for `drive` arcs

**Kind: Spec.** Extends the `drive` primitive from RFC-0630 with an optional,
mutually-exclusive `radius` field. This changes the shape of an accepted
primitive, which is a one-way door, so the decision is left to the maintainer.

**State: Draft.** Proposed in response to a live user bug report (Discussion
#572). Not yet settled. The Open questions section is the decision surface.

## Summary

RFC-0630 gave `drive` an optional `arc` field so a frameless robot can follow a
circular arc: `drive: {distance: 0.157, arc: 180}` drives a 0.157 m path while
sweeping 180 degrees. The radius is left implicit; the runtime recovers it as
`radius = distance / arc_in_radians`.

That encoding is correct but it puts an arithmetic burden on Layer 4. A person
says "orbit 180 degrees with a 5 cm radius", which is a radius and a sweep angle,
two numbers given directly. To emit today's `drive`, the language model must
convert them into an arc length, `distance = radius x angle_in_radians =
0.05 x pi = 0.157`. A small local model gets this wrong in a specific,
reproducible way: it drops or doubles the factor, and the error rides all the way
to the wheels.

This RFC proposes letting `drive` accept the radius directly:
`drive: {radius: 0.05, arc: 180}`, exactly equivalent to
`drive: {distance: 0.05 x radians(180), arc: 180}`. The model passes through the
two numbers it was handed, with no trigonometry, and the whole class of
arc-length arithmetic error disappears.

## Motivation

The motivating case is concrete and current. In
[Discussion #572](https://github.com/URML-MARS/URML/discussions/572), an active
user (the GoPiGo3 power user from RFC-0630, running a local `qwen3.5:9b` on the
robot) asked for a prompt that would make "orbit 180 degrees with a 5 cm radius"
drive a 5 cm-radius arc. The robot orbited at 10 cm instead, twice the requested
radius. He pinned it to the number.

Tracing it: the correct arc length for a 5 cm radius over 180 degrees is
`pi x 0.05 = 0.157 m`. The model emitted `distance: 0.314`, which is `2 x 0.157`.
It doubled, effectively using the diameter where it meant the radius, a classic
radius-versus-diameter slip. The runtime then inverted that faithfully,
`radius = 0.314 / radians(180) = 0.10 m`, and called the substrate orbit with a
10 cm radius. The 10 cm step in the same run showed the same doubling
(`0.629 = 2 x 0.314`). The runtime is not the bug; it is honestly reporting a
doubled input.

The immediate cause is the model's arithmetic. The deeper cause is the encoding.
Asking Layer 4 to compute `radius x angle_in_radians` on every arc puts a
multiplication in the hot path where a small model is weakest, and the failure is
silent: the emitted program is valid URML, validates clean, and drives the wrong
circle. A validator cannot catch it, because `distance: 0.314, arc: 180` is a
perfectly admissible motion. The only defense is to stop asking the model to do
the arithmetic.

This is not a GoPiGo-specific concern. Radius plus sweep angle is how humans and
beginner-robot APIs describe arcs (GoPiGo3 `orbit(degrees, radius)`, "circle of
radius R", the turtle-graphics `arc radius, degrees` form). URML already speaks
the drive-and-turn vocabulary of that audience (RFC-0630); the radius form
completes it.

## Proposal

Add one optional field to `DriveArgs`, and make `distance` optional so exactly one
of the two forms is chosen.

```yaml
# Straight line (unchanged).
- drive:
    distance: 0.30

# Arc, arc-length form (unchanged, still valid).
- drive:
    distance: 0.157
    arc: 180

# Arc, radius form (new). Equivalent to the line above.
- drive:
    radius: 0.05
    arc: 180
```

`radius` is a signed value in metres: the radius of the circular arc the drive
follows. It is meaningful only together with `arc`, and it is mutually exclusive
with `distance`.

### Semantics: the radius form is the arc-length form, inverted

The two forms describe the same motion. The equivalence is exactly the relation
the RFC-0630 runtime already uses, read the other way:

```
distance = radius x radians(arc)          # radius form  -> arc-length form
radius   = distance / radians(arc)        # arc-length form -> radius form  (arc != 0)
```

A runtime may implement the radius form by computing `distance` with the line
above and then reusing its existing arc lowering, or by mapping `radius` and
`arc` straight onto a substrate `orbit(degrees, radius)` call. Both are correct
and produce identical wheel motion. Nothing about the substrate mapping in
RFC-0630 changes; this RFC only adds a second, arithmetic-free way to name the
same arc.

Because the equivalence is exact and the runtime already computes this quotient,
the radius form adds no new geometry and no new execution path at the wheels. It
is purely a Layer-4 ergonomics change surfaced as a Layer-2 field.

### Sign convention

`radius` carries the same sign meaning that `distance` carries in the arc-length
form, so the equivalence `distance = radius x radians(arc)` holds with signs:

- `arc` is signed degrees, `+` counterclockwise (unchanged from RFC-0630).
- `radius` is signed metres. `radius > 0` with `arc > 0` is a forward arc curving
  left; the four sign combinations map one-to-one onto the four
  `(distance, arc)` sign combinations through the equivalence.

A robot that only drives forward-arcs (the common case, and all that
`orbit(degrees, radius)`-style APIs expose) will see positive `radius`. The
signed definition is kept so the radius form is a complete substitute for the
arc-length form, not a partial one.

### Field rules

`DriveArgs` becomes a one-of over three shapes:

1. `distance` alone: straight-line drive (unchanged).
2. `distance` + `arc`: arc, arc-length form (unchanged).
3. `radius` + `arc`: arc, radius form (new).

Constraints the schema enforces:

- Exactly one of `distance` / `radius` is present. Neither present is
  underspecified; both present is overspecified. Both are rejected at
  validation with a clear message.
- `radius` requires `arc`, and `arc` must be non-zero (a zero-degree arc has no
  radius). `radius` without `arc`, or with `arc: 0`, is rejected.
- `distance` with or without `arc` is unchanged, so every RFC-0630 program keeps
  validating exactly as before. This is a purely additive change; no existing
  program's meaning moves.

### Capability and envelope handling

The capability gate is unchanged: `drive` still requires
`mobility.supports_relative_motion` and the `educational` profile (RFC-0630).

The `max_relative_distance` bound applies to the path length the robot actually
travels, which for the radius form is the computed arc length
`|radius x radians(arc)|`, not the radius. The validator computes the effective
distance for whichever form was supplied and checks the same bound against it, so
the two forms are bounded identically. The RFC-0518 velocity and acceleration
limits apply unchanged.

## Why not an existing mechanism

**Leave it to Layer 4 / a better model.** A stronger model does get the
arithmetic right, and a system-prompt line spelling out
`arc_length = radius x angle_in_radians` reduces the error rate. But this is
mitigation, not a fix. URML's educational reach depends on small on-device models
(the motivating user runs a 986 MB model on the robot itself, RFC-0630). An
encoding that is only safe with a large model fails the audience that most needs
the natural-language front door. The right fix removes the arithmetic rather than
hoping it is done correctly.

**A separate `orbit` primitive.** Rejected. Adding a primitive is a one-way door,
and an orbit is not a new intent; it is the arc `drive` already expresses.
A second verb for the same motion would violate URML's one-primitive-per-meaning
preference and split the safety reasoning across two verbs. A field on the verb
that already owns arcs is the smaller change.

**Radius-only, drop the arc-length form.** Rejected. The arc-length form is
already Accepted and in use (RFC-0630, the gopigo3 example), and some callers do
have the path length in hand rather than the radius. Keeping both, as a one-of,
costs one schema validator and lets each caller name the arc with the numbers it
actually has.

## Prior art

- GoPiGo3 `EasyGoPiGo3.orbit(degrees, radius_cm)`: the exact
  degrees-plus-radius shape, and the substrate the motivating report runs on.
- Turtle-graphics arc primitives: `arc(radius, extent)` in Python's `turtle`,
  radius plus sweep angle.
- Everyday phrasing: "drive a circle of radius R", "orbit N degrees at radius R".
  Radius and sweep are the two numbers a person states; arc length is derived.

## Implementation plan

1. `DriveArgs`: add `radius: float | None`; relax `distance` to `float | None`;
   add a model validator enforcing the one-of and the `radius`-requires-nonzero-
   `arc` rules, with clear messages
   (`primitive.drive_underspecified`, `primitive.drive_overspecified`,
   `primitive.drive_radius_requires_arc`).
2. Validator: compute the effective path length for the radius form
   (`|radius x radians(arc)|`) and apply the existing `max_relative_distance`
   check to it, so both forms are bounded identically.
3. Reference runtime: lower the radius form via the equivalence (compute
   `distance`, reuse the RFC-0630 arc path) or map `radius`/`arc` straight onto
   the substrate arc call; the gopigo3 adapter maps to `orbit(arc, radius_cm)`
   with no division.
4. Conformance fixtures: a radius-form arc validates and lowers to the same wheel
   motion as its arc-length twin (equivalence fixture); the underspecified,
   overspecified, and `radius`-without-`arc` cases are rejected.
5. Worked example / gopigo3 update: show "orbit 180 degrees at 5 cm radius"
   emitting `drive: {radius: 0.05, arc: 180}` and lowering to `orbit(180, 5.0)`,
   the case Discussion #572 got wrong under the arc-length form.
6. Layer-4 grammar note and a bridge few-shot: when an utterance gives a radius
   and a sweep angle, emit the radius form and do not compute an arc length.

## Open questions

1. **Do this at all, or fix it in Layer 4 only?** The cheapest response to #572 is
   a prompt-contract line plus a model recommendation, no schema change. The case
   for the field is that the arithmetic-free encoding is robust across models and
   is the shape the audience's APIs already use; the case against is that it adds
   a second way to say one thing and slightly widens the primitive. This is the
   maintainer's call and the reason this RFC is Draft.
2. **Signed or magnitude `radius`?** Signed keeps the radius form a complete
   substitute for the arc-length form (all four quadrants) at the cost of a sign
   rule a small model could still get wrong. Magnitude-only is simpler and matches
   `orbit(degrees, radius)` APIs directly, but cannot express a reversing arc, so
   the arc-length form would remain the only way to write one. Recommendation:
   signed, for completeness, since the common forward-arc case uses positive
   `radius` and never has to reason about the sign.
3. **Keep both forms, or is one-of churn not worth it?** The plan keeps both. An
   alternative is to accept the radius form as the blessed way to write an arc and
   leave the arc-length form documented but de-emphasized. No behavior differs;
   this is only about what the docs and the bridge steer toward.

## Resolved decisions

None yet. This RFC is Draft pending the maintainer's answers to the Open
questions, chiefly question 1 (whether to add the field at all).

## Strategic note

Same shape as RFC-0630 itself: an active user, on a real robot, in URML's core
educational audience, hit a real limitation, and the fix is small and additive.
The failure mode here is subtler and more instructive than a rejected program,
because a valid program drove the wrong circle. It is a reminder that when a small
model is the compiler, an encoding that demands arithmetic is a latent bug, and
the cleanest safety win is to let the model pass through numbers rather than
transform them. The risk to manage is primitive-surface creep; the mitigation is
that this is a field on an existing verb, gated exactly as RFC-0630 gated it, with
no new execution path at the wheels.
