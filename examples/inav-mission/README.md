# URML mission intent, validated, compiled to an INAV waypoint mission

State a mission in plain intent ("fly over to the water tower, then come back and
land; don't cross the road"), check the aircraft can fly it within its
constraints, and compile the result into an INAV waypoint mission. URML does the
declaring and the checking; INAV does the flying.

This example comes from the
[iNavFlight/inav engagement](https://github.com/iNavFlight/inav/issues/11651),
where the maintainer restated the role exactly: a human or LLM states the goal
and the constraints (geofence, limits), URML checks the aircraft's capabilities,
and compiles to an INAV mission. He also pointed at two things a real check
should use: physical limits like minimum turn radius, and INAV capabilities like
return-to-home.

```
"fly to the water tower and back, don't cross the road"
        │
        ▼
   URML program ──validate vs manifest + geofence──▶ admissible ──▶ INAV waypoint mission
   (take_off / move_to / return_to_home / land)        │              (WAYPOINT / RTH / LAND)
                                                        └─reject (leg crosses the road) ──▶ nothing compiled
```

## What the example shows

[`compile_inav_mission.py`](compile_inav_mission.py) validates each mission in
[`missions.yaml`](missions.yaml) against [`inav-aircraft.manifest.yaml`](inav-aircraft.manifest.yaml)
and [`mission.envelope.yaml`](mission.envelope.yaml), then compiles the admissible
one:

| Mission | Result |
|---|---|
| water_tower_and_back | COMPILED → `WAYPOINT` + `RTH` + `LAND` |
| across_the_road | REJECTED — `envelope.geofence_violation` (nothing compiled) |

`return_to_home` maps to INAV's **RTH**; `move_to` becomes a **WAYPOINT**;
`land` becomes **LAND**. The "don't cross the road" rule is a **geofence** (the
operating area is the field on this side of the road); the validator's Pass 3
catches a waypoint on the far side before any INAV command is emitted. The
aircraft is declared a drone substrate with `autopilot_class: custom` +
note (INAV is not in the px4/ardupilot enum, RFC-0250).

## The open design question: minimum turn radius

The maintainer's turn-radius point is the right next step and is **not** modeled
here yet. Minimum turn radius is a fixed-wing kinodynamic limit (an INAV
setting); URML's manifest declares `max_velocity` and `service_ceiling` but no
turn radius. The natural home is an aerial-kinodynamic field on `mobility`,
parallel to RFC-0518's base-mobility bounds (`max_angular_velocity`,
`max_linear_acceleration`, ...). With it declared, the validator could reject a
mission whose leg-to-leg geometry is tighter than the aircraft can fly, before
compile. That is a Spec RFC to design against a real INAV setup, not something to
invent unilaterally; flagged here as the seam.

## Run it

```bash
python examples/inav-mission/compile_inav_mission.py
```

Validator-only, no flight controller, deterministic. The committed
[`inav-mission-report.txt`](inav-mission-report.txt) is byte-asserted by
`reference/validator/tests/test_inav_mission.py`.
