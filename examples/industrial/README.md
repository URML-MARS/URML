# Industrial Examples

End-to-end industrial-profile programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`) with US-federal-compliant provenance.

## Scenarios

- **`simple-pick-and-place`** — the minimum-viable industrial example for first-time integrators. One pick-place cycle written with the **core twelve**: navigate to a pick bin, detect a red widget, grasp it, move to the red kitting tray, place it, return home, report cycle completion to the line controller. Modeled on the line-reconfiguration scenario in [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios. Retained as the documented composition-equivalent of the industrial primitives below.
- **`pick-place-tool-change`** — the same line story written with the industrial profile's own Layer-2 verbs ([RFC-0013](../../docs/rfcs/0013-industrial-layer2-primitives.md)): wait for the safety door, `swap_tool` to fit the wide gripper, `pick_from` the bin, `place_at` the red tray, report. Shows `pick_from`/`place_at`/`swap_tool` end to end; `swap_tool` rides the declared `tool_change_station` docking service.

## Validate

```
urml validate simple-pick-and-place.urml.yaml \
  -m simple-pick-and-place.manifest.yaml --profile industrial

urml validate pick-place-tool-change.urml.yaml \
  -m pick-place-tool-change.manifest.yaml --profile industrial
```

Each companion manifest declares third-party-audited US provenance, so the bundled default policy (RFC-0004) accepts it. Pass `--no-policy` to skip Pass 5 when exercising programs against manifests without provenance blocks. To watch the tool-change example run on the hermetic mock:

```
urml execute pick-place-tool-change.urml.yaml \
  -m pick-place-tool-change.manifest.yaml --profile industrial --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
