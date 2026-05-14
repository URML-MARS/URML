# Drone Examples

End-to-end drone-profile programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`) with US-federal-compliant provenance.

## Scenarios

- **`roof-inspection`** — the "citizen inspector" scenario from [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios. Take off, fly to a declared roof inspection station, capture a photo, return home, land.

## Validate

```
urml validate roof-inspection.urml.yaml \
  -m roof-inspection.manifest.yaml --profile drone
```

The companion manifest declares third-party-audited US provenance, so the bundled default policy (RFC-0004) accepts it. Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without provenance blocks.

See the examples convention in [`/examples/README.md`](../README.md).
