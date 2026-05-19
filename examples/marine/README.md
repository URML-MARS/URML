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

# Marine Examples

End-to-end underwater-vehicle programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

The marine runtime's `BlueRovAdapter` speaks MAVLink with **zero ROS** — this family doubles as the proof that a URML primitive is not ROS-coupled. Underwater navigation adds no new profile — the program uses the core twelve under the `home` profile (profiles over forks), exactly as the marine conformance fixture does, and runs hermetically against the mock and adapter-agnostically against `BlueRovAdapter`.

## Scenarios

- **`reef-survey`** — the minimum-viable marine example. A navigation-only survey on a BlueROV2 manifest (`mobility.drive_type: underwater_thrusters`): descend to the survey start, run the reef transect, then hold at the ascent point. The depth waypoints are declared *locations* (z = depth), not docking actions.

## Validate

```
urml validate reef-survey.urml.yaml \
  -m reef-survey.manifest.yaml --profile home
```

Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without a provenance block. To watch it run on the hermetic mock:

```
urml execute reef-survey.urml.yaml \
  -m reef-survey.manifest.yaml --profile home --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
