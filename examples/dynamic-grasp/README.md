# Catch the ball: a grasp whose target refuses to sit still

A worked example for [RFC-0671](../../docs/rfcs/0671-dynamic-target-grasp.md). Catching a
thrown object is not a new primitive: it is a `grasp` with `target_motion: ballistic`. The
millisecond perception-prediction-closure loop is a runtime skill (an RFC-0383 learned
policy). What URML decides, on paper and before anything moves, is one thing: is this hand
on this robot **allowed to attempt** an interception at all?

That is the same shape as refusing a 250 N grasp on a 100 N gripper, applied to motion
instead of force.

## The declarations

A program marks a moving target:

```yaml
- grasp:
    target: $incoming_ball
    grasp_type: spherical
    target_motion: ballistic   # optional; default static
```

A gripper declares what it can intercept, with the numbers that make the claim honest:

```yaml
grippers:
  - name: phantom_hand
    kind: dexterous
    interception:
      modes: [tracked, ballistic]   # non-empty, from {tracked, ballistic}
      closing_time_ms: 80           # commanded-open to commanded-closed
      reaction_latency_ms: 40       # perception-to-actuation budget
      max_target_speed_m_s: 12.0    # optional
```

`interception` is not restricted to dexterous hands: a fast parallel-jaw gripper picking off
a moving conveyor is a legitimate `tracked` interceptor.

## Run it

```bash
python examples/dynamic-grasp/run_dynamic_grasp.py
```

It writes [`dynamic-grasp-report.txt`](dynamic-grasp-report.txt), byte-asserted in CI
(`reference/validator/tests/test_dynamic_grasp_example.py`). The report validates the same
catch program against three manifests:

| Manifest | Result |
|---|---|
| hand declares interception `[tracked, ballistic]` | **VALID**: the attempt is admissible |
| same hand, no `interception` block | **REJECTED** `capability.target_motion_not_supported` |
| gripper declares only `[tracked]` | **REJECTED** `capability.target_motion_mode_not_declared` |

## Honest altitude

URML admits or refuses the *attempt* on declared hardware; it never answers whether the catch
will succeed, and it validates no trajectory or timing. The declaration is trusted, not
verified, like every manifest field. At runtime the hand's `target_motion` reaches the adapter
(`send_manipulation_goal`) and is recorded in the audit; an interception substrate dispatches
on it, and a substrate that cannot ignores it, safe because the parameter is only ever set
after validation confirmed the declaration. No code is vendored from any hand vendor.
