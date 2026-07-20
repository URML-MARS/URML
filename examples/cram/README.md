# CRAM: a validate-before-actuate gate below the decomposition

A worked example from a conversation with the
[CRAM](https://cram-system.org/) group (University of Bremen, Institute for
Artificial Intelligence) about where a declared-capability check sits relative to a
cognitive architecture.

CRAM takes an underspecified request and decomposes it into a plan of grounded
sub-actions, resolving the open parameters at runtime from its knowledge base
(KnowRob). URML sits one step below that decomposition: it validates each grounded
sub-action against the robot's declared capability manifest and safety envelope
before the sub-action is dispatched. It does not plan, and it does not compete with
the decomposition. It is the admissibility check under it.

## Run it

```
python examples/cram/run_cram.py
```

The request is a CRAM `transporting` designator, roughly

```
(an action (type transporting) (object (an object (type mug)))
          (target (a location (on counter))))
```

which decomposes into the grounded sub-action sequence `move_to table -> detect mug
-> grasp mug -> move_to counter -> place`, validated three ways.

## What it shows, honestly

URML validates a *declaration*, so an in-envelope sub-action is not guaranteed to
succeed in a novel scene. What it buys cheaply is rejecting the
*definitely-inadmissible* grounded sub-action before the robot commits to the plan.
Two flavors of that, both caught before dispatch:

1. **An out-of-envelope grounded parameter.** CRAM can ground a firm grasp whose
   force is above the gripper's rated range. Case 2 grasps at 250 N with a gripper
   rated to 100 N; URML refuses it statically, no robot and no attempt
   (`envelope.force_exceeded`).

2. **A grounded object the robot cannot perceive.** CRAM's knowledge base can
   resolve a request to an object class the robot's perception vocabulary does not
   declare. Case 3 grounds a `tray` when the vocabulary knows only `mug`; URML
   rejects the grounded `detect` before the plan runs
   (`capability.missing_object_class`), rather than discovering the gap
   mid-execution.

The example runs policy-free (`policy=None`): it is about the capability and
safety-envelope gate, not federal compliance, which is a separate and orthogonal
concern. The committed `cram-report.txt` is byte-asserted in CI, so the example
cannot drift from what the validator actually does.

## What URML is not

It is not a planner, and it is not a promise that an admissible sub-action will
succeed. It is the narrow, static admissibility gate below the decomposition: cheap
to run, honest about its limits, and able to reject a grounded sub-action the robot
demonstrably cannot perform before the robot moves.
