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

# Legged Examples

End-to-end legged-robot programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

Legged locomotion adds no new profile — the program uses the core twelve under the `home` profile (profiles over forks), exactly as the quadruped conformance fixtures do. The same program validates and executes adapter-agnostically against the legged runtime's `SpotAdapter` / `AnymalAdapter` and hermetically against the mock.

## Scenarios

- **`spot-patrol`** — the minimum-viable legged example. A navigation-only patrol on a `quadruped` manifest ([RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: quadruped`): walk to two patrol waypoints, then return to the dock. `dock` is a declared *location* (it has a pose), not a docking action, so the program stays within core navigation.

## Validate

```
urml validate spot-patrol.urml.yaml \
  -m spot-patrol.manifest.yaml --profile home
```

The companion manifest is the canonical Spot quadruped fixture. Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without a provenance block. To watch it run on the hermetic mock:

```
urml execute spot-patrol.urml.yaml \
  -m spot-patrol.manifest.yaml --profile home --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
