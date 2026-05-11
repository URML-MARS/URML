# Industrial Profile

**Status:** Pre-draft. v1.0 target; third profile to ship. See roadmap in [`MANIFESTO.md`](../../../MANIFESTO.md).

## Application domain

Single-arm manipulators and mobile bases operating in **controlled industrial cells**: pick-and-place stations, line stations, kitting cells, small-batch reconfiguration. The defining shape of the industrial profile is *predictable physical environment, well-defined safety perimeter, semi-trained operators reconfiguring tasks without re-programming the PLC*.

## In scope

- **Pick-and-place** with declared object types and bins.
- **Line reconfiguration** by a line manager via natural language — "same as before, but pick red instead of blue, and slow down by twenty percent." The canonical industrial example in [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Industrial: the line reconfiguration*.
- **Kitting** — assembling sets of components.
- **Light assembly** within force/torque limits the cell declares.
- **Mobile base operation within a declared cell perimeter** — pallet transport, station-to-station moves.
- **Safety-door-gated motion** — a mandatory interlock where the cell's safety perimeter being open halts motion.

## Out of scope

- **Welding, painting, machining**, and other process-specialized tasks at v1.0. These are domain-specialized enough to merit their own profiles or to live outside the canonical maintenance scope.
- **Multi-arm coordination** at v1.0. Compose with multiple single-arm cells instead; explicit dual-arm coordination is a v1.x stretch.
- **Heavy-payload manipulation** beyond a declared cell ceiling.
- **Outdoor or human-shared-floor mobile operation.** Industrial mobile bases in this profile operate within a declared cell perimeter, not in mixed-traffic warehouse aisles. Mixed-traffic warehouse operation is plausibly its own profile.

## Safety envelope class

An industrial cell operates with **trained operators, a declared physical perimeter, and explicit interlocks**. The default safety envelope:

- **Cell perimeter** declared as a polygon (or set of polygons) — motion is rejected if the program's declared targets fall outside.
- **Safety-door interlock** declared in the manifest — when the door is open, all motion halts. The runtime is expected to honor this regardless of program state; the validator only checks that programs don't *require* motion-with-door-open.
- **Force ceilings** per gripper, declared in the manifest. Grasps that exceed the ceiling are rejected.
- **Velocity ceilings** that may be lowered by deployment (the *"slow down by twenty percent"* example exercises exactly this).
- **No motion in declared people-occupancy moments** — e.g., during manual loading windows the operator declares.

## Required manifest fields

When this profile is drafted, the capability manifest of an industrial-profile-conformant cell will be required to declare at least:

- Arm count (1 in v1.0), DOF, reachable workspace.
- Gripper(s): type, force range, accepted object classes.
- Mobile base (if any): drive type, declared cell perimeter, max velocity.
- Perception: cameras, object-detection model alignment with the declared object vocabulary.
- Cell perimeter polygon.
- Safety-door interlock declarations.
- Declared object vocabulary (`widget_blue`, `widget_red`, etc.) so the validator can verify that referenced objects are known.

## Layer-2 primitives this profile adds

To be defined. Likely candidates: `pick_from(source: bin | conveyor | pallet)`, `place_at(target: bin | fixture | station)`, possibly a `wait_for(interlock_state)` for handoffs with PLC-controlled equipment.

## Layer-2 primitives this profile constrains

- `move_to` must declare frame and target pose; named-location vocabulary is the cell's declared station list.
- `grasp.force` must be at or below the gripper's declared force ceiling.

## Conformance points

When this profile is drafted, the conformance suite will include:

- End-to-end test of the *line-reconfiguration* scenario (re-color, slow-down).
- Negative tests that the validator rejects programs that violate the cell perimeter, exceed force ceilings, or require motion while the safety-door interlock is open.
- Tests that natural-language re-parameterization ("slow down by twenty percent") produces the expected URML diff against a stored prior program.

## Related documents

- [`/docs/architecture.md`](../../../docs/architecture.md) §Profiles.
- [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Industrial: the line reconfiguration*.
