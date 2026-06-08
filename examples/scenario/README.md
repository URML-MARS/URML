<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# URML to OpenSCENARIO (esmini)

A worked example: export a **validated** URML navigation program to an ASAM
OpenSCENARIO (`.xosc`) run, where the URML-governed agent is the controlled
entity. This is the concrete first cut from the esmini engagement
([esmini/esmini#816](https://github.com/esmini/esmini/issues/816)); the esmini
maintainer (@eknabevcc) confirmed that OpenSCENARIO's road-user action model
lines up with URML's mobility layer.

## What it does

[`urml_to_openscenario.py`](urml_to_openscenario.py):

1. **Validates first.** It runs the URML program against its capability manifest
   (`validate(...)`) and refuses to emit a scenario unless the intent is
   admissible. That static gate is URML's whole point: an inadmissible program
   never reaches a simulator.
2. **Maps the validated intent** onto OpenSCENARIO, with the URML agent as the
   single controlled `ScenarioObject`:

   | URML | OpenSCENARIO |
   |---|---|
   | `move_to: { location: X }` | an `Event` with an `AcquirePositionAction` to X's declared `WorldPosition` |
   | `mobility.max_velocity` | the agent's cruise `SpeedAction` (set in `Init`) |
   | the `sequence` of steps | events chained by `StoryboardElementStateCondition` (`completeState`) so each waypoint starts when the previous one finishes |
   | the declared-location pose | a `WorldPosition (x, y, z)` |

The input here is the [`examples/mobile/husky-patrol`](../mobile/) program: a
Clearpath Husky AMR driving two waypoints, then back to the charge point.

## Run it

```bash
python examples/scenario/urml_to_openscenario.py    # regenerates husky-patrol.xosc
```

The generator is pure Python stdlib XML (no esmini, no network needed to
produce the `.xosc`), and deterministic: the committed
[`husky-patrol.xosc`](husky-patrol.xosc) is byte-asserted against it in CI
(`reference/validator/tests/test_openscenario_export.py`), the same discipline
the README hero SVG uses. A stale or hand-edited file fails the build.

## Playing it in esmini

Producing the scenario is hermetic; **playing** it needs esmini plus an
OpenDRIVE road network. The scenario references `straight_500m.xodr`; point it at
any flat road from esmini's resources and run:

```bash
esmini --window 60 60 800 400 --osc husky-patrol.xosc
```

Wiring a specific esmini road + a smoke run is the documented calibration step,
exactly as the PX4 / MuJoCo / Chrono reference runtimes treat their first
hardware/simulator runs.

## Scope

Generation only. Driving the entity at runtime through esmini's
**external-controller / co-simulation** interface (so a live URML runtime acts as
the controller during the scenario) is the deeper integration and is left for
later. The `AnimationAction`-to-joints/limbs idea @eknabevcc raised is URML's
manipulation / whole-body side and is out of scope while esmini has no animation
support. The probabilistic-scenario counterpart is the Scenic engagement
([RFC-0366](../../docs/rfcs/0366-scenic-outreach.md)); the OpenSCENARIO target is
[RFC-0370](../../docs/rfcs/0370-esmini-outreach.md).
