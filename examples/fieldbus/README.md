# Fieldbus: operation modes, clock, and bring-up ordering

A fieldbus carries cyclic and acyclic traffic, runs under a clock that cannot
always be hidden, and brings its elements up in a dependency-constrained order.
URML declares all three in the capability manifest, above the controller, so the
manifest is a faithful description of the drive and the validator can reject an
incoherent declaration before the cell is commissioned. This example grew out of
one engagement thread: the maintainer raised the operation-mode distinction
first, then the clock and ordering questions.

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

[`check_operation_modes.py`](check_operation_modes.py) validates the same CiA-402
drive ([`ethercat-drive.manifest.yaml`](ethercat-drive.manifest.yaml)) across the
three fieldbus blocks the engagement surfaced:

| Block | Declaration | Result |
|---|---|---|
| Operation mode (RFC-0016 / [0469](../../docs/rfcs/0469-acyclic-operation-mode.md)) | cyclic PDO only | VALID |
| | cyclic PDO + coherent acyclic SDO (500 ms) | VALID |
| | cyclic PDO + SDO timeout shorter than one cycle | REJECTED — `capability.acyclic_timeout_shorter_than_cycle` |
| Clock / time sync ([0477](../../docs/rfcs/0477-substrate-clock-synchronization.md)) | bus clock as reference (EtherCAT DC) | VALID |
| | master-synced without a sync protocol | REJECTED — `capability.clock_sync_protocol_required` |
| Bring-up ordering ([0478](../../docs/rfcs/0478-substrate-bringup-ordering.md)) | power_bus → drive_axis_1 → gripper | VALID |
| | circular bring-up dependency | REJECTED — `capability.bringup_dependency_cycle` |

Each rejection is a coherence rule. An acyclic command that must return inside a
single control cycle is cyclic traffic, not acyclic. A `master_synced` clock with
no sync protocol cannot actually be synchronized. A circular bring-up dependency
can never be satisfied. These are declaration checks, not real-time guarantees;
URML does not police the bus timing itself.

### The three regimes

- **Operation mode** — cyclic PDO (control period + watchdog) vs acyclic SDO
  (timeout + read-back goal check). The maintainer's first point: the answer
  time differs, so the instrument differs.
- **Clock / time synchronization** — once events outside the bus must be
  synchronized, the bus clock cannot be hidden. Either the bus clock is the
  reference (EtherCAT DC, strongest guarantee, hardware-timestamped) or the bus
  rides a master synced to the user clock (needs a protocol, bounds user drift).
- **Bring-up / recovery ordering** — a drive cannot init before its power bus; a
  gripper cannot configure before its drive; recovery order may differ from
  bring-up. Declared as dependencies, checked acyclic.

## Run it

```bash
python examples/fieldbus/check_operation_modes.py
```

The script is hermetic (the validator only, no bus, no robot) and deterministic.
The committed [`operation-mode-report.txt`](operation-mode-report.txt) is
byte-asserted by `reference/validator/tests/test_fieldbus_example.py`, so the
example cannot drift from the validator.
