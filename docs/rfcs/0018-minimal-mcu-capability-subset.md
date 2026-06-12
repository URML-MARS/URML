---
rfc: 0018
title: Minimal-MCU capability subset in the manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-19
updated: 2026-06-12
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

# RFC-0018: Minimal-MCU capability subset in the manifest

## Summary

A mobile educational buggy fits the v0.1 capability manifest honestly
(it really is `mobility.drive_type: differential`). A large class of
educational microcontroller nodes does not: a fixed micro:bit with an
LED, a buzzer, and a light sensor; a breadboard with one servo. These
have no honest `mobility`, no `perception` camera, no manipulator —
yet they are exactly the cheap, ownable platforms RFC-0011's
educational flywheel depends on. This RFC is filed as a **Draft for
maintainer decision** by the spec-gap loop (RFC-0014); the
`urml-embedded-runtime` build surfaced it. It proposes — for
discussion, not yet accepted — a minimal *declaration* a non-mobile
sensor/actuator node can present so the conformance suite can check it
as a coherent class. It explicitly does **not** own the actuation verb
("blink the LED"): that is RFC-0017's `set_output`, cross-referenced,
not duplicated.

## Motivation

The manifest's `mobility`/`manipulation`/`perception` blocks are each
individually optional, so a minimal node *can* technically omit them
all. But then the manifest says almost nothing, and there is no
positive way to declare "this is a minimal actuator/sensor node" that
the conformance suite can recognise and test as such. The dishonest
workaround — give an LED-only board a fake `differential` mobility so a
fixture validates — is exactly the kind of silent schema-bending the
spec-gap loop exists to stop. Without an honest minimal declaration,
the single largest population of classroom hardware (and the
contributors who own it) cannot be a first-class, conformance-checkable
URML target, which directly undercuts the educational adoption flywheel
RFC-0011 is built on.

## Detailed design

An optional Layer-1 manifest block:

```
minimal_node:
  class: sensor | actuator | sensor_actuator
  declared_sensors: [ <Identifier>, ... ]   # names also in perception.sensors if present
  declared_outputs: [ <Identifier>, ... ]   # the lines RFC-0017 set_output targets
  has_locomotion: false                     # explicit: this node does not move
```

`extra: forbid` as everywhere in Layer 1. A manifest with
`minimal_node` and no `mobility` is then a *valid, recognised* shape
rather than an under-specified one: the validator can confirm a
program for it uses only primitives the declared sensors/outputs
support, and the conformance suite can carry a `minimal_node` fixture
class. The block is declarative only; it introduces no primitive.

### Spec changes

- **Layer 1**: add the optional `minimal_node` model + spec section,
  and a normative note that `minimal_node` and `mobility` are mutually
  exclusive (a thing either drives or declares it does not).
- No Layer 2/3/4 change. The actuation verb a minimal node needs is
  RFC-0017's `set_output`; this RFC is the *capability-declaration*
  half and references RFC-0017 rather than restating it.

### Validator changes

Schema parse + the mutual-exclusion check in v0.1. A future Pass-2 rule
("a program for a `minimal_node` may only use primitives its declared
sensors/outputs support") is explicitly deferred — the RFC-0011 /
RFC-0013 declare-now/enforce-later staging.

### Reference runtime changes

None required. `EmbeddedAdapter` already returns honest
`not_supported_on_mcu` results for capabilities a board lacks; it would
optionally read `minimal_node` to choose its command set, but is not
obligated to in v0.1.

### Conformance suite changes

A `conformance/fixtures/educational/` manifest-acceptance fixture for a
`minimal_node` LED/sensor board (validator-only, no `expected_execution`
— the no-SDK-humanoid pattern), once RFC-0017 lands the verb such a
node would actually use.

## Backward compatibility

Fully compatible. Additive optional block; every existing manifest is
still valid; the mutual-exclusion rule only constrains manifests that
opt into `minimal_node`. Pre-v1.0.

## Drawbacks

It adds manifest surface for the smallest robots, which can read as
disproportionate. A fair objection is "just let minimal boards omit
every block and accept a near-empty manifest" — but that yields an
untestable, meaningless manifest, which is worse for a conformance
standard than a small honest declaration. There is also coupling risk
with RFC-0017: if that RFC is rejected, `declared_outputs` has no
consumer and this block is half-useful; this RFC should not advance to
Accepted ahead of an RFC-0017 decision, and that ordering constraint is
a real scheduling cost.

## Alternatives considered

1. **Omit all optional blocks (status quo).** Rejected: produces an
   untestable manifest and no positive "minimal node" identity — the
   exact gap. (It is, however, the legitimate "do nothing in v0.1"
   option the maintainer may pick.)
2. **A new top-level profile for MCUs.** Rejected: profiles are
   behavior-shaping (RFC-0011 is the right home for educational
   *behavior* defaults); this is a *capability-shape* problem, which
   belongs in the manifest, not a profile fork ("profiles over forks").
3. **Fold this into RFC-0017.** Rejected: RFC-0017 is an actuation
   *primitive*; this is a *manifest declaration*. Bundling a schema
   block into a primitive RFC would muddy two separately-decidable
   questions — but they must be sequenced (0017 first).

## Prior art

Minimal device profiles in constrained-device standards (OCF/IoTivity
device types, Matter minimal device types, Web of Things "thing
descriptions" for sensor-only nodes). URML-internal: RFC-0011
(educational flywheel — the why), RFC-0017 (the actuation verb a
minimal node pairs with), RFC-0006 (declare-an-abstract-capability
precedent), and the no-SDK-humanoid manifest-acceptance fixtures (the
validator-only conformance pattern this would reuse).

## Unresolved questions

- Exact `class` enumeration and whether `sensor_actuator` is needed or
  is just "both lists non-empty".
- Whether `declared_outputs` should reference RFC-0017's line
  declaration directly (coupling) or duplicate a minimal name list.
- Sequencing with RFC-0017 (this RFC should not reach Accepted first).

## Implementation note

The ordering constraint is satisfied: RFC-0017 (`set_output`) shipped
first, so `declared_outputs` has its consumer and the block is fully
useful rather than half-useful.

### Shipped (Draft → Implemented, 2026-06-12)

Landed as the single Layer-1-only change the note anticipated, fully
additive (every existing manifest stays valid; `manifest_version` stays
`0.1`):

- **Schema**: `MinimalNode` (`class` ∈ sensor/actuator/sensor_actuator,
  `declared_sensors`, `declared_outputs`, `has_locomotion`) +
  `CapabilityManifest.minimal_node`; an intra-block validator requires a
  sensor class to declare sensors and an actuator class to declare outputs.
  Spec: `spec/layer-1-hal/v0.2.0.md` §2.17.
- **Validator** (`_check_minimal_node`, manifest-static Pass-2): mutual
  exclusion with `mobility` (`capability.minimal_node_with_mobility`),
  `has_locomotion` must be false (`..._locomotion_inconsistent`),
  `declared_outputs` ⊆ `outputs.lines[]` (`..._undeclared_output`),
  `declared_sensors` ⊆ `perception.sensors` when present
  (`..._undeclared_sensor`). Per-program enforcement stays deferred
  (declare-now/enforce-later).
- **Conformance**: `microbit_minimal_node` (+ `_mobility` / `_bad_output`)
  manifest fixtures + three `conformance/fixtures/educational/` cases
  (LED-board acceptance positive; mobility-coexist + undeclared-output
  negatives).
- **Example**: `examples/educational/blink-the-led` — a micro:bit-class
  `minimal_node` that blinks its declared LED via `set_output` (pulse),
  runnable end-to-end on the hermetic mock.
- **Tests**: `reference/validator/tests/test_minimal_node.py` (8 cases).

The substrate-neutrality posture holds: `minimal_node` is a capability
*declaration*, not a primitive; the verb it implies is RFC-0017's
`set_output`, referenced not duplicated.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test). — N/A: this RFC adds no primitive; it is an optional Layer-1 manifest declaration only (the actuation verb is RFC-0017).
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
