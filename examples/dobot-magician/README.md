<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# An English front door for the Dobot Magician

A worked example of URML driving a Dobot Magician, the 4-axis desktop arm, through
the [magician_ros2](https://github.com/jkaniuka/magician_ros2) ROS 2 driver. It
came out of [magician_ros2#11](https://github.com/jkaniuka/magician_ros2/issues/11).

A request like "pick up the block and put it on the dropoff spot" becomes a typed
URML program. The validator checks it against the Dobot's declared manifest, its
taught locations, its gripper, and what its wrist camera can recognize, before
the arm moves.

`check_pick_place.py` validates the happy path, then shows the validator refusing
three programs the Magician cannot do:

- pick an object that is not in its vocabulary (`capability.missing_object_class`)
- move to a location it has not been taught (`capability.missing_location`)
- grasp with a force past the gripper's range (`capability.missing_gripper`)

```
python examples/dobot-magician/check_pick_place.py
```

Validator-only, no arm, deterministic. The committed `pick-place-report.txt` is
byte-asserted by `reference/validator/tests/test_dobot_example.py`, so the example
cannot drift from the validator.

## Files

- `dobot-magician.manifest.yaml` — the Magician's capability manifest (gripper, wrist camera, taught locations).
- `check_pick_place.py` — the generator.
- `pick-place-report.txt` — the recorded, byte-asserted output.

The manifest models a Magician with the wrist-camera accessory, so `pick_from` /
`place_at` resolve a detected object. A base unit without the camera does taught
coordinate moves; that is a `move_to` plus gripper sequence at known poses.
