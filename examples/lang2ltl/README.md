# Lang2LTL: a capability gate below the task spec

A worked example from a conversation with Prof. Stefanie Tellex about
[Lang2LTL](https://arxiv.org/abs/2302.11649) and where a declared-capability layer
sits relative to an LTL task specification.

A pipeline like Lang2LTL turns a natural-language command into a formal (LTL) task
spec: what to achieve, and in what order. That spec dispatches concrete actions to
a robot. URML sits one step below: it validates each dispatched action against the
robot's declared capability manifest and safety envelope before the action runs.
It does not author the task and does not compete with the LTL spec. It is the
admissibility check under it.

## Run it

```
python examples/lang2ltl/run_lang2ltl.py
```

The task is "go to the table, pick up the mug, place it on the counter," read as
the LTL-shaped goal `F(at_table & F(holding_mug & F(at_counter & placed)))`. It
dispatches the URML sequence `move_to table -> detect mug -> grasp -> move_to
counter -> release`, validated three ways.

## What it shows, honestly

Two limits of a declared-capability layer, and how URML handles each. Both were
raised by Prof. Tellex, and both are real.

1. **Necessary, not sufficient.** URML validates against a *declaration*, so an
   in-envelope action is not guaranteed to succeed in a new scene. What it buys
   cheaply is rejecting the *definitely-inadmissible* before a risky attempt. Case
   2 grasps at 250 N with a gripper rated to 100 N; URML refuses it statically,
   with no robot and no attempt (`envelope.force_exceeded`).

2. **A declared capability is not an actual one.** This is the sharper point: a
   robot claiming a capability often does not mean it works in reality.
   [RFC-0631](../../docs/rfcs/0631-capability-evidence-traceability.md) lets a capability record
   *how* its claim was established (`inferred < declared < derived < verified`),
   and a deployment policy can require a minimum. Under
   `verified-evidence.policy.yaml`, a gripper whose force range is only
   self-declared is refused (`policy.evidence_insufficient`, case 3), even though
   the action is within the declared range. URML does not take a capability on
   faith; a deployment can insist a claim be verified before it is trusted.

The committed `lang2ltl-report.txt` is byte-asserted in CI, so the example cannot
drift from what the validator actually does.

## What URML is not

It is not a general specification language, and it is not a promise that an
admissible action will succeed. It is the narrow, static admissibility gate below
the task spec: cheap to run, honest about its limits, and able to refuse an
unverified claim rather than trust it.
