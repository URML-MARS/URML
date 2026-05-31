<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# Fleet demo — courier-to-arm handoff

The multi-robot example for [RFC-0286](../../docs/rfcs/0286-multi-robot-fleet-addressing.md).
Two heterogeneous robots, one program, one job neither can do alone: a mobile
base (`courier`) brings a tray to a shared dock; a stationary arm (`arm`) picks a
widget from the dock and places it on a conveyor; the courier leaves only after
the arm has cleared.

```
courier ──move_to(handoff_dock)──┐
                                 ├─ BARRIER ─┬─ arm: pick_from(dock) ─ place_at(conveyor) ─┐
                                 │           └─ courier: wait (hold) ───────────────────────┤
                                 │                                              ─ BARRIER ──┴── courier ──move_to(staging)
```

## Run it

Hermetic — no ROS, no cloud, any OS:

```bash
python run_demo.py
```

It validates the mission across both members' manifests, then executes it against
one `MockROSAdapter` per member and prints each robot's audit trail.

## Files

| File | What it is |
|---|---|
| [`courier_handoff.fleet.yaml`](courier_handoff.fleet.yaml) | The mission: a **roster** (member handles → manifests) and the **program** (`on:` scopes + `barrier:` rendezvous), as one two-document YAML. |
| [`husky_amr.manifest.yaml`](husky_amr.manifest.yaml) | The courier's per-robot capability manifest. |
| [`kawasaki_rs.manifest.yaml`](kawasaki_rs.manifest.yaml) | The arm's per-robot capability manifest. |
| [`run_demo.py`](run_demo.py) | The runnable `validate → execute` pipeline. |

## What the validator catches before anything moves

The point is not the syntax — it is the cross-robot safety the validator enforces
*statically*:

- **Member-scoped capability.** `place_at: conveyor_a` is checked against the
  *arm's* manifest, `move_to: handoff_dock` against the *courier's*.
- **Cross-robot collision.** Delete the step-2 barrier and the arm could reach
  into the dock before the courier has stopped — flagged as
  `fleet.concurrent_shared_workspace`.
- **Synchronization is real.** Each `barrier` member must declare the `peer_link`
  connectivity role (`fleet.barrier_missing_peer_link`).

## A note on YAML

The `on:` node is spelled `type: "on"` — **quoted**. YAML 1.1 reads a bare `on`
as the boolean `true`, so the quotes are required (the same reason `yes`/`no` are
quoted). The `barrier`, `sequence`, and `parallel` tags need no quoting.
