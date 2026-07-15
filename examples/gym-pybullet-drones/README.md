# gym-pybullet-drones: a validate-before-actuate gate

A worked example for
[learnsyslab/gym-pybullet-drones#312](https://github.com/learnsyslab/gym-pybullet-drones/discussions/312).

@JacopoPan noted the repo's design driver is KISS, so this is deliberately frugal
and **adds nothing to gym-pybullet-drones**: it imports nothing from that repo,
and that repo imports nothing from URML. The gate lives entirely on the URML side.

URML declares what the quadcopter can do (`quadcopter.manifest.yaml`: an aerial
multirotor with a service ceiling and a speed limit) and a deployment declares the
arena it may fly in (`arena.envelope.yaml`: a 3 by 3 m box with a 2.5 m altitude
cap). A commanded flight is validated against both before any target is handed to
the gym-pybullet-drones control interface.

## Run it

```
python examples/gym-pybullet-drones/run_gym_pybullet_drones.py
```

The flight is minimal: take off, go to a waypoint, land. It is validated three
ways:

1. **Admissible** (inside the arena, under the cap): accepted.
2. **Too high**: a 3.0 m take-off is within the 5 m service ceiling but above the
   arena's 2.5 m cap, so the envelope refuses it (`envelope.altitude_exceeded`).
3. **Out of bounds**: a waypoint outside the 3 by 3 m box is refused
   (`envelope.geofence_violation`).

Only the admissible flight is mapped onto control targets: each primitive becomes
a `target_pos` for a gym-pybullet-drones position controller (for example
`DSLPIDControl.computeControlFromState(state, target_pos)`), which the env turns
into motor RPMs and steps. The committed `gym-pybullet-drones-report.txt` is
byte-asserted in CI.

## The shape, if you ever want it upstream

The whole thing is one small script and two YAML files, and it changes nothing in
gym-pybullet-drones. If a gate like this is useful, the natural upstream form is a
thin wrapper that a user opts into: validate the target against a manifest and
envelope, and only on success call the controller as usual. If it is not useful,
it costs the project nothing, because it lives here.
