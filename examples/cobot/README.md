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

# Cobot output-line examples

End-to-end programs for the class of end-effectors and cell signals that are *just a digital or analog line* ([RFC-0017](../../docs/rfcs/0017-digital-io-actuation.md)): a glue gun, a vacuum solenoid, a paint trigger, an ag spot-sprayer relay, an MCU GPIO, a "cycle done" PLC handshake. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

`set_output` is the narrow, bounded actuator for these lines. Unlike `call_program` (RFC-0015), it is not an opaque escape hatch: its effect is a single typed line write the validator fully understands. The line must be declared in `manifest.outputs.lines`, a digital line rejects a non-bool, and an analog value is range-checked against the line's declared `range` — all *before* anything actuates. `pulse_ms` optionally holds the value then auto-reverts to the line's `safe_state`.

## Scenarios

- **`glue-bead`** — move to the seam, set the analog glue-flow setpoint to 65% (range-checked against the declared `[0, 100]`), pulse the digital glue-gun trigger for 800 ms (auto-reverting to its `safe_state` of `false`), raise the digital cycle-done handshake to the PLC, and return home. Modeling the glue gun as `grasp` would be a lie (there is nothing grasped) and as `report` would be a lie (it actuates the world); `set_output` is the honest primitive.

## Validate

```
urml validate glue-bead.urml.yaml \
  -m glue-bead.manifest.yaml --profile industrial
```

The companion manifest declares the three output lines and a compliant US provenance block, so it passes all five validator passes. To watch it run on the hermetic mock (which implements the `OutputAdapter` capability), where each `set_output` becomes a `set_output_line` call in the audit:

```
urml execute glue-bead.urml.yaml \
  -m glue-bead.manifest.yaml --profile industrial --no-policy
```

A green vendor adapter (binding `set_output` to a cobot's digital-output bank, an MCU's GPIO, or a PLC line over the substrate's `std_msgs`/service surface) is a follow-on; see RFC-0017.
