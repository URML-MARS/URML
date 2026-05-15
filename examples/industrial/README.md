# Industrial Examples

End-to-end industrial-profile programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`) with US-federal-compliant provenance.

## Scenarios

- **`simple-pick-and-place`** — the minimum-viable industrial example for first-time integrators. One pick-place cycle: navigate to a pick bin, detect a red widget, grasp it, move to the red kitting tray, place it, return home, report cycle completion to the line controller. Modeled on the line-reconfiguration scenario in [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios.

## Validate

```
urml validate simple-pick-and-place.urml.yaml \
  -m simple-pick-and-place.manifest.yaml --profile industrial
```

The companion manifest declares third-party-audited US provenance, so the bundled default policy (RFC-0004) accepts it. Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without provenance blocks.

See the examples convention in [`/examples/README.md`](../README.md).
