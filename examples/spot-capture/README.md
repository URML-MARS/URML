# Selecting the camera a capture shoots with, checked before dispatch

For the rai-opensource spot_ros2 conversation ([Discussion #805](https://github.com/rai-opensource/spot_ros2/discussions/805)).

A Boston Dynamics Spot carries five fixed body fisheyes and one movable hand
camera. A program that says "photograph that valve" means the hand camera: a
fixed fisheye cannot be pointed at a subject. This example shows how URML's
`capture` primitive names the camera, and checks the choice statically, before
any command reaches the robot.

## The gap this closes

Before [RFC-0699](../../docs/rfcs/0699-capture-camera-selector.md), `capture` had
no way to name a camera. A targeted capture validated as long as *any* declared
camera was movable, so a program that named the wrong camera, or meant a specific
one, passed the static gate. On a robot with six cameras that is a real hole, and
it was called out as an honest caveat in the Spot Arm manifest.

RFC-0699 adds an optional `camera` selector naming a declared `perception.cameras`
entry, and scopes capture's existing checks (mode support, movable-for-target) to
that one camera. Omitting it keeps the old any-eligible-camera behavior, so
existing programs are unaffected.

## What it shows

The manifest declares the Spot Arm camera set: five fixed photo-only fisheyes and
one movable photo+video hand camera (`hand_color`). The runner validates three
programs against it, hermetically (validator only, no ROS, no robot):

| Program | Result |
|---|---|
| `capture(camera: hand_color, target: $subject)` | **VALID**: hand_color is movable and supports photo |
| `capture(camera: chest_cam)` | **REJECTED** `capability.missing_camera`: no such declared camera |
| `capture(camera: frontleft_fisheye, target: $subject)` | **REJECTED** `capability.fixed_camera_target`: that fisheye is fixed, even though the movable hand_color exists |

The third case is the motivating one from #805: before RFC-0699 it validated
against the movable `hand_color`, so naming the wrong camera passed.

## Run it

```bash
python examples/spot-capture/run_spot_capture.py
```

It writes [`spot-capture-report.txt`](spot-capture-report.txt), which is
byte-asserted in CI (`reference/validator/tests/test_spot_capture_example.py`), so
the example can never drift from the tool.

## Honest altitude

URML validates the intent against the declared manifest before dispatch. The
per-robot adapter still drives the actual camera (a Spot SDK image request, a ROS
`image_transport` topic). URML does not take the picture; it refuses an intent that
names a camera the robot does not have, or asks a fixed camera to frame a subject.
No code is vendored and there is no dependency on `spot_ros2`.
