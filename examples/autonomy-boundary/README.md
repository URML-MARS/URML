# URML in the mind of an autonomous robot

The worked answer to [Discussion #526](https://github.com/URML-MARS/URML/discussions/526):
where does URML sit in an autonomous robot, and where does it not?

The scenario is the patrol @slowrunner described: during activity hours, if the
battery is over 50%, wander the allowed area, stop when an unclassified shape is
seen, photograph it from several angles, and store the photos tagged with time
and pose.

The boundary this example draws:

- **The mastermind (autonomy) decides.** A planner, a behavior tree, a policy, or
  your own Python owns *when* to patrol (hours + battery), *where* to wander,
  *whether* a shape is novel and unclassified, and *storing* the tagged photos.
  URML expresses none of this. Deciding that something is a not-yet-classified
  shape is open-set perception, which is a mastermind judgment.
- **URML validates and executes each physical action.** Every concrete move the
  mastermind decides on becomes a URML step, checked against the robot's manifest
  before it runs: `drive`, `turn`, `capture`.

[`autonomy_patrol.py`](autonomy_patrol.py) plays a plain-Python `Mastermind`
through one patrol and validates every physical action it issues as a URML step,
then executes the whole patrol through the mock substrate. It also shows the
boundary the other way: when the mastermind tries to push its perception judgment
*down* into URML as a `detect`, the validator refuses it.

```
  [VALID]  turn +30 deg
  [VALID]  drive 0.50 m
  [VALID]  capture photo (current view)
  ...
    detect(object: unclassified_shape)  ->  [REJECTED] capability.missing_object_class
    novelty detection is not a declared capability; it stays in autonomy.
```

Run it:

```sh
python examples/autonomy-boundary/autonomy_patrol.py
```

The output is deterministic and byte-asserted in
[`autonomy-boundary-report.txt`](autonomy-boundary-report.txt) by
`reference/validator/tests/test_autonomy_boundary_example.py`.

The point: the mastermind can be as clever as it likes, and the robot still only
does what the manifest declares and the safety envelope allows. URML is the
checkable seam between an open-ended autonomy stack and a physical machine.
