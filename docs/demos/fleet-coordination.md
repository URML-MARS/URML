<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# Demo: fleet coordination — a courier-to-arm handoff

The multi-robot walkthrough for [RFC-0286](../rfcs/0286-multi-robot-fleet-addressing.md).
One program commands two heterogeneous robots through a job neither can do alone, and
the validator catches a cross-robot collision before anything moves.

The runnable bundle lives in [`examples/fleet/`](../../examples/fleet/). It is hermetic:
pure Python, no ROS, no cloud, any OS.

```bash
python examples/fleet/run_demo.py
```

## The job

1. The **courier** (a mobile base) drives to a shared handoff dock.
2. **BARRIER** — neither robot proceeds until both have reached the rendezvous. The
   exchange cannot start half-ready.
3. In **parallel**: the **arm** (a stationary industrial arm) picks a widget from the dock
   and places it on a conveyor, while the courier holds station.
4. **BARRIER** — the courier leaves only after the arm has cleared.
5. The courier returns to staging.

## The mission file

A fleet mission is two YAML documents: a **roster** (member handles → per-robot manifests)
and the **program**. The roster binds two *existing, unchanged* manifests:

```yaml
roster_version: "0.1"
members:
  - { name: courier, manifest: husky_amr }
  - { name: arm,     manifest: kawasaki_rs }
```

The program addresses members with `on:` and synchronizes them with `barrier:`. (The `on:`
tag is written `type: "on"` — quoted — because YAML 1.1 reads a bare `on` as the boolean
`true`.) See the full file at
[`examples/fleet/courier_handoff.fleet.yaml`](../../examples/fleet/courier_handoff.fleet.yaml).

## What you see

```
fleet: arm, courier
validate_fleet -> accepted=True
execute -> success=True, steps=5
  arm: send_navigation_goal -> query_detection -> send_manipulation_goal -> send_navigation_goal -> send_manipulation_goal
  courier: send_navigation_goal -> wait_passively -> send_navigation_goal
```

Each member has its own adapter, so the audit trail is one clean call-log per robot: the
courier navigates twice and holds; the arm picks and places.

## What the validator rejects (the point)

The value is not the syntax. It is the cross-robot safety the validator enforces
*statically*. The conformance lane ([`conformance/fixtures/fleet/`](../../conformance/fixtures/fleet/))
ships one positive and four negatives, one per check:

| Break the program this way | Validator says |
|---|---|
| Address a member the roster doesn't declare | `fleet.undeclared_member` |
| Scope `pick_from` to the courier (no gripper/perception) | `fleet.capability_unsupported_on_member` |
| Send both robots to `handoff_dock` in one `parallel`, no barrier | `fleet.concurrent_shared_workspace` |
| Name a member with no `peer_link` in a `barrier` | `fleet.barrier_missing_peer_link` |

The third is the one no single vendor SDK can catch — two robots into the same place at the
same instant — because no single SDK sees both robots.

## Honest limits (v0.1)

- **Collision is by location name, not geometry.** Two members "share a workspace" iff they
  target the same *declared location name* concurrently. A `workspace_volumes` block with
  polygon overlap is named as future work in the RFC.
- **Execution is deterministic and sequential**, like the single-robot runtime. A `barrier`
  is a rendezvous marker under sequential execution; its teeth are in the validator.
- **Building-scale fleet traffic** (lift queues, aisle reservation) is Open-RMF's job
  ([RFC-0053](../rfcs/0053-open-rmf-multirobot-integration.md)), not URML's.

## See also

- [RFC-0286](../rfcs/0286-multi-robot-fleet-addressing.md) — the design and decision trail.
- [`examples/fleet/README.md`](../../examples/fleet/README.md) — the runnable bundle.
- [Layer-3 spec](../../spec/layer-3-behavior/README.md) §Fleet addressing — the normative nodes.
