# Warehouse profile examples

Runnable warehouse-profile programs that pair with the [warehouse profile spec](../../spec/profiles/warehouse/README.md) and [RFC-0022](../../docs/rfcs/0022-warehouse-domain-profile.md).

The warehouse profile adds no new Layer-2 primitives. These examples use only the existing twelve core primitives plus the industrial pair (`pick_from`, `place_at` from RFC-0013); the profile-specific value is in the manifest interpretation and the safety envelope, not the program vocabulary.

## Files

- `pick-to-conveyor.urml.yaml` — the URML program.
- `pick-to-conveyor.manifest.yaml` — companion capability manifest for a mobile manipulator AMR with a US-allied compliant BOM.
- `pick-to-conveyor.en.txt` — the natural-language prompt the program was generated from.

## Validate

From the repo root, with the URML packages bootstrapped:

```bash
urml validate examples/warehouse/pick-to-conveyor.urml.yaml \
    --manifest examples/warehouse/pick-to-conveyor.manifest.yaml \
    --profile warehouse
```

Expected: `Validation passed`, exit 0.

The manifest's provenance block declares a Hesai-free, US-allied component set, so the bundled US-federal default policy (RFC-0004) accepts it. Pass `--no-policy` to skip Pass 5 if you want to exercise the program against a manifest without a provenance block.

## See also

- [`/spec/profiles/warehouse/`](../../spec/profiles/warehouse/) — the profile spec.
- [`/docs/rfcs/0022-warehouse-domain-profile.md`](../../docs/rfcs/0022-warehouse-domain-profile.md) — the specifying RFC.
- [`/conformance/fixtures/warehouse/`](../../conformance/fixtures/warehouse/) — eight conformance fixtures covering happy paths, dynamic-obstacle events, the speed-violation rejection, the people-occupancy-zone intrusion rejection, the missing-event rejection, and a full-policy acceptance smoke.
- [`/examples/industrial/`](../industrial/) — the sibling profile's examples for comparison.
