# URML on a Robotiq Hand-E (declare a force envelope, refuse a grasp that breaks it)

The worked example promised to [@macmacal](https://github.com/macmacal) on
[AGH-CEAI/robotiq_hande_driver#44](https://github.com/AGH-CEAI/robotiq_hande_driver/issues/44),
where he confirmed a system-level admissibility layer "could indeed be useful"
and that a Hand-E's parameters map onto a capability manifest cleanly.

A Robotiq Hand-E is a **single-DoF parallel-jaw gripper**: an aperture and a
commanded force, no dexterity. So URML declares it as an ordinary (non-dexterous)
gripper with a force range and the object classes it accepts. That force range is
the envelope the validator checks a grasp against, **before** anything reaches the
`ros2_control` hardware interface.

- [`robotiq-hande.manifest.yaml`](robotiq-hande.manifest.yaml): one arm, one
  `servo_electric` gripper `hand_e`, force envelope `20.0 - 185.0 N`, accepting
  `small_part`.
- [`run_robotiq_hande.py`](run_robotiq_hande.py): validates two grasps against
  that manifest, no execution and no hardware:
  1. grasp a small part at **60 N** (inside the envelope) → **accepted**;
  2. the same grasp at **250 N** (over the cap) → **rejected** before the gripper
     closes.

```
[VALID]    grasp small_part at 60.0 N
[REJECTED] grasp small_part at 250.0 N
   -> capability.missing_gripper, envelope.force_exceeded
```

Run it:

```sh
python examples/robotiq-hande/run_robotiq_hande.py
```

Deterministic and byte-asserted in [`robotiq-hande-report.txt`](robotiq-hande-report.txt)
by `reference/validator/tests/test_robotiq_hande_example.py`.

## Why URML is additive to ros2_control, not a reimplementation

In `ros2_control` the gripper's limits live in the URDF and the hardware interface
exchanges I/O; the controller waits for a setpoint. URML does not duplicate that.
It sits one layer up, reading the same numbers (force range, and which object
classes fit) and refusing an out-of-envelope grasp before the setpoint is ever
handed down. The Modbus / UR-tool-comm / fake backends look identical from here,
because the check runs **before** the command regardless of what feedback comes
back. macmacal's own distinction holds: this is the "is this grasp admissible?"
check, separate from the runtime "did the grasp succeed?" interpretation.

## The honest limitation: no explicit aperture field

URML's simple-gripper model states a **force range** (first-class and enforced,
as the 250 N refusal shows) and a set of **accepted object classes**. It has no
explicit aperture field. On a single-DoF gripper, "what fits" is carried by
`accepted_classes` and "how hard" is the force envelope, so the aperture is
implicit in which objects the gripper is declared to accept rather than stated as
a min/max opening. A dexterous, multi-fingered hand is a different model
([RFC-0586](../../docs/rfcs/0586-dexterous-hand-declaration.md)); a Hand-E does
not need it.

The over-force grasp is refused on two independent, honest grounds: no declared
gripper is **rated** for 250 N (`capability.missing_gripper`), and 250 N exceeds
the declared **force cap** (`envelope.force_exceeded`).
