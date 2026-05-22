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

# SPEC-GAPS — urml-opcua-runtime

Per the spec-gap protocol (RFC-0014): this runtime is built strictly
against the frozen substrate Protocol. Anything the OPC UA Robotics
substrate needs that URML cannot express is recorded here and, if
genuinely inexpressible, promoted to a numbered RFC Draft for
maintainer decision — never a silent primitive/schema change.

## Genuinely inexpressible → RFC Drafts filed

- **RFC-0015 — ControlProgram / PLC-method invocation.** OPC UA
  Robotics cells routinely expose "run named ControlProgram P with
  arguments" or "call vendor method M". This is *not* `move_to`,
  `grasp`, or `report`, and — unlike RFC-0013's `swap_tool`, which
  legitimately rides `send_docking_goal` because it *is* a station
  service — a general program/method call is not a station service.
  No existing primitive composes it. Filed as RFC-0015 (Draft); until
  accepted, the adapter exposes only nav/dock/grasp/measure/report and
  does not invent a primitive.

- **RFC-0016 — Real-time / cyclic manifest block.** A fieldbus/OPC UA
  cell often has a cyclic update period, a watchdog, and a requested
  packet interval (RPI). The Layer-1 manifest has no block to declare
  these, so a runtime cannot state the timing contract it operates
  under. This is a manifest-schema field, not a primitive. Filed as
  RFC-0016 (Draft); v0.1 ships without it (timing is deployment config
  in `opcua_adapter.yaml`, not URML-declared).

## Composable (no gap, documented)

- **Station services** (e.g. `swap_tool`, `park`) → `send_docking_goal`
  with the service name, exactly the RFC-0013 path. Preserved
  unchanged; `service_to_method` in `OpcUaConfig` maps it.
- **Per-location motion** → `send_navigation_goal(location=...)` →
  configured method node. Named-pose only (the companion spec is
  method/node oriented); raw pose goals return an honest unsuccessful
  result, not a gap.

## Maintainer ratification flag (not a spec gap)

`asyncua` is **LGPL-3.0**. In-repo code is Apache-2.0 and depends on it
**only** via the optional `[opcua]` extra, never imported at module
load (the same posture as `rclpy` / `pymavlink`), so the Core
Commitment boundary is intact and this runtime is outside that
boundary regardless. Whether an LGPL optional dependency in a
reference runtime is acceptable is a licensing-posture call for the
maintainer to ratify on this PR. Fallback if rejected: gate the OPC UA
server-integration to CI only, or vendor a minimal pure-Apache client.
