# Fieldbus operation modes: cyclic (PDO) vs acyclic (SDO)

A fieldbus carries two kinds of traffic, and they are bounded differently. URML
declares both in the capability manifest's `realtime` block, above the
controller, so the manifest is a faithful description of the drive and the
validator can reject an incoherent timing declaration before the cell is
commissioned.

This example comes from the
[ethercat_driver_ros2 engagement](https://github.com/ICube-Robotics/ethercat_driver_ros2/issues/224)
(RFC-0320). The driver's maintainer put it precisely:

> in a cyclic communication (PDOs) the answer from the bus is immediate, whereas
> for asynchronous (mailbox aka SDOs) the answer time from the bus is not
> guaranteed. The way to handle errors, checks and especially check that goal is
> reached, timeout, etc. changes completely in these cases.

## The two regimes

```
                      cyclic period + watchdog          timeout + goal-reached check
   URML manifest  ─▶  realtime: { cyclic_period_ms,  ─▶  realtime.acyclic: { timeout_ms,
   (declares)          watchdog_ms, guarantee }            requires_goal_check }
                            │                                    │
                       PDO  │  immediate, guaranteed cadence  SDO │  no guaranteed return time
                            ▼                                    ▼
                      EtherCAT process data               EtherCAT mailbox
```

- **Cyclic (PDO)** — the position/velocity command on the control cycle. The
  answer is immediate; a watchdog faults to a safe state if a cycle is missed.
  Declared by `cyclic_period_ms` + `watchdog_ms` ([RFC-0016](../../docs/rfcs/0016-realtime-cyclic-manifest-block.md)).
- **Acyclic (SDO)** — a parameter write or an operation-mode change over the
  mailbox. Its return time is not guaranteed, so a watchdog is the wrong
  instrument; it is bounded by a `timeout_ms` and confirmed by an explicit
  read-back (`requires_goal_check`, default true)
  ([RFC-0469](../../docs/rfcs/0469-acyclic-operation-mode.md)).

URML stays above the controller. It never touches the ESI, the distributed
clock, or the PDO mapping; those stay at the driver / SOEM layer. URML maps a
validated intent onto the controller's command interfaces and declares the
timing regime the substrate runs under.

## What the example shows

[`check_operation_modes.py`](check_operation_modes.py) validates three timing
declarations over the same drive ([`ethercat-drive.manifest.yaml`](ethercat-drive.manifest.yaml)):

| Declaration | Result |
|---|---|
| cyclic PDO only (no mailbox path) | VALID |
| cyclic PDO + coherent acyclic SDO (500 ms timeout) | VALID |
| cyclic PDO + SDO timeout shorter than one cycle | REJECTED — `capability.acyclic_timeout_shorter_than_cycle` |

The rejection is the coherence rule: an acyclic command that must return inside a
single control cycle is, by definition, cyclic traffic and belongs on the cyclic
path. This is a declaration check, not a real-time guarantee; URML does not
police the bus timing itself.

## Run it

```bash
python examples/fieldbus/check_operation_modes.py
```

The script is hermetic (the validator only, no bus, no robot) and deterministic.
The committed [`operation-mode-report.txt`](operation-mode-report.txt) is
byte-asserted by `reference/validator/tests/test_fieldbus_example.py`, so the
example cannot drift from the validator.
