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

# A hermetic walkthrough: natural language to a robot, end to end

This is the whole URML path on one page, reproducible on any machine in
under a minute. No robot, no ROS, no cloud, no install beyond the open
packages. Every command here was run exactly as written.

## 1. The intent, in a sentence

[`home/red-mug.en.txt`](home/red-mug.en.txt):

```
Bring me the red mug from the kitchen.
```

The same intent in the manifesto's reserved languages ships alongside
it: [`red-mug.es.txt`](home/red-mug.es.txt),
[`red-mug.ja.txt`](home/red-mug.ja.txt),
[`red-mug.zh.txt`](home/red-mug.zh.txt),
[`red-mug.he.txt`](home/red-mug.he.txt). URML's natural-language layer
is multilingual on purpose; the program below is the same whichever
language produced it.

## 2. The program it yields

[`home/red-mug.urml.yaml`](home/red-mug.urml.yaml) is plain, readable
YAML: move to the kitchen, detect the red mug, grasp it, carry it to
the user, hand it over. That is the entire language surface a reader
needs to understand the scenario.

## 3. Validate it (static, before any actuator moves)

The validator checks the program against the robot's declared
capabilities and the bundled US-federal compliance policy. Nothing
executes until this passes.

```bash
python -m urml_validator.cli validate \
  examples/home/red-mug.urml.yaml \
  -m examples/home/red-mug.manifest.yaml \
  --profile home
```

Observed output:

```
Validation passed: examples/home/red-mug.urml.yaml
```

The companion manifest declares fully US-compliant provenance, so
Pass 5 (RFC-0004) accepts it. Swap in
[`red-mug.dji-camera.manifest.yaml`](home/red-mug.dji-camera.manifest.yaml)
and the same command is rejected with `policy.vendor_denied`: the gate
works, and you can see it work.

## 4. Execute it (hermetic, no hardware)

The conformance suite runs the same scenario through `URMLRuntime`
against a `MockROSAdapter`. It is fully offline and deterministic, so
the run is identical on every machine.

```bash
python -m pytest conformance/tests -q -k red_mug
```

The fixture asserts the five steps execute in order and the audit
trace is `send_navigation_goal, query_detection,
send_manipulation_goal, send_navigation_goal, send_manipulation_goal`.
That trace is the contract: any URML-compatible runtime, on any
substrate, must produce it.

## 5. Run it against a real runtime

The exact same fixtures run against a live substrate by swapping the
adapter. That is the bring-your-own-adapter kit:

```bash
python -m urml_conformance --adapter your_pkg.substrate:YourAdapter
```

See [`/conformance/CONFORMANCE_KIT.md`](../conformance/CONFORMANCE_KIT.md).
The reference runtimes under [`/reference/`](../reference/) are nine
worked adapters across ROS 2, MAVLink, and vendor SDKs to copy from.

## Why this matters

The point of URML is not this one program. It is that the line from a
sentence in any language to a verified robot action is short, legible,
and reproducible without owning the robot. If you can run this page,
you have run URML.
