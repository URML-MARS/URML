<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# Claim your robot's fleet name

The lightest way to get a robot into the URML world — lighter than building an adapter,
lighter than running the conformance suite. You publish a small, self-declared manifest;
your robot gets a **name** that any URML fleet program can address with `on:` and
synchronize with `barrier:` (see [RFC-0286](../../docs/rfcs/0286-multi-robot-fleet-addressing.md)).

No code. No integration. One YAML file you write and own.

## What a claim *is*

- A robot's `robot_id` becomes its **fleet name** — the handle a roster binds and an `on:`
  scope addresses.
- The manifest declares, abstractly, what the robot can do, so a fleet author knows whether
  it can move, manipulate, or perceive, and whether it can rendezvous at a barrier.
- It is **self-declared**, **opt-in**, and **de-listable at any time** — exactly like the
  manufacturer directory. You publish it; you can withdraw it.

## What a claim is **not**

- **Not an endorsement** — not URML endorsing your robot, and not you endorsing URML. A
  published manifest is a capability declaration, nothing more.
- **Not a certification or a compatibility mark.** Those are separate, later, and earned.
- **Not "engaged."** Claiming a name does not make you a partner or imply a relationship.
  URML's outreach ledger tracks real engagement separately and honestly; a claim is just a
  claim.
- **Not us naming your product for you.** We never list a robot a vendor has not published
  themselves. The claim is yours to make and yours to revoke.

## The minimal fleet-ready manifest

The smallest manifest that makes a robot a usable fleet member: a name, at least one
capability, and a `peer_link` so it can synchronize at a barrier. Copy this, fill it in,
delete what doesn't apply:

```yaml
manifest_version: "0.1"
robot_id: your_robot_name        # <- this is your fleet name (snake_case)
description: One line about the robot.

frames:
  - name: base

# Declare AT LEAST ONE capability so the robot can do something in a fleet.
# Pick the block(s) that fit; delete the rest.

mobility:                        # if the robot moves
  drive_type: differential       # differential | omnidirectional | ackermann | tracked |
                                 #   multirotor | fixed_wing | vtol | manipulator_base |
                                 #   underwater_thrusters | quadruped | biped
  max_velocity: 1.0              # m/s

# manipulation:                  # if the robot has an arm/gripper
#   arm_count: 1
#   grippers:
#     - { name: gripper, kind: servo_electric, force_min_n: 1.0, force_max_n: 50.0 }

# perception:                    # if the robot senses
#   cameras: [{ name: cam }]
#   object_vocabulary: [widget]

# Declare peer_link so your robot can rendezvous with others at a fleet barrier:
connectivity:
  links:
    - role: peer_link
```

Validate it before you submit:

```bash
pip install urml-validator
urml validate --manifest your_robot_name.manifest.yaml --no-policy
```

(`--no-policy` skips the US-federal provenance pass; add a `provenance:` block later if you
want to pursue the compliance path too. A claim does not require it.)

## How to claim

Pick whichever is least friction for you:

1. **Open a pull request** adding `your_robot_name.manifest.yaml` under `examples/fleet/claims/`
   (the directory is created by the first claim). One file, your robot, your name.
2. **Or self-host** the manifest anywhere public and open an issue pointing us at the URL —
   we link to it, you keep ownership.

Either way the manifest stays yours; withdraw it and the name is released.

## Why bother before building an adapter

A claimed name is a hook other people can pull on. An integrator assembling a fleet can
reference your named robot in a program today, then come to you with a concrete request:
*"your robot is URML-nameable and I want it in this fleet — will you ship the adapter?"*
That pull is easier to answer than a cold ask, and it starts with nothing more than a name.

## See also

- [RFC-0286](../../docs/rfcs/0286-multi-robot-fleet-addressing.md) — fleet addressing and the roster.
- [Fleet demo](README.md) — the courier-to-arm handoff a claimed robot could join.
- The full manifest schema: `urml schema manifest`.
