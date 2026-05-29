---
rfc: 0255
title: substrate.ipc_substrate — declaring zero-copy intra-process IPC in the Layer-1 manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
supersedes: —
superseded-by: —
---

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

# RFC-0255: `substrate.ipc_substrate` — declaring zero-copy IPC

## Summary

URML's manifest declares `substrate.class: ros2` (and via sibling RFC-0251, `substrate.rmw_implementation`) but does not declare the IPC sub-substrate that handles intra-process zero-copy transport. Production high-throughput deployments (camera images, lidar point clouds) commonly use Eclipse iceoryx as a shared-memory backend below the RMW. URML's manifest cannot today express that choice. This RFC adds `substrate.ipc_substrate` to the Layer-1 manifest with a closed enum, an `ipc_options` sub-block, and defines validator behavior. Optional. Backward compatible.

The surface that demanded this RFC is Move-16 RFC-0210 (Eclipse iceoryx outreach).

## Motivation

RMW choice (RFC-0251) and IPC choice (this RFC) are independent degrees of freedom. A deployment running Fast DDS can also run iceoryx underneath for intra-process zero-copy; a deployment running Cyclone DDS can do the same. URML's manifest needs both fields to express the deployment configuration honestly.

Three concrete consequences:

1. **High-throughput dispatch correctness.** URML's manifest cannot statically describe a deployment that relies on zero-copy IPC for camera or point-cloud paths. A maintainer reading the manifest cannot tell whether the deployment expects iceoryx shared-memory or whether it falls through to standard DDS copies.
2. **iceoryx vs iceoryx2 generation.** iceoryx (C++) is production. iceoryx2 (Rust rewrite) is sub-stable. URML's manifest needs to declare which generation the deployment targets, with `substrate.maturity_tier` (RFC-0254) classifying the choice honestly.
3. **Memory-pool budgets are deployment-critical.** iceoryx requires a shared-memory pool budget configured per RouDi daemon instance. URML's manifest can declare the budget as a hint that the validator surfaces in reports and that downstream tooling consumes.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_cyclonedds_cpp
  ipc_substrate: iceoryx                    # NEW — this RFC
  ipc_options:                              # NEW — optional
    generation: iceoryx1                    # iceoryx1 | iceoryx2
    shared_memory_pool_mb: 512              # budget hint
    roudi_runtime_name: roudi               # iceoryx daemon name
    max_publishers: 32
    max_subscribers: 64
```

### Allowed values

| Value | Description | Reference |
|---|---|---|
| `iceoryx` | Eclipse iceoryx (C++) | RFC-0210 |
| `iceoryx2` | Eclipse iceoryx2 (Rust rewrite) | RFC-0210 (sister track) |
| `none` | Deployment does not use IPC layer below RMW | n/a |
| `custom` | Vendor-specific or experimental IPC | escape hatch + `ipc_substrate_note` required |

`iceoryx` and `iceoryx2` are separate enum values rather than combined-with-generation-field because they are distinct upstream projects with separate Apache-2.0 licenses, separate APIs, and separate operational characteristics. The `generation` sub-field exists to capture the iceoryx1 / iceoryx2 split when the maintainer-side selection allows fallback ordering.

### Schema fragment (Layer-1)

```jsonc
{
  "substrate": {
    "properties": {
      "ipc_substrate": {
        "type": "string",
        "enum": ["iceoryx", "iceoryx2", "none", "custom"]
      },
      "ipc_substrate_note": { "type": "string" },
      "ipc_options": {
        "type": "object",
        "properties": {
          "generation": { "enum": ["iceoryx1", "iceoryx2"] },
          "shared_memory_pool_mb": { "type": "integer", "minimum": 1 },
          "roudi_runtime_name": { "type": "string" },
          "max_publishers": { "type": "integer", "minimum": 1 },
          "max_subscribers": { "type": "integer", "minimum": 1 }
        }
      }
    },
    "if": {
      "properties": { "ipc_substrate": { "const": "custom" } }
    },
    "then": {
      "required": ["ipc_substrate_note"]
    }
  }
}
```

### Validator behavior

1. **Optional field.** Missing field means no IPC declaration. URML does not infer iceoryx from RMW choice; the declaration is explicit.
2. **Custom note required.** `ipc_substrate: custom` requires non-empty `ipc_substrate_note`.
3. **Generation consistency.** If `ipc_substrate: iceoryx`, `ipc_options.generation` may be `iceoryx1` (default) or `iceoryx2` (fallback declaration). If `ipc_substrate: iceoryx2`, generation must be `iceoryx2` if specified.
4. **iceoryx2 maturity warning.** When `ipc_substrate: iceoryx2` or `ipc_options.generation: iceoryx2`, the validator emits a warning unless `substrate.maturity_tier` is `emerging` or `experimental` (RFC-0254). The warning recommends explicit maturity-tier declaration.
5. **Forward-compat.** Closed enum.

### Reference-runtime behavior

`reference/ros2-runtime/` reads `ipc_substrate` for startup-log diagnostics. When `iceoryx` is declared, the runtime sets the RMW-side iceoryx-enabled flag (Cyclone DDS supports `iceoryx` via `iceoryx_psmx`; Fast DDS supports via `shared_memory` transport). The runtime does not start RouDi itself; deployment-side orchestration owns the daemon lifecycle. URML's manifest declares the expectation; the deployment runs it.

### Conformance test additions

`conformance/tests/test_manifest_ipc_substrate.py`:

1. Manifest without `ipc_substrate` field passes (optional).
2. Manifest with `ipc_substrate: iceoryx` passes.
3. Manifest with `ipc_substrate: iceoryx2` and no `maturity_tier: emerging` passes with warning.
4. Manifest with `ipc_substrate: iceoryx2` and `maturity_tier: emerging` passes without warning.
5. `ipc_substrate: custom` without note fails.

## Backward compatibility

Pre-v1.0. Additive: missing field defaults to no IPC declaration. No migration required.

## Drawbacks

- **iceoryx1 vs iceoryx2 split is a maintenance burden.** Two enum values plus a sub-field for generation. The Rust rewrite (iceoryx2) is the future direction; URML's discipline is to accept both today and let the maturity_tier field classify the readiness honestly.
- **Manifest does not capture RMW-side iceoryx enablement.** Cyclone DDS and Fast DDS each have their own way to enable iceoryx (Cyclone via `iceoryx_psmx` plugin, Fast DDS via `shared_memory` transport configuration). URML's manifest declares the intent; the per-RMW configuration glue lives in the RMW's own config file (referenced via `rmw_options.config_reference` in RFC-0251).
- **Memory-pool budget is a hint, not enforcement.** URML's validator cannot check that the deployment host actually has the declared memory available. The field surfaces intent; runtime verification is RouDi's job.

## Alternatives considered

1. **Skip the field; let RMW choice imply IPC choice.** Rejected. IPC is a real independent degree of freedom; production users routinely override IPC per-deployment.
2. **Single field combining IPC + generation.** Rejected. iceoryx vs iceoryx2 are distinct upstream projects, not generations of the same project; combining loses precision.
3. **Defer iceoryx2 enum value until iceoryx2 ships v1.0.** Rejected. URML's substrate-emerging tier (RFC-0254) is the right way to mark iceoryx2's status; refusing the value would close URML to deployments already using iceoryx2.
4. **Per-topic IPC overrides.** Rejected for v0.1 of this field. Deployment-wide IPC is the standard pattern; per-topic overrides are future work.

## Prior art

- [RFC-0210 (Eclipse iceoryx outreach)](0210-iceoryx-outreach.md) — the outreach RFC that surfaced this field.
- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — the RMW field that pairs with this IPC field.
- [RFC-0254 (substrate.maturity_tier)](0254-substrate-maturity-tier.md) — classifies iceoryx2 as substrate-emerging at validate time.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent ROS 2 substrate engagement.

## Unresolved questions

1. **Multi-IPC deployments.** A deployment with mixed-namespace IPC choices is unusual today but possible. v0.1 of this field assumes single IPC per deployment.
2. **iceoryx2 ↔ iceoryx1 fallback semantics.** When `ipc_options.generation: iceoryx2-preferred-fallback-iceoryx1` is the deployment intent, how URML's runtime should handle the fallback is unresolved. Sibling future RFC.
3. **Cross-RMW IPC portability.** iceoryx via Cyclone DDS vs iceoryx via Fast DDS may have subtly different behavior; URML's manifest does not capture per-RMW IPC quirks today.

## Implementation plan

1. JSON Schema fragment.
2. Validator with iceoryx2 maturity warning.
3. Conformance tests.
4. Reference-runtime startup-log addition.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Three alternatives considered (four total).
- [x] Drawbacks named honestly.
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs and sibling Spec RFCs (0251, 0254).
- [x] CLAUDE.md compliance: enum closure preserves substrate moat; maturity_tier cross-link surfaces iceoryx2 status honestly.
