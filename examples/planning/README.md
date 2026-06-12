# URML as the validating dispatcher for a PDDL planner, with replan feedback

A PDDL planner (ROSPlan, PlanSys2, ...) searches a symbolic domain for a plan.
URML sits **between the plan and the actuators**: it validates each grounded
action against the physical robot's capability manifest and the active safety
envelope before dispatch, and when an action is inadmissible it returns
structured feedback the planner consumes to replan.

This example comes from the
[ROSPlan engagement](https://github.com/KCL-Planning/ROSPlan/issues/330), where
@gerardcanal asked the three questions it answers:

```
PDDL domain ──plan──▶ grounded actions ──URML──▶ dispatch     (admissible actions only)
(symbolic model)                          (validate vs        │
                                           manifest+envelope)  └─reject──▶ replan-feedback ──▶ planner re-plans
```

## The three questions

1. **How does the capability layer relate to the PDDL domain?** The domain
   encodes what the robot can do *symbolically*, for search. URML's manifest +
   safety envelope is the *physical* layer: declared limits (force, reach,
   velocity) and the deployment-time safety contract (occupancy zones, geofence,
   grip-force cap). A plan can be valid in the domain and still inadmissible on
   the real robot. Here plan v1 is symbolically fine, but its route passes
   through `crowd_spot`, which lies inside the envelope's people-occupancy zone
   the domain never modeled.

2. **Is URML a dispatcher that checks validity?** Yes. It validates each grounded
   action against the manifest and envelope before dispatch and halts on the
   first inadmissible one. It is not a planner; it is the admissibility gate the
   plan passes through.

3. **What happens when validation fails?** It returns *structured* feedback: the
   rejected action, the failing validation pass, the error codes, and a directive
   the planner applies (forbid this action and replan). Without that feedback, as
   @gerardcanal noted, the planner would hand back the same plan.

## What the example shows

[`validate_and_replan.py`](validate_and_replan.py) dispatches
[`plan-v1.yaml`](plan-v1.yaml) action by action against
[`delivery.manifest.yaml`](delivery.manifest.yaml) and
[`safety-envelope.yaml`](safety-envelope.yaml):

| Action | Result |
|---|---|
| `(goto dock shelf)` | DISPATCH |
| `(pick mug shelf)` | DISPATCH |
| `(goto shelf crowd_spot)` | HALT — `envelope.occupancy_zone_intrusion` |
| `(goto crowd_spot user)` | not reached |

URML halts and emits the replan-feedback. The planner applies it (forbid the
crowd_spot transit) and re-plans via the safe `approach` waypoint;
[`plan-v2.yaml`](plan-v2.yaml) then validates clean and the whole plan
dispatches.

The point is the closed loop. URML does not plan and does not replace the PDDL
domain; it validates the plan against the real robot and hands back something the
planner can act on, so the next plan is different.

## Run it

```bash
python examples/planning/validate_and_replan.py
```

Hermetic (the validator only, no planner, no robot) and deterministic. The
committed [`replan-report.txt`](replan-report.txt) is byte-asserted by
`reference/validator/tests/test_replan_feedback.py`, so the example cannot drift
from the validator.
