---
rfc: 0518
title: Base-level mobility bounds for a velocity-controlled mobile base
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0518: Base-level mobility bounds for a velocity-controlled mobile base

## Summary

URML's `mobility` block declares `max_velocity` (linear) and `max_payload`, and
the legged/humanoid platforms carry a `whole_body` block (RFC-0384) for
kinematic structure and stability. But a large class of platforms is exposed to
upper layers as an **omnidirectional velocity-controlled base**: you command it
with `Twist`, and its whole-body internals are not part of the public interface.
For those, the relevant bounds are base-level, and URML cannot express most of
them today. This RFC adds optional base-level motion bounds to `mobility`: angular
velocity, linear and angular acceleration, traversable slope, and obstacle height.
It is *not* a new primitive.

**State: Implemented** (2026-06-13). Ships the schema fields, one Pass-2
coherence check, unit tests, and a worked intermediary-node example. Additive: a
manifest without these fields validates unchanged.

## Motivation

Surfaced directly by an engagement. On
[legubiao/quadruped_ros2_control#65](https://github.com/legubiao/quadruped_ros2_control/issues/65)
the maintainer explained how the stack actually operates:

> The stack abstracts the quadruped as an omnidirectional mobile base at the
> controller's public interface. Upper layers send `Twist` velocity commands,
> while all low-level logic (leg actuation, CoM and stability enforcement,
> MPC/RL-based motion generation) is encapsulated internally and not exposed.

And, on the manifest:

> The proposed definition of `legged drive type + whole_body CoM/support polygon
> limits` does not align with this stack's public abstraction, as these details
> are internal to the controller implementation. A manifest suited for this
> stack would instead define base-level capability boundaries: maximum linear and
> angular velocity, acceleration limits, terrain constraints (slope, obstacle
> height), and payload limits. These are the relevant bounds for upper-layer
> intent.

He also confirmed the layer's value: the controllers have no unified, declarative
capability validation, so an invalid velocity command may fail silently or
destabilise the platform, and the lowest-effort integration is an intermediary
URML node that validates incoming intent against the base manifest and then emits
`Twist`, with no change to the ros2_control stack.

URML had `max_velocity` and `max_payload` but no angular velocity, acceleration,
or terrain bounds, so it could not express the base envelope such a node would
check against. This is a capability-declaration gap, not a behavior gap.

## Detailed design

Five optional fields on the existing `mobility` block:

```
mobility:
  drive_type: omnidirectional
  max_velocity: 1.5
  max_angular_velocity: 1.0        # rad/s, >= 0
  max_linear_acceleration: 2.0     # m/s^2, >= 0
  max_angular_acceleration: 3.0    # rad/s^2, >= 0
  max_traversable_slope_deg: 25.0  # (0, 90]
  max_obstacle_height_m: 0.15      # m, >= 0
  max_payload: 10.0
```

`extra: forbid` as everywhere in Layer 1. Absent fields ⇒ "unspecified"
(today's behavior). These are the right altitude when a platform is exposed as a
base and its whole-body internals are not; they coexist with, and do not replace,
`whole_body` (RFC-0384), which is for stacks that *do* expose whole-body control.

### Spec changes

- **Layer 1**: add the five optional fields to the `Mobility` model and §2.4 of
  the Layer-1 HAL spec. No Layer 2/3/4 change; no new primitive.

### Validator changes

Field validity is schema-enforced (non-negative; slope in (0, 90]). One Pass-2
**internal-coherence** check ships: the terrain bounds
(`max_traversable_slope_deg`, `max_obstacle_height_m`) are not applicable to an
aerial `drive_type` (multirotor / fixed_wing / vtol), which does not traverse
ground; declaring them there is incoherent
(`capability.terrain_bound_not_applicable`).

The fields are otherwise *declarations* a velocity-controlled-base runtime or an
intermediary node validates intent against. URML core has no `Twist`-velocity
primitive to check, so the enforcement of a base-velocity intent against these
bounds lives in the consuming node, exactly the architecture the maintainer
proposed. The reference intermediary node (`examples/mobile-base/`) demonstrates
it.

### Reference runtime changes

None required. A mobile runtime MAY read these bounds to validate base intent
before emitting `Twist`, but is not obligated to in v0.1.

## Alternatives considered

**Use the `whole_body` block (RFC-0384).** Rejected for this case: the maintainer
was explicit that the whole-body internals (CoM, support polygon, MPC/RL) are not
exposed at the public interface, so a whole-body manifest would describe state the
upper layer cannot command or observe. Base-level bounds match the actual
abstraction. The two blocks serve different exposure levels and coexist.

**A separate `base_limits` block.** Rejected: these are mobility facts and belong
on `mobility` next to `max_velocity` / `max_payload`, not in a parallel block.

**Enforce base-velocity intent in the core validator.** Rejected: URML is
intent-not-trajectory and has no primitive carrying a raw `Twist`; forcing one in
would be a leaky abstraction. The bounds are declared in the manifest and enforced
by the consuming node, which is where a velocity command actually exists.

## Prior art

`Twist` velocity limits, acceleration limits, and traversability (slope / step
height) are the standard parameters of ROS 2 mobile-base controllers and
nav stacks (`diff_drive_controller`, Nav2 costmap traversability). This RFC
declares those bounds at the manifest level so an intent layer can check against
them.

## Implementation plan

1. Five fields on `Mobility` (`schemas/manifest.py`). Done.
2. Error code `capability.terrain_bound_not_applicable` + `_check_base_mobility_bounds`
   (`errors.py`, `validator.py`). Done.
3. Unit tests in `test_base_mobility_bounds.py`. Done.
4. Worked intermediary-node example under `examples/mobile-base/` (validate base
   intent -> emit `Twist`), byte-asserted. Done.
5. Layer-1 HAL §2.4 spec update. Done.

## Open questions

- A future rule could relate the base bounds to a safety-envelope cap (an envelope
  that tightens the angular-velocity or acceleration bound, strictest wins), the
  base-motion analogue of the existing `max_velocity` envelope relationship.
  Deferred until a primitive or envelope field carries the commanded base motion.
