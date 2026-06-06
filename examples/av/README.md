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

# AV (Autonomous Vehicle) Examples

End-to-end research-grade autonomous-vehicle programs ([RFC-0020](../../docs/rfcs/0020-autoware-av-substrate.md)). Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

The `av` profile is **research-grade**, explicitly not production safety-certified (`production_safety_certified: false`, see [`spec/profiles/av/`](../../spec/profiles/av/README.md)). It adds two Layer-2 primitives: `plan_path` (a compute verb that cost-maps a trajectory against the manifest's HD map and binds it) and `follow_trajectory` (the only verb that actuates, consuming that trajectory). The split is the AV analog of `detect` → `grasp($target)`: decide, then do.

## Scenarios

- **`robotaxi-trip`** — the minimum-viable AV example. `plan_path` computes a route from the depot to the drop-off against the declared HD map and binds it as `route`; `follow_trajectory` drives `route` under a 12 m/s speed envelope. The validator checks that the envelope stays within the manifest's ODD speed cap and that `follow_trajectory` consumes a `plan_path`-produced trajectory. The runtime decomposes the program into a `plan_trajectory` call (compute) and a `follow_trajectory_goal` call (actuate); the audit shows exactly those two.

## Validate

```
urml validate robotaxi-trip.urml.yaml \
  -m robotaxi-trip.manifest.yaml --profile av
```

The companion manifest declares the `av` block (HD map, ODD, MRM) and a compliant US provenance block, so it passes all five validator passes. To watch it run on the hermetic mock (which implements the `TrajectoryAdapter` capability):

```
urml execute robotaxi-trip.urml.yaml \
  -m robotaxi-trip.manifest.yaml --profile av --no-policy
```

A green `reference/autoware-runtime/` adapter (binding `plan_path` to Autoware's mission/behavior/motion planners and `follow_trajectory` to its control stack) is a follow-on; see RFC-0020.
