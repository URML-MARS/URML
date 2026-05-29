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

# Industrial Examples

End-to-end industrial-profile programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`) with US-federal-compliant provenance.

## Scenarios

- **`simple-pick-and-place`** — the minimum-viable industrial example for first-time integrators. One pick-place cycle written with the **core twelve**: navigate to a pick bin, detect a red widget, grasp it, move to the red kitting tray, place it, return home, report cycle completion to the line controller. Modeled on the line-reconfiguration scenario in [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios. Retained as the documented composition-equivalent of the industrial primitives below.
- **`pick-place-tool-change`** — the same line story written with the industrial profile's own Layer-2 verbs ([RFC-0013](../../docs/rfcs/0013-industrial-layer2-primitives.md)): wait for the safety door, `swap_tool` to fit the wide gripper, `pick_from` the bin, `place_at` the red tray, report. Shows `pick_from`/`place_at`/`swap_tool` end to end; `swap_tool` rides the declared `tool_change_station` docking service.
- **`kawasaki-as-program`** — `call_program` ([RFC-0015](../../docs/rfcs/0015-control-program-invocation.md)): wait for the safety door, then invoke two commissioned on-controller Kawasaki AS-language programs by name (`pick_place_cycle`, `home_all`), and report. The program names are URML-facing identifiers the adapter maps to the real AS programs, declared in the manifest's `programs:` block; an undeclared name is rejected at validation. This is the binding the Kawasaki-Robotics maintainer endorsed on khi_ros2 issue #9. A fourth companion file (`*.echo-response.json`) drives the hermetic hero SVG (`docs/assets/kawasaki-as-program-to-motion.svg`), regenerated with `make kawasaki-demo-record`.

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
