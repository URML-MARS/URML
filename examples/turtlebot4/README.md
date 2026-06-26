# URML on a TurtleBot 4 (ROS 2, Nav2)

The worked example from [Discussion #526](https://github.com/URML-MARS/URML/discussions/526),
where [@slowrunner](https://github.com/slowrunner) asked how a ROS 2 robot maps
onto URML. His Dave is a ROS bot and his WaLI is a TurtleBot 4 clone, so this is
the shape for that family.

A TurtleBot 4 is **mapped**: it knows where it is in a `map` frame, so its natural
verb is `move_to` a named pose. The ROS 2 reference runtime lowers that to a Nav2
`NavigateToPose` goal. (The frameless GoPiGo3, by contrast, drives by amount with
`drive` / `turn`, [RFC-0630](../../docs/rfcs/0630-relative-motion-primitive.md).)

- [`turtlebot4.manifest.yaml`](turtlebot4.manifest.yaml) — a TB4-class mobile base
  with named Nav2 goals (`kitchen`, `living_room`, `charging_dock`) and a camera.
- [`run_turtlebot4.py`](run_turtlebot4.py) — validates a short errand (`move_to`
  the kitchen, take a photo, report) and executes it hermetically through
  `MockROSAdapter`. On a real TB4 the same validated program runs through the ROS 2
  `RclpyAdapter`, which lowers `move_to` onto Nav2.

```
[VALID] move_to kitchen, capture a photo, report.
  move_to kitchen      -> send_navigation_goal(location='kitchen')  [Nav2 NavigateToPose]
  capture photo        -> capture_media(media='photo')
  report               -> emit_report(to='run_log')
```

Run it:

```sh
python examples/turtlebot4/run_turtlebot4.py
```

Deterministic and byte-asserted in [`turtlebot4-report.txt`](turtlebot4-report.txt)
by `reference/validator/tests/test_turtlebot4_example.py`.

## Where the Nav2 knobs live

The URML program is just `move_to { location: kitchen }`. A real Nav2 deployment
also tunes goal tolerance, a rotation-shim trigger angle, pause-for-moving-obstacles,
and replan-vs-plan-once. Those are **Nav2 concepts**, so they live in the ROS 2
adapter's deployment config, not in the URML program. Baking them into `move_to`
would make `move_to` unimplementable on a frameless GoPiGo3, which is the
leaky-primitive failure mode URML avoids by construction. Keeping the primitive
substrate-neutral is what lets one program run on a GoPiGo3, a drone, or this TB4.

Navigation telemetry (duration, number of recoveries, time in recoveries) comes
back in the run report; a neutral, runtime-filled shape for that is scoped in
[RFC-0638](../../docs/rfcs/0638-execution-lifecycle-and-run-report.md), which also
covers cancel and progress.
