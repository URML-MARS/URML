<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# Relative motion on a frameless buggy (RFC-0630)

A worked example of the `drive` and `turn` primitives: relative (odometric)
motion for a frameless robot, the two-motor, wheel-encoder classroom buggy that
has no global frame. It came out of
[Discussion #497](https://github.com/URML-MARS/URML/discussions/497), where a user
runs URML on a GoPiGo3 and wanted "drive forward X" / "spin X degrees" rather
than navigation to named locations.

- `turn: { angle }` rotates in place by a signed angle in degrees.
- `drive: { distance, arc? }` drives a signed distance in metres; with `arc` it
  follows a circular arc instead of a straight line.

Both are gated by the `educational` profile and the
`mobility.supports_relative_motion` capability, so the validator still refuses
motion a robot cannot perform.

`check_relative_motion.py` validates a square-driving program against the buggy,
then shows the three ways the gate rejects misuse: the wrong profile, a robot
that does not declare relative motion, and a drive past the declared distance
bound.

```
python examples/educational/relative-motion/check_relative_motion.py
```

Validator-only, no server, no robot, deterministic. The committed
`relative-motion-report.txt` is byte-asserted by
`reference/validator/tests/test_relative_motion_example.py`, so the example
cannot drift from the validator.

## Files

- `buggy.manifest.yaml` — a frameless differential buggy declaring relative motion.
- `check_relative_motion.py` — the generator.
- `relative-motion-report.txt` — the recorded, byte-asserted output.
