# A native (non-ROS) GoPiGo3 URML runtime — the #523 headstart

On [Discussion #523](https://github.com/URML-MARS/URML/discussions/523),
[@slowrunner](https://github.com/slowrunner) asked for an example runtime that
drives a basic GoPiGo3 from a validated URML program, on the Raspberry Pi,
without ROS. This is that headstart, and it runs end to end here with no robot.

The GoPiGo3 is frameless (dead reckoning), so its natural vocabulary is "drive
forward X" and "turn X degrees", not "go to the kitchen". URML expresses that with
the [RFC-0630](../../docs/rfcs/0630-relative-motion-primitive.md) `drive` / `turn`
primitives, gated by the `educational` profile and `mobility.supports_relative_motion`.
"Announce ..." maps to `speak`, which the Pi backs with espeak.

Three files:

- [`gopigo3.manifest.yaml`](gopigo3.manifest.yaml) — the basic GoPiGo3 capability
  manifest (differential, relative-motion, a distance sensor, an espeak output).
- [`gopigo3_adapter.py`](gopigo3_adapter.py) — `GoPiGo3Adapter`, which drives the
  wheels through Dexter Industries' `easygopigo3` (`drive_cm` / `turn_degrees` /
  `orbit`) and speaks through espeak. The library is imported lazily, so the file
  is importable on any machine; the real library is only needed to move a robot.
- [`run_gopigo3.py`](run_gopigo3.py) — validates two programs and executes them
  through the adapter.

```
[VALID] announce, then drive 1 m (the translated command from #497/#523)
   executed 2 steps, success=True
     emit_speech  -> espeak 'Driving forward 1 meter'
     drive_by     -> easygopigo3.drive_cm(100.0)
```

Run it (dry run, never moves a robot):

```sh
python examples/gopigo3/run_gopigo3.py
```

By default this is a **dry run**: it validates the programs and prints the planned
wheel/speech calls against a fake backend. Nothing actuates, so it is safe to run
by habit (including `-h`). The output is deterministic and byte-asserted in
[`gopigo3-report.txt`](gopigo3-report.txt) by
`reference/validator/tests/test_gopigo3_example.py`.

### Run your own translated program

Point `-f` at the YAML that `urml translate ... --out prog.urml.yaml` wrote, to
run *your* program instead of the two built-in demos:

```sh
urml translate "Drive forward 10 centimeters" \
    --manifest gopigo3.manifest.yaml --profile educational --no-policy \
    --provider openai --model qwen3.5:9b --out drive10.urml.yaml
python examples/gopigo3/run_gopigo3.py -f drive10.urml.yaml          # dry run
python examples/gopigo3/run_gopigo3.py -f drive10.urml.yaml --execute # drives the robot
```

This is the loop @slowrunner runs: translate an English sentence on a capable box,
copy the validated YAML to the Pi, and run it here.

### Versions, for a traceable run

`run_gopigo3.py --version` prints the URML package versions it runs on, and every
run prints the same line on stderr (a `-f` run also records it in its report
header). The version is read from the installed package metadata
(`importlib.metadata`), so there is no version string to hand-edit when the code
changes: `pip` records it, the example reports it.

## On a real GoPiGo3

To actually drive the wheels, pass `--execute`:

```sh
python examples/gopigo3/run_gopigo3.py --execute   # WILL move a connected GoPiGo3
```

With `--execute` the script uses the installed `easygopigo3` and drives the robot,
after printing a warning. Without it, the script never moves a robot. To preview a
program on a robot-connected machine without moving anything, add `-m` / `--mock`
(it forces the fake backend even with `--execute`). URML is a validate-before-actuate
project, so actuation is opt-in, not the default; thanks to @slowrunner, whose
GoPiGo3 drove off when he ran the old version with `-h`.

Installing the GoPiGo3 software (the `gopigo3` / `easygopigo3` libraries and their
firmware) is the platform's responsibility, not URML's. Follow Dexter Industries'
[GoPiGo3 Installation FAQ](https://github.com/DexterInd/GoPiGo3/blob/main/Installation_FAQ.md).
You will also want `urml-validator` and `urml-ros2-runtime` in the same environment.

**Speech.** The default `speak` backend is espeak; if espeak is missing or the
Pi has no audio output configured, the utterance is not spoken and the adapter
says so on stderr (it does not fail silently). If your robot has its own speech
path (for example a ROS say node), pass your own callable as
`GoPiGo3Adapter(speak=...)` instead of relying on espeak.

A basic GoPiGo3 has no arm, camera pipeline, or microphone, so `grasp`, `detect`,
`capture`, and `listen` are returned as not-supported rather than faked. Add a
servo or a sensor and extend `GoPiGo3Adapter`; the URML program, manifest, and
validator do not change.
