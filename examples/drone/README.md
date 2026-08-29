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

# Drone Examples

End-to-end drone-profile programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`) with US-federal-compliant provenance.

## Scenarios

- **`roof-inspection`** — the "citizen inspector" scenario from [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios. Take off, fly to a declared roof inspection station, capture a photo, return home, land.
- **`bridge-survey`**, **`parallel-watch`**, **`link-aware-patrol`** — scan, parallel composition, and RFC-0006 link-loss policy on the same PX4-shaped manifest.
- **`bench-battery`**, **`bench-hop`** — a real Pixhawk running ArduCopter on USB, propellers off (`pixhawk-ardupilot.manifest.yaml`, `pixhawk-ardupilot.adapter.yaml`). The first reads the battery over MAVLink; the second is refused by the autopilot's own pre-arm checks. Runbook: [`docs/demos/sentence-to-pixhawk.md`](../../docs/demos/sentence-to-pixhawk.md).
- **`site-photogrammetry`** — flight test 1: five orbit stations at 100 m AGL around a geocoded address, one photo each. WGS84 bindings in `site-photogrammetry.adapter.yaml`, produced by `tools/scripts/geocode_locations.py` from `addresses.example.yaml`.
- **`parcel-delivery`**, **`parcel-delivery-servo`** — flight test 2: carry a parcel to a geocoded drop-off and release by winch + latch, or latch only. Payload mechanisms are RFC-0017 output lines driven by `set_output`.

The flight-test bundles are validated in CI and gated on an ArduCopter SITL pass before any field run; no physical flight is claimed. Each ships a manifest and an envelope; validate with `-e <name>.envelope.yaml`.

## Run on hardware

```
python -m urml_ardupilot_runtime.probe COM5
urml execute bench-battery.urml.yaml -m pixhawk-ardupilot.manifest.yaml   --profile drone --no-policy --adapter ardupilot   --adapter-config pixhawk-ardupilot.adapter.yaml
```

## Validate

```
urml validate roof-inspection.urml.yaml \
  -m roof-inspection.manifest.yaml --profile drone
```

The companion manifest declares third-party-audited US provenance, so the bundled default policy (RFC-0004) accepts it. Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without provenance blocks.

See the examples convention in [`/examples/README.md`](../README.md).
