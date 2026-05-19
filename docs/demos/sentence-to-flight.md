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

# Sentence to flight: one English sentence flies a simulated autopilot

The drone counterpart of [sentence-to-motion.md](sentence-to-motion.md). There,
the substrate was a labeled mock that moved nothing. Here it is PX4 SITL: a
real PX4 autopilot running in simulation, flown over MAVLink from one English
sentence. Same pipeline, one substrate step further.

Scenes 1 and 2 are hermetic (no API key, no network). Scene 3 needs one extra
piece you stand up yourself: a running PX4 SITL. That is the honest cost of
showing a real autopilot fly instead of a mock.

Useful for: the proof that URML is not mock-only. A simulated autopilot
actually executing a sentence, reproducible by a developer with no aircraft.

## Prerequisites

- URML installed from a checkout per [Tutorial 1](../tutorials/01-getting-started.md).
- The `urml execute` subcommand. It ships with the sentence-to-motion change;
  if `urml execute --help` works, you have it.
- The PX4 MAVLink transport: `pip install urml-px4-runtime[px4]` (pulls
  `pymavlink`). Without it, Scene 3 exits with an actionable error and no
  traceback rather than pretending.
- A running PX4 SITL on the standard offboard port. The shortest path is the
  PX4 user guide's SITL setup; the gated CI in
  [`.github/workflows/px4-integration.yml`](../../.github/workflows/px4-integration.yml)
  shows the exact headless boot invocation this demo was written against
  (`make px4_sitl jmavsim`, MAVLink on `udp:127.0.0.1:14540`). Edit
  [`examples/drone/flight-only.px4.yaml`](../../examples/drone/flight-only.px4.yaml)
  if your SITL world or ports differ.

## The sentence

```
Take off, fly to the north roof, then return home and land.
```

In [`examples/drone/flight-only.en.txt`](../../examples/drone/flight-only.en.txt).

## Scene 1: the sentence becomes a URML flight program

Hermetic. The `echo` provider replays a committed canned completion, so no
model is called.

```bash
urml translate "Take off, fly to the north roof, then return home and land." \
    -m examples/drone/roof-inspection.manifest.yaml --profile drone \
    --provider echo \
    --echo-response-file examples/drone/flight-only.echo-response.json \
    --out /tmp/flight.generated.yaml
```

Expected (on stderr):

```
wrote /tmp/flight.generated.yaml
Translation accepted after 0 revision(s); profile(s)=drone
```

The generated `/tmp/flight.generated.yaml`:

```yaml
profile: drone
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
  - take_off:
      altitude: 30.0
  - move_to:
      location: roof_north
  - return_to_home: {}
  - land: {}
```

Pure flight: no capture, scan, or measure. That is deliberate. The PX4 adapter
implements the flight primitives for real and returns a documented
not-supported result for perception, so this program is exactly what a PX4
autopilot can fly end to end.

## Scene 2: the validator clears it for execution

Hermetic.

```bash
urml validate /tmp/flight.generated.yaml \
    -m examples/drone/roof-inspection.manifest.yaml \
    --profile drone \
    --no-policy
```

Expected:

```
Validation passed: /tmp/flight.generated.yaml
```

Capability and envelope checks confirmed the drone manifest declares takeoff,
navigation, and return-to-home, and that 30m is inside the declared altitude
envelope, before anything is allowed to fly. `--no-policy` skips the
compliance pass for the same reason as in the mock demo: the language is the
story here. See [compliance-walkthrough.md](compliance-walkthrough.md) for
that pass on its own.

## Scene 3: the simulated autopilot flies it

Not hermetic. With PX4 SITL running:

```bash
urml execute /tmp/flight.generated.yaml \
    -m examples/drone/roof-inspection.manifest.yaml \
    --profile drone \
    --no-policy \
    --adapter px4 \
    --adapter-config examples/drone/flight-only.px4.yaml
```

Expected:

```
URML execute: /tmp/flight.generated.yaml
  adapter:   px4
  substrate: PX4 / MAVLink. Primitives dispatched to the connected autopilot (PX4 SITL or hardware). The vehicle will act.
  re-validation: passed (executed only after the validator accepted it)

  trace (4 step(s) executed, 0 adapter call(s)):
    (4 step(s) dispatched; this adapter keeps no call log, so there is no per-step trace. See RESULT below.)

  RESULT: SUCCESS (4 step(s) executed)
```

In the SITL console and any attached viewer, the vehicle arms, climbs to 30m,
flies north to the roof waypoint, returns to launch, and lands. The trace
shows `0 adapter call(s)` because the PX4 adapter keeps no mock call log: its
effects are MAVLink commands to an autopilot, not recordable in-process calls.
The proof is the autopilot's own state and the four dispatched steps, not a
mock trace. The same fixture is asserted green in CI by the
`drone/flight_only_positive` conformance test (see "What this is NOT").

If SITL is not reachable, the run does not hang: the first flight primitive
fails on the missing MAVLink heartbeat and `urml execute` exits non-zero with
an actionable message. If `pymavlink` is not installed, it exits 2 with the
install hint. Neither path prints a traceback.

## What this is NOT

PX4 SITL is a simulated autopilot, not physical hardware. This demo proves the
URML pipeline flies a real autopilot in simulation. It does not prove a
physical aircraft flew. A physical-hardware run needs an airframe, a payload,
and a licensed operator, and is out of Phase-0 scope. No claim of
physical-hardware verification is made here or anywhere in this repository.

The CI backing is honest about its own state. The gated job `px4-sitl-e2e` in
[`.github/workflows/px4-integration.yml`](../../.github/workflows/px4-integration.yml)
flies the `drone/flight_only_positive` conformance fixture through the same
runner the hermetic suite uses, with a live `PX4Adapter` against PX4 SITL.
That workflow has not been executed yet. Its first run is the calibration run,
exactly as the ROS 2 `gazebo-e2e` job was treated before its calibration runs.
No green run is claimed until one exists; the status is tracked in
[`docs/launch/claims-audit.md`](../launch/claims-audit.md).

This walkthrough is illustrative. A real flight uses a real aircraft manifest,
a real safety envelope, a surveyed waypoint, and a checklist no demo replaces.

## Files used in this walkthrough

- [`examples/drone/flight-only.en.txt`](../../examples/drone/flight-only.en.txt):
  the one-sentence input.
- [`examples/drone/flight-only.echo-response.json`](../../examples/drone/flight-only.echo-response.json):
  the committed canned completion that makes Scene 1 hermetic.
- [`examples/drone/roof-inspection.manifest.yaml`](../../examples/drone/roof-inspection.manifest.yaml):
  the drone capability manifest (declares `home` and `roof_north`).
- [`examples/drone/flight-only.px4.yaml`](../../examples/drone/flight-only.px4.yaml):
  the PX4 adapter config binding location names to local-NED coordinates.
- [`conformance/fixtures/drone/14_flight_only_positive.yaml`](../../conformance/fixtures/drone/14_flight_only_positive.yaml):
  the conformance fixture the gated CI flies; identical program.

## Related reading

- [sentence-to-motion.md](sentence-to-motion.md): the hermetic mock version.
  Start there; this is its drone, real-sim follow-on.
- [compliance-walkthrough.md](compliance-walkthrough.md): the compliance pass
  this demo skips with `--no-policy`, shown on its own.
- [`reference/px4-runtime/tests/integration/test_px4_sitl_e2e.py`](../../reference/px4-runtime/tests/integration/test_px4_sitl_e2e.py):
  the gated end-to-end test this demo's Scene 3 mirrors by hand.
- [Tutorial 1: Getting started](../tutorials/01-getting-started.md): install
  and first run.
