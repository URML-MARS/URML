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

v0.1 humanoid coverage is the **locomotion subset** — whole-body / bimanual manipulation is the explicit [RFC-0010](../../docs/rfcs/0010-whole-body-bimanual-manipulation.md) deferral. The program uses the core twelve under the `home` profile (profiles over forks), exactly as the biped conformance fixtures do, and validates/executes adapter-agnostically against the humanoid runtime's `DigitAdapter` and hermetically against the mock.

## Scenarios

- **`digit-patrol`** — the minimum-viable humanoid example. A navigation-only patrol on a `biped` manifest (Agility Digit, US origin; [RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: biped`): walk to two staging points, then return to the dock. `dock` is a declared *location* (it has a pose), not a docking action.

## Validate

```
urml validate digit-patrol.urml.yaml \
  -m digit-patrol.manifest.yaml --profile home
```

The companion manifest is the canonical Digit biped fixture (US-compliant provenance, so the bundled default policy accepts it). Pass `--no-policy` to skip Pass 5. To watch it run on the hermetic mock:

```
urml execute digit-patrol.urml.yaml \
  -m digit-patrol.manifest.yaml --profile home --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
