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
python -m urml_conformance --adapter p:A --report report.json   # JSON report
```

`urml conformance run --adapter p:A --filter drone --output report.json`
does the same from the `urml` command line.

Or wire it in code, the same hook the reference runtimes' gated CI
uses:

```python
from urml_conformance import ConformanceRunner, run_suite
report = ConformanceRunner(adapter_factory=lambda: YourAdapter()).run()
assert report.all_passed, report.render()

report = run_suite("your_pkg.substrate:YourAdapter", filter="drone")  # what the CLIs run
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

The JSON report (`urml.conformance-report/1`) says what ran:
`all_passed`, the `passed` and `failed` counts, the `adapter` spec
(`urml_ros2_runtime:MockROSAdapter` when you pass none), the
urml-conformance and urml-validator versions, the `--filter`, the number
of fixtures, and a sha256 over the fixture files, followed by one result
per fixture. A report read back must agree with its own results, so an
edited `all_passed` does not parse.

## The goal line: a rejected program sends nothing

The main run stops a rejected fixture at the validator. The goal-line
lane hands every rejected fixture to the runtime itself, through a
recording proxy around your adapter. A case passes only when the runtime
refuses, the refusal carries the fixture's expected error codes, and the
adapter saw zero calls:

```bash
python -m urml_conformance --goal-line                                # reference runtime + mock
python -m urml_conformance --goal-line --adapter your_pkg:YourAdapter
python -m urml_conformance --goal-line --runtime your_pkg:make_runtime
```

`--runtime` takes a callable that receives one adapter and returns your
runtime. Its `execute(program, manifest, envelope, profiles, *, policy,
manifest_base_dir)` must refuse by raising an exception whose
`validation_result` holds the validator's result, the way `URMLRuntime`
raises `ValidationRejectedError`. Fleet fixtures run through the
reference `FleetRuntime`. In code, call
`run_goal_line(adapter_factory=..., runtime_factory=...)`.

## What "URML-compatible" means

Passing the suite is a factual statement: this runtime reproduces the
spec's behavior on the shared contract. It is the **self-reported** tier
of [`spec/conformance/v0.1.0.md`](../spec/conformance/v0.1.0.md) section
3: run it yourself, in your own CI, against your own runtime's adapter.
To publish the result, add the JSON report to an entry in the
[URML registry](../registry/README.md), whose checker refuses a report
from the mock adapter or with a failed fixture. There is no badge to
display, and the `URML-Certified` mark is reserved for a separate
program that does not exist yet (see [TRADEMARK.md](../TRADEMARK.md)).

## Privacy

The suite runs entirely locally and sends nothing anywhere. There is no
telemetry, no phone-home, no identifier collected. You can run it fully
offline.

## Contributing a fixture

A good fixture is spec-level: it must pass on *any* URML-compatible
runtime, not just one. If you find behavior the spec implies but no
fixture pins, that is the most valuable contribution. The fixture
format is `conformance/fixtures/<profile>/NN_name.yaml`; see existing
ones for the shape, and send it as a pull request per
[CONTRIBUTING.md](../CONTRIBUTING.md).
