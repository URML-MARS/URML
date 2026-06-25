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

Run it hermetically (no robot):

```sh
python examples/gopigo3/run_gopigo3.py
```

When the real `easygopigo3` is not installed, it falls back to a fake that records
the wheel calls. The output is deterministic and byte-asserted in
[`gopigo3-report.txt`](gopigo3-report.txt) by
`reference/validator/tests/test_gopigo3_example.py`.

## On a real GoPiGo3

There is nothing to edit. When the GoPiGo3 software is installed, `run_gopigo3.py`
binds to the real `easygopigo3` automatically and the same validated programs
drive the wheels; otherwise it uses the fake. The script prints which backend it
chose on stderr.

Installing the GoPiGo3 software (the `gopigo3` / `easygopigo3` libraries and their
firmware) is the platform's responsibility, not URML's. Follow Dexter Industries'
[GoPiGo3 Installation FAQ](https://github.com/DexterInd/GoPiGo3/blob/main/Installation_FAQ.md).
You will also want `urml-validator` and `urml-ros2-runtime` in the same
environment. Swap the `speak=` callback for your own backend if you do not use espeak.

A basic GoPiGo3 has no arm, camera pipeline, or microphone, so `grasp`, `detect`,
`capture`, and `listen` are returned as not-supported rather than faked. Add a
servo or a sensor and extend `GoPiGo3Adapter`; the URML program, manifest, and
validator do not change.
