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

# Mobile Examples

End-to-end wheeled-AMR programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`) with US-federal-compliant provenance.

Wheeled AMR navigation adds no new profile — the program uses the core twelve under the `home` profile (profiles over forks), exactly as the mobile conformance fixtures do, and validates/executes adapter-agnostically against the mobile runtime's `HuskyAdapter` / `JackalAdapter` and hermetically against the mock.

## Scenarios

- **`husky-patrol`** — the minimum-viable mobile example. A navigation-only patrol on a Clearpath Husky manifest (`mobility.drive_type: differential`) that declares compliant parts (Robotiq gripper, Intel RealSense camera, Clearpath base — none on the FCC Covered List): drive to two waypoints, then return to the charge point. `charge_point` is a declared *location* (it has a pose), not a docking action.

## Validate

```
urml validate husky-patrol.urml.yaml \
  -m husky-patrol.manifest.yaml --profile home
```

The companion manifest declares third-party-audited US provenance, so the bundled default policy (RFC-0004) accepts it. Pass `--no-policy` to skip Pass 5. To watch it run on the hermetic mock:

```
urml execute husky-patrol.urml.yaml \
  -m husky-patrol.manifest.yaml --profile home --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
