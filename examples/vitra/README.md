# VITRA: one action, two robots, two verdicts

A worked example for [microsoft/VITRA#41](https://github.com/microsoft/VITRA/issues/41).

VITRA is a vision-language-action model pretrained on human-activity video. Like
any VLA, it emits a manipulation action for a target robot. What a human
demonstrated, or a policy produced, is not automatically admissible on the
specific robot that will execute it: the arm may not be rated for the commanded
grip force, the object may be out of reach, the workspace may be smaller.

This example checks the same policy-emitted action against two robots and shows
one admissible, the other refused, decided statically and with no ROS.

## Run it

```
python examples/vitra/run_vitra.py
```

It validates one grasp action (grasp a workpiece at 150 N, then place it) against
two manifests that differ only in the gripper's declared force range:

- **Robot A** (`robot-a.manifest.yaml`), gripper rated 50 to 250 N: the 150 N
  grasp is within envelope, so the action is admissible.
- **Robot B** (`robot-b.manifest.yaml`), gripper rated 10 to 100 N: the same
  150 N grasp is above the range, so it is refused, with `capability.missing_gripper`
  and `envelope.force_exceeded`.

The output is committed as `vitra-report.txt` and byte-asserted in CI, so the
example cannot drift from what the validator actually does.

## What this shows, and what it does not

The action is validated against a declaration, before dispatch, off to the side
of any planner or controller. The same policy output earns a different verdict
per robot from one manifest each. That portability is the distinction from a
ROS-bound, single-robot, runtime mechanism:

- URML is a specification, not a ROS library. The same manifest and validator
  apply whether the target runs ROS 2, PX4, a vendor SDK, or bare firmware. It
  runs fully offline, with no planner or controller in the loop.
- The check is static and pre-dispatch. It answers "is this action admissible
  for this specific robot at all," at the policy-output boundary.

URML does **not** plan the motion, solve collisions against a live scene, or run
on the robot. Those are the job of MoveIt, a Pinocchio-based controller, or the
ROS 2 safety components, at execution time. URML is the layer above them: the
declarative admissibility gate a VLA's output passes through first. A real
deployment uses both.

This example uses gripper force as the single deciding axis because it is
concrete and fully enforced today. Reach, payload, and keep-out envelopes extend
the same idea: one declared contract per robot, checked against the action a
policy emits.
