# A declared actuator envelope, checked before dispatch

For [gatech-epic-power/epically-powerful#32](https://github.com/gatech-epic-power/epically-powerful/issues/32).

[Epically Powerful](https://github.com/gatech-epic-power/epically-powerful) (Georgia
Tech EPIC Lab) commands quasi-direct-drive actuators (CubeMars AK, RobStride,
CyberGear) over CAN and enforces per-motor limits at run time. This example declares
the *same* envelope in a URML manifest and checks a command against it statically,
before anything is sent over CAN.

## The question this answers

The issue raised a fair point: if the runtime monitor already limit-checks every
command, does a static pre-dispatch check just duplicate it and add overhead?

It does not. The two are complementary layers:

- **URML's static check is the first line, off-hardware.** It runs in an LLM planning
  loop, in CI, or in simulation, before any command reaches the bus.
- **Epically Powerful's runtime monitor is the last line, on-hardware,** during
  execution.

The static gate catches an inadmissible command (an LLM emitting a 50 Nm target on a
±35 Nm actuator) in exactly the contexts where a runtime monitor cannot run, because
there is no hardware in the loop yet. And the envelope is one substrate-neutral
declaration that covers CubeMars, RobStride, and CyberGear actuators alike.

## What it shows

The manifest models one QDD actuator joint as an RFC-0018 `minimal_node` with two
RFC-0017 analog output lines, whose ranges are the actuator's real limits:

| Line | Declared range | Source |
|---|---|---|
| `joint_torque_nm` | ±35.0 Nm | `torque_limits` |
| `joint_velocity_rad_s` | ±20.0 rad/s | `velocity_limits` |

Three commands against that envelope:

1. **Admissible**: `set_output joint_torque_nm = 20.0` validates (within ±35).
2. **Rejected (torque)**: `set_output joint_torque_nm = 50.0` is rejected with
   `capability.output_value_out_of_range`, before dispatch.
3. **Rejected (velocity)**: `set_output joint_velocity_rad_s = 30.0` is rejected the
   same way, showing the check generalizes across limit types.

## Run it

```bash
python examples/epically-powerful/run_epically_powerful.py
```

The run is hermetic and deterministic (validator only, no CAN, no hardware). The
committed [`epically-powerful-report.txt`](epically-powerful-report.txt) is
byte-asserted in CI, so the example cannot drift from what the tool actually does.

## Honest altitude

URML declares and statically checks; Epically Powerful does the runtime monitoring and
the actual CAN actuation. URML does no motor control, no current loop, and no
scheduling.

The envelope numbers are cross-cited from Epically Powerful's own motor table (the
CubeMars `AKE80-8-V3` entry in `epicallypowerful/actuation/motor_data.py`, commit
`2a3941278c59`). No code is vendored, and there is no dependency on their package
(AGPL-3.0). Compliance policy is out of scope for this example, so it runs with policy
off; the CubeMars origin is stated truthfully in the manifest regardless.
