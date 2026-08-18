# A URDF's own limits as a capability-manifest source

For [clemense/yourdfpy#69](https://github.com/clemense/yourdfpy/issues/69) (the liburdf JSON-emission thread).

A URDF already carries, per joint, the numbers a validate-before-actuate check
needs: effort, velocity, and position limits. This example reads a real URDF with
the Python standard library, takes the gripper finger joint's effort limit as a
grasp-force cap, builds a URML capability manifest around it, and validates a grasp
against that cap.

## What it shows

`simple_arm.urdf` declares three joints with limits. The parallel-jaw finger joint
carries `effort="185.0"`, and that becomes the gripper's force cap:

| URDF | URML |
|---|---|
| `left_finger_joint` `<limit effort="185.0">` | `manipulation.grippers[0].force_max_n = 185.0` |

Then two grasps against that cap:

1. **Admissible**: a grasp at 60 N validates (within the 185 N cap sourced from the URDF).
2. **Refused**: a grasp at 250 N is rejected with `envelope.force_exceeded`, before the
   gripper closes, on the limit the URDF itself declared.

## Run it

```bash
python examples/urdf-to-manifest/run_urdf_to_manifest.py
```

Hermetic and deterministic (stdlib XML + the validator, no ROS, no robot). The
committed [`urdf-to-manifest-report.txt`](urdf-to-manifest-report.txt) is
byte-asserted in CI.

## The point (and the liburdf connection)

The mapping is the point, not the parser. A URDF gives you kinematics and limits, not
deployment context: frames, object classes, and provenance are things the URDF does
not carry, so they stay authored. What the URDF *does* carry, the effort / velocity /
position limits, is exactly the admissibility half of a capability manifest.

That is why the [liburdf](https://github.com/wissem01chiha/liburdf) direction is
useful here. A tool that reads a URDF and emits its limits as JSON with explicit units
would make the limit half of this mapping automatic, for any validate-before-actuate
layer, not just URML. This example does the extraction by hand with the standard
library to show the shape; a clean JSON emission would replace that step.

URML reads the limits and checks a command against them. It does no kinematics, no
motion planning, and no control.
