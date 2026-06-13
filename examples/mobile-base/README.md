# URML as a validated-intent node above a velocity-controlled base

A quadruped (or any mobile base) is often exposed to upper layers as an
**omnidirectional velocity-controlled base**: you send it `Twist` commands, and
all the hard parts (leg actuation, centre-of-mass and stability enforcement,
MPC/RL motion generation) live inside the controller and are not exposed. At that
public interface, the right place for URML is not the whole-body manifest
(RFC-0384 would be the wrong altitude); it is a **base-level capability manifest**
plus an intermediary node that validates intent before it becomes a `Twist`.

This example comes from the
[quadruped_ros2_control engagement](https://github.com/legubiao/quadruped_ros2_control/issues/65),
where the maintainer described exactly this: the stack abstracts the quadruped as
an omnidirectional base, the controllers have no unified declarative capability
validation (an invalid velocity command can fail silently or destabilise the
platform), and the lowest-effort, non-intrusive fix is an intermediary URML node
that validates incoming intent against the base manifest and then emits a
standard `Twist`, with no change to the ros2_control stack.

```
upper layer ──intent──▶ URML node ──validate vs base manifest──▶ Twist ──▶ existing controller
(planner / LLM / teleop)              (RFC-0518 base bounds)        │
                                                                    └─reject──▶ no Twist, reason returned
```

## The base manifest (RFC-0518)

[`quadruped-base.manifest.yaml`](quadruped-base.manifest.yaml) declares the
bounds an upper-layer intent must respect, the base-level boundaries the
maintainer named:

- `max_velocity` (linear) and `max_angular_velocity` (yaw)
- `max_linear_acceleration`, `max_angular_acceleration`
- `max_traversable_slope_deg`, `max_obstacle_height_m`
- `max_payload`

These are base-level declarations. The whole-body internals stay private to the
controller; URML never reaches into them.

## What the node does

[`validate_base_intents.py`](validate_base_intents.py) reads the manifest through
URML's capability-manifest schema, then validates each base intent in
[`base-intents.yaml`](base-intents.yaml) against those bounds:

| Intent | Result |
|---|---|
| cruise_forward | DISPATCH → `Twist(1.0, 0.0)` |
| spot_turn | DISPATCH → `Twist(0.0, 0.8)` |
| drive_too_fast | REJECTED — `max_velocity (2.5 > 1.5)` |
| spin_too_hard | REJECTED — `max_angular_velocity (1.8 > 1.0)` |
| climb_too_steep | REJECTED — `max_traversable_slope_deg (40 > 25)` |
| overloaded | REJECTED — `max_payload (20 > 10)` |

An admissible intent becomes a `Twist` sent to the existing controller; an
inadmissible one is refused with the specific bound it broke, before anything
actuates. That is the declarative validation the controllers lack today, added
without touching the core stack.

## Run it

```bash
python examples/mobile-base/validate_base_intents.py
```

Validator-only, no ROS, no robot, and deterministic. The committed
[`base-intent-report.txt`](base-intent-report.txt) is byte-asserted by
`reference/validator/tests/test_base_intent_node.py`, so the example cannot drift
from the schema.
