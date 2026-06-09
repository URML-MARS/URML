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

# URML to Crazyswarm2 (a validated swarm)

A worked example: validate **one coordinated intent over a roster of Crazyflies**
with `validate_fleet`, then map each per-UAV primitive onto the real Crazyswarm2
interfaces. This is the concrete example from the Crazyswarm2 engagement
([IMRCLab/crazyswarm2#864](https://github.com/IMRCLab/crazyswarm2/discussions/864));
@whoenig confirmed Crazyswarm2 supports per-UAV position/velocity control and that
capabilities vary per drone, per area, and per swarm size, which is exactly what
URML's fleet model carries.

## What it does

[`urml_to_crazyswarm2.py`](urml_to_crazyswarm2.py) takes the
[`swarm-formation.fleet.yaml`](swarm-formation.fleet.yaml) mission (three
Crazyflies take off, fly a triangle, land, in lockstep) and:

1. **Validates the whole fleet first** with `validate_fleet`: every primitive
   against its member's manifest, plus the cross-robot checks. The load-bearing
   one is **deconfliction** — the three formation corners are checked against
   each Crazyflie's operational-clearance volume (RFC-0291). No command is
   emitted for a rejected program.
2. **Maps each validated per-UAV primitive** onto the real `crazyflie_interfaces`:

   | URML | Crazyswarm2 |
   |---|---|
   | `take_off: { altitude }` | `/<cf>/takeoff` (`crazyflie_interfaces/srv/Takeoff`) |
   | `move_to: { location }` | `/<cf>/go_to` (`crazyflie_interfaces/srv/GoTo`); low-level: the `Position` / `VelocityWorld` topics |
   | `land` | `/<cf>/land` (`crazyflie_interfaces/srv/Land`) |
   | `barrier` | a fleet rendezvous: the runtime holds the next phase until all members reach `completeState` (no per-UAV command) |

The fleet model maps cleanly onto Wolfgang's points: each Crazyflie is a **roster
member with its own manifest** (a Bolt and a stock CF can differ), the operating
area is the **clearance volume**, and the swarm size is just the **roster length**.

## Validation-first, demonstrated

Send two drones to the **same** corner and the program is rejected before a single
command goes out:

```
fleet program does not validate; no Crazyswarm2 command dispatched.
Errors: fleet.concurrent_shared_workspace
```

That is the difference from issuing setpoints directly: the conflicting swarm
intent never reaches the `go_to` services.

## Run it

```bash
python examples/fleet/crazyswarm2/urml_to_crazyswarm2.py   # regenerates dispatch-plan.txt
```

Pure Python stdlib + the URML validator (no ROS 2, no radios, no Crazyflies), and
deterministic: the committed [`dispatch-plan.txt`](dispatch-plan.txt) is
byte-asserted against the generator in CI
(`reference/validator/tests/test_crazyswarm2_dispatch.py`).

## Scope

The validated-fleet-intent to Crazyswarm2-interface mapping, not a live ROS 2
node. A real flight needs Crazyswarm2 + a positioning system; a live rclpy
dispatcher fanning the validated intent out to the per-CF service clients is the
natural next step. Single-robot siblings of this example: the esmini
([`examples/scenario/`](../../scenario/)) and ros2_kortex
([`examples/manipulation/kortex/`](../../manipulation/kortex/)) worked examples.
