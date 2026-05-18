# URML Conformance Kit

This is how you check whether a robot runtime is URML-compatible. The
fixtures in `conformance/fixtures/` are the contract. They are Apache
2.0 and part of the [Core Commitment](../CORE_COMMITMENT.md): the
behavior a runtime claims compatibility with does not move behind a
paywall, ever.

You do not need any reference runtime, any robot, or ROS to run this.
The default run is fully hermetic.

## The idea in one paragraph

URML programs are substrate-neutral. A *runtime* is the thing that
translates a validated URML program into commands for a specific robot
stack (ROS 2, PX4/MAVLink, a vendor SDK). A runtime is URML-compatible
if, for every fixture, it validates the program the way the spec says
and executes it with the effects the spec says. You demonstrate that by
implementing one small Python Protocol and running the suite against
it.

## Step 1: implement the adapter Protocol

Implement `ROSAdapter` from
`reference/ros2-runtime/src/urml_ros2_runtime/substrate/base.py`. The
name has "ROS" in it for historical reasons; the Protocol is
substrate-neutral and has no ROS dependency. It is ~15 methods, one per
URML primitive dispatch step (`send_navigation_goal`,
`send_manipulation_goal`, `query_detection`, ...).

Two rules carry all the weight:

- **Return failures, do not raise them.** Every method returns a typed
  result with a `success: bool`. A robot-side failure is
  `success=False` with a `reason`. Only an unrecoverable substrate
  break (process died, transport gone) may raise.
- **Be honest about what you do not have.** If your robot has no arm,
  `send_manipulation_goal` returns `success=False` with a clear
  `reason` (the reference runtimes use a `not_supported_on_<x>`
  convention). It does not pretend.

The reference runtimes are worked examples of every shape: a composed
ROS 2 runtime (`reference/industrial-arm-runtime`,
`reference/mobile-runtime`), a no-ROS MAVLink runtime
(`reference/px4-runtime`, `reference/marine-runtime`), and a vendor-SDK
runtime (`reference/legged-runtime`'s `SpotAdapter` over `bosdyn`).
Copy the closest one.

## Step 2: run the suite against your adapter

Your adapter factory is anything callable with no arguments that
returns a fresh adapter instance. A class or a factory function both
work:

```bash
pip install -e reference/validator -e reference/ros2-runtime -e conformance
python -m urml_conformance --adapter your_pkg.substrate:YourAdapter
```

Useful flags:

```bash
python -m urml_conformance                       # hermetic self-test (MockROSAdapter)
python -m urml_conformance --filter quadruped    # one family
python -m urml_conformance --adapter p:A -v       # full per-case report
```

Or wire it in code, the same hook the reference runtimes' gated CI
uses:

```python
from urml_conformance import ConformanceRunner
report = ConformanceRunner(adapter_factory=lambda: YourAdapter()).run()
assert report.all_passed, report.render()
```

## Step 3: read the result

Exit code is `0` only if every selected fixture passes, so this drops
straight into a CI job. A failing case prints what diverged: a
validation outcome that did not match, a wrong executed-step count, or
an audit-trace mismatch. Fixtures whose programs your robot genuinely
cannot serve (no arm, no camera) are not your failures to force green:
the right move is the honest not-supported result plus a fixture subset
that matches your robot's declared capability manifest, exactly as the
PX4 runtime runs the flight-only subset rather than faking perception.

## What "URML-compatible" means

Passing the suite is a factual statement: this runtime reproduces the
spec's behavior on the shared contract. During Phase 0 this is
**self-assessment** — run it yourself, in your own CI, against your own
runtime. There is no badge to display and no claim to publish yet; a
formal certification program is a later, separate concern and is not
implied by passing these fixtures. Measure first, claim later.

## Privacy

The suite runs entirely locally and sends nothing anywhere. There is no
telemetry, no phone-home, no identifier collected. You can run it fully
offline.

## Contributing a fixture

A good fixture is spec-level: it must pass on *any* URML-compatible
runtime, not just one. If you find behavior the spec implies but no
fixture pins, that is the most valuable contribution. The fixture
format is `conformance/fixtures/<profile>/NN_name.yaml`; see existing
ones for the shape. (External contribution process opens in Phase 1;
until then, file it as an issue.)
