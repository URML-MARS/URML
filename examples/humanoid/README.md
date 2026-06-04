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

# Humanoid Examples

End-to-end humanoid programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

A humanoid is a biped ([RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: biped`) with two arms ([RFC-0010](../../docs/rfcs/0010-whole-body-bimanual-manipulation.md) whole-body manipulation). Both the locomotion path and whole-body manipulation are in scope. The programs use the core vocabulary plus the `bimanual` primitive under the `home` profile (profiles over forks), exactly as the biped conformance fixtures do, and validate/execute adapter-agnostically against the humanoid runtime's `DigitAdapter` and hermetically against the mock.

## Scenarios

- **`digit-patrol`** — the minimum-viable locomotion example. A navigation-only patrol on a `biped` manifest (Agility Digit, US origin; [RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: biped`): walk to two staging points, then return to the dock. `dock` is a declared *location* (it has a pose), not a docking action.
- **`digit-tote-lift`** — the minimum-viable whole-body example ([RFC-0010](../../docs/rfcs/0010-whole-body-bimanual-manipulation.md)). On a two-arm Digit manifest (`manipulation.arm_count: 2` with a named `arms` list), the robot detects a tote, lifts it with both arms in one `bimanual together` step, walks it to staging, and sets it down with both arms. The runtime decomposes each `bimanual` into a left-arm and a right-arm `send_manipulation_goal`, so the audit shows one detection and two arm-addressed goals per lift.

## Validate

```
urml validate digit-patrol.urml.yaml \
  -m digit-patrol.manifest.yaml --profile home

urml validate digit-tote-lift.urml.yaml \
  -m digit-tote-lift.manifest.yaml --profile home
```

The companion manifests carry US-compliant provenance, so the bundled default policy accepts them. Pass `--no-policy` to skip Pass 5. To watch one run on the hermetic mock:

```
urml execute digit-tote-lift.urml.yaml \
  -m digit-tote-lift.manifest.yaml --profile home --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
