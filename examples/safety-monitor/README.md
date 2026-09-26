# Declare a safety property, check it before dispatch, monitor it at run time

A worked example for [RFC-0382](../../docs/rfcs/0382-monitorable-temporal-logic-envelope.md),
URML's "validate then monitor" safety story. A deployment envelope declares
runtime-monitorable temporal properties over the robot's signals, and URML does two
things with them:

1. **Validate, before dispatch.** The validator parses each property and resolves its
   signals against the manifest at Pass 3. A malformed expression, or one that references
   a signal the robot cannot sense, is refused with a typed code before anything runs.
2. **Monitor, at run time.** The same property is evaluated over a trace of signal samples.
   URML ships the evaluator (`urml_validator.monitor`); the ros2 shield
   (`ShieldedAdapter`) or `urml validate --rehearse` uses it to catch a violation and block
   a critical one. URML declares the property and provides the checker and the evaluator; it
   does not itself drive the robot.

## The property

The headline property, on a home robot that shares space with people:

```yaml
monitorable_properties:
  - name: slow_near_people
    severity: critical
    expression: "always (person_distance < 2.0 implies speed <= 0.3)"
```

Never move faster than 0.3 m/s while a person is within 2 m. The envelope also declares
`bounded_stop` (a stop request brings the robot to rest within half a second), which
references the manifest's declared `stop_requested` event.

Signals a property may reference: the built-ins `speed`, `altitude`, `payload`,
`grip_force`, `person_distance`, plus any event or sensor the manifest declares. Referencing
anything else is rejected: you cannot monitor what the robot never said it can sense.

## Run it

```bash
python examples/safety-monitor/run_safety_monitor.py
```

It writes [`safety-monitor-report.txt`](safety-monitor-report.txt), byte-asserted in CI
(`reference/validator/tests/test_safety_monitor_example.py`). The report shows the validate
leg (the well-formed envelope accepts; a malformed `always (` and an undeclared `battery_temp`
are rejected with `envelope.monitorable_parse_error` and
`envelope.monitorable_undeclared_signal`) and the monitor leg (a trace that slows near a
person satisfies `slow_near_people`; one that stays fast violates it).

## Honest altitude

The static check is the first line, off-hardware, in an LLM planning loop or CI. The monitor
is the last line, on-hardware, over the live or simulated signal trace. Same declaration,
checked once and enforced continuously. This example is hermetic (validator + the pure-Python
monitor, no ROS, no robot); the runtime shield and the `--rehearse` gate carry it onto a
substrate.
