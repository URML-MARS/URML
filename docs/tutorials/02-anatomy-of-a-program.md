# Tutorial 2 — Anatomy of a URML program

**By the end of this tutorial you will:**

- Understand the five-layer architecture URML organises itself around.
- Be able to read every line of the canonical red-mug program and explain what it does.
- Know what a variable binding (`$ref`) is and how it flows between primitives.

This tutorial assumes you completed [Tutorial 1](01-getting-started.md) and have a `my-first-robot/` directory with a passing program. We'll walk through that program from top to bottom.

## The 30-second mental model

URML organises itself as five layers, top to bottom:

```
Layer 4   Natural-language interface     "Bring me the red mug from the kitchen."
Layer 3   Behavior composition           sequence / branch / parallel / retry
Layer 2   Intent primitives              move_to, detect, grasp, release, ...
Layer 1   Hardware abstraction           manifest: declared locations, sensors, grippers
Layer 0   Substrate                      ROS 2, PX4, OPC UA, vendor SDK — NOT part of URML
```

A complete URML *program* lives at Layers 2 + 3 (intent primitives composed into a behavior). The *manifest* lives at Layer 1. The *natural-language request* lives at Layer 4. The runtime translates everything down to Layer 0 — whatever robot OS is actually running on the robot.

You don't need to memorize this. The point is that each layer has one job, and a change at one layer doesn't ripple through the others.

## The program

Open `my-first-robot/program.urml.yaml`. It looks like this:

```yaml
profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - move_to:
        location: kitchen
    - detect:
        object: mug
        attributes:
          color: red
        store_as: target_mug
    - grasp:
        target: $target_mug
        force: gentle
    - move_to:
        location: user
        carrying: $target_mug
    - release:
        mode: hand_to_user
```

That's the entirety of *"bring me the red mug from the kitchen"* in URML. Let's read it.

## The `profile` line

```yaml
profile: home
```

This is the **profile** the program targets. Profiles are domain-specific extensions to the core URML vocabulary — `home`, `drone`, `industrial`, and so on. A profile may add primitives, constrain core primitives, or declare extra safety-envelope requirements. The validator uses the profile to decide which constraints to apply.

In Tutorial 1's manifest, the home profile mostly means: civilian indoor robots, gentle force defaults, no aerial concepts. Drone-profile constraints (altitude caps, geofencing, weather thresholds) don't apply here.

## The `behavior` tree

```yaml
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - ...
```

A URML program has exactly one top-level `behavior`. The `type` tells the runtime how to *compose* the steps inside:

- **`sequence`** — do steps in order, top to bottom. (Used here.)
- **`branch`** — `if condition then if_true else if_false`.
- **`parallel`** — run multiple sub-behaviors at once; the `complete_when` field decides what *done* means.
- **`retry`** — keep running the inner behavior up to `max_attempts` times.

You can nest these freely. A `parallel` containing two `sequence`s containing a `retry` is fine. The validator statically checks the whole tree before any step runs.

`on_error: abort_and_report` says *if any step fails, stop the sequence and tell the caller why*. The other option is `continue`, which absorbs the failure and moves on.

## The first step

```yaml
- move_to:
    location: kitchen
```

This is a **Step**, and `move_to` is its **primitive** — one of the twelve verbs URML defines at Layer 2. The verb's arguments are everything underneath. Here, `location: kitchen` says *move to the place named `kitchen`*.

The validator does several checks on this single step:

1. **The manifest declares mobility.** Check: yes, the scaffolded manifest has a `mobility` block.
2. **`kitchen` resolves in the manifest's declared locations.** Open `manifest.yaml` and look at `declared_locations` — yes, `kitchen` is there with `pose: { x: 3.2, y: 1.0 }`.
3. **The envelope's velocity cap allows the runtime to move.** The scaffolded `envelope.yaml` caps velocity at 0.4 m/s, manifest allows 0.46 m/s. Fine.

If any of those failed, the validator would reject the program with a stable `capability.*` or `envelope.*` error code (you saw `capability.missing_location` in Tutorial 1).

## The detection step

```yaml
- detect:
    object: mug
    attributes:
      color: red
    store_as: target_mug
```

`detect` asks the robot's perception pipeline to find an object matching the criteria. Three fields:

- **`object: mug`** — the class to look for. The validator checks that `mug` is in the manifest's `perception.object_vocabulary`.
- **`attributes: {color: red}`** — narrow the search. Optional.
- **`store_as: target_mug`** — give the result a name we can reference later.

That `store_as: target_mug` is the load-bearing part. URML programs have **variable bindings**: a primitive can store its result under a name, and subsequent primitives can reference that name via `$target_mug`.

When this step runs, the bound value looks something like:

```yaml
target_mug:
  class: mug
  pose: { x: 3.5, y: 1.1, z: 0.8 }
  frame: map
  attributes: { color: red }
  confidence: 0.95
```

— a structured object describing what was found.

## The grasp step

```yaml
- grasp:
    target: $target_mug
    force: gentle
```

`grasp` closes a gripper on the bound target. The `$target_mug` syntax is a **reference** — the runtime resolves it to the actual object dict from the previous step before calling the substrate. (So the underlying ROS 2, PX4, or OPC UA adapter sees concrete data, not URML syntax. That separation is by design — see RFC-0002 §Detailed Design.)

`force: gentle` is profile-aware: the home profile interprets `gentle` as ~1.5 N (calibrated so an inadvertent contact with a person yields). The envelope's `max_grip_force_n: 3.0` further constrains this — even if you asked for `force: 8.0`, the validator would reject the program before execution.

## The second move

```yaml
- move_to:
    location: user
    carrying: $target_mug
```

Another `move_to`, but with a new field: `carrying: $target_mug`. This tells the runtime *the robot is transporting this object*. The substrate can use that to plan trajectories with the carried object's footprint in mind, or to report which object reached which destination.

The reference is again resolved to the concrete object data before reaching the substrate. The runtime, validator, and substrate all see the same target_mug payload.

## The release step

```yaml
- release:
    mode: hand_to_user
```

`release` opens the gripper. The `mode` field is mandatory: `drop` (let it fall), `place` (set it down with explicit `at:` location), or `hand_to_user` (present the object and wait for the user to take it).

`hand_to_user` is the home-profile-appropriate mode here. If you tried `mode: place` without `at: ...`, the validator would reject the program — that's a cross-field rule encoded in the Layer-2 schema for `release`.

## Where the layers ended up

Re-read the program with the layers in mind:

```yaml
profile: home                       # Profile (which constraints apply)
behavior:
  type: sequence                    # Layer 3 (composition)
  on_error: abort_and_report
  steps:
    - move_to: { location: kitchen }            # Layer 2 (primitive)
    - detect: { ..., store_as: target_mug }     # Layer 2, with a binding
    - grasp: { target: $target_mug, ... }       # Layer 2, with a reference
    - move_to: { location: user, carrying: ... }
    - release: { mode: hand_to_user }
```

Every named field in this program has its meaning checked against **Layer 1** (the manifest):

- Locations (`kitchen`, `user`) must be declared.
- Object classes (`mug`) must be in the perception vocabulary.
- Force levels (`gentle`) must fit a declared gripper's force range.

And against the **envelope** (deployment-level safety overlay):

- Velocity must be at or below the envelope's cap.
- Force must be at or below the envelope's cap.
- Geofences and people-occupancy zones must not be violated.

That's the validator's job: take the program plus the manifest plus the envelope, and accept or reject before any actuator moves.

## What about Layer 0?

Layer 0 — the actual robot operating system (ROS 2, PX4, OPC UA, vendor SDK) — is **outside URML**. The reference runtime translates each primitive into substrate-specific calls when the program executes:

- `move_to: { location: kitchen }` → on ROS 2, a Nav2 `NavigateToPose` action with the manifest-resolved pose for `kitchen`.
- `grasp: { target: $target_mug }` → on ROS 2, a MoveIt 2 `MoveGroup` plan with a configured gripper command.

The translation lives in `reference/ros2-runtime/`. On Windows or Linux without ROS 2 installed, you can still exercise the runtime against a hermetic mock substrate (`MockROSAdapter`) — useful for testing programs end-to-end without a robot. We'll see that in Tutorial 3.

## What you have now

A working mental model of the layered architecture, the difference between primitives and composition, and how variable bindings flow between steps. That's most of what you need to read any URML program.

## Next

[Tutorial 3: Natural language to URML](03-natural-language-to-urml.md) — let an LLM produce URML for you, with the validator-feedback revision loop in action.

Or jump straight to [Tutorial 4: Writing your own manifest](04-writing-your-own-manifest.md) if you want to describe your own robot rather than the scaffolded TurtleBot.
