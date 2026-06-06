---
rfc: 0385
title: substrate.ipc, declaring the zero-copy IPC sub-substrate (iceoryx generation)
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0385: substrate.ipc, declaring the zero-copy IPC sub-substrate (iceoryx generation)

## Summary

URML's `substrate` block declares the drone autopilot class (RFC-0250) and the ROS 2 RMW middleware (RFC-0251), but not the **IPC sub-substrate**: the zero-copy shared-memory transport beneath the RMW that carries high-frequency, large-payload data (camera images, lidar clouds). This RFC adds an optional `substrate.ipc` block declaring that transport, specifically the Eclipse iceoryx generation in use, and the validator checks it for coherence. The change is additive, backward compatible, and ships with its implementation.

## Motivation

This converts a gap two engaged outreach threads named into normative surface. [RFC-0210](0210-iceoryx-outreach.md) opened an engagement against the C++ `iceoryx`; during that thread ([`eclipse-iceoryx/iceoryx#2530`](https://github.com/eclipse-iceoryx/iceoryx/issues/2530)) maintainer @elBoberido confirmed the team's focus has fully shifted to the Rust successor `iceoryx2` and invited URML to the developer meetup. [RFC-0305](0305-iceoryx2-outreach.md) retargeted the mapping to iceoryx2. Both are outreach RFCs that explicitly proposed **no spec change**; each pointed at the same missing manifest surface. The `Substrate` model's own docstring already listed `ipc_substrate` as a planned field. This RFC is that field.

The reason it matters for validation: iceoryx1 and iceoryx2 are materially different substrates. iceoryx1 is built around the central RouDi daemon; a deployment registers against a named broker. iceoryx2 is decentralized, the RouDi daemon is gone, and a deployment is configured from a global config file. A manifest that cannot say which generation it runs cannot be checked for the daemon-vs-config coherence that distinguishes them, and a request validated against the wrong assumption is a validated-but-wrong result.

## Detailed design

An optional `ipc` block on `substrate`:

```yaml
substrate:
  ipc:
    generation: iceoryx2          # iceoryx1 | iceoryx2 | custom
    config_path: /etc/iceoryx2/config.toml
    messaging_pattern: pub_sub    # pub_sub | request_response | event
    shared_memory_budget_mb: 256.0
    max_publishers: 8
    max_subscribers: 16
```

`IpcSubstrate` fields: `generation` (closed enum, required), `runtime_name` (the RouDi daemon, iceoryx1), `config_path` (the decentralized global config, iceoryx2), `generation_note` (free text, required for `custom`), `messaging_pattern`, `shared_memory_budget_mb` (≥ 0), `max_publishers` / `max_subscribers` (≥ 0). All but `generation` are optional; the carry-over fields (memory budget, pub/sub counts, messaging pattern) are RFC-0305's mapping realized as schema.

### Validator changes

A whole-manifest Pass-2 check (`_check_substrate_ipc`) enforces generation coherence, mirroring the RFC-0251 `rmw_implementation == 'custom'` rule:

- `iceoryx1` requires `runtime_name` → `capability.ipc_runtime_name_required`;
- `iceoryx2` requires `config_path` → `capability.ipc_config_path_required`, and forbids `runtime_name` (RouDi is gone) → `capability.ipc_runtime_name_not_applicable`;
- `custom` requires `generation_note` → `capability.ipc_generation_note_required`.

No existing pass changes for a manifest without `substrate.ipc`.

### Relationship to RFC-0210 / RFC-0305

Those remain outreach RFCs (the request-for-comment to the iceoryx maintainers); this is the spec realization they each deferred. RFC-0305's `runtime_name → config_path` retarget is exactly the iceoryx1-vs-iceoryx2 coherence rule implemented here.

## Backward compatibility

Fully additive. `substrate.ipc` is optional; absent, behavior is identical. `manifest_version` stays `"0.1"`. Every existing manifest, program, fixture, and runtime is unaffected. Validator-only: no runtime adapter changes (the reference runtimes consume the validated manifest).

## Drawbacks

Naming a specific vendor stack (iceoryx) in a closed enum risks coupling the spec to one ecosystem. Mitigation: `generation: custom` + `generation_note` is the documented escape hatch (the same pattern as `autopilot_class: custom` and `rmw_implementation: custom`), so a non-iceoryx zero-copy bus is expressible without a spec change. The field stays a *declaration* the validator checks for internal coherence; URML does not configure or manage the IPC transport.

## Alternatives considered

- **A free-form `ipc: {vendor, config}` blob**: rejected. It cannot carry the one rule that matters (daemon vs decentralized config), so the validator could not catch an iceoryx2 manifest that still names a RouDi daemon.
- **Fold into `rmw_options`**: rejected. The IPC transport sits *beneath* the RMW and can exist under different RMWs (or none); it deserves its own sibling field, the way `autopilot_class` and `rmw_implementation` are siblings.
- **Defer until a `substrate.class` field exists** (as RFC-0251 deferred its ros2-required rule): rejected. The coherence rule here is intrinsic to the `ipc` block itself (it needs no outer class), so it can ship now.

## Prior art

Eclipse iceoryx (RouDi-based, C++) and iceoryx2 (decentralized, Rust); zero-copy shared-memory transports generally (eCAL, Fast DDS SHM). URML-internal: RFC-0250 (`autopilot_class`) and RFC-0251 (`rmw_implementation`), whose closed-enum-plus-custom-note discipline this follows exactly; RFC-0210 / RFC-0305 (the iceoryx engagement this realizes).

## Unresolved questions

- Whether `messaging_pattern`, `shared_memory_budget_mb`, and the pub/sub counts should gain validator rules (e.g. budget vs declared payload sizes). They are declared and range-checked now; a cross-field rule waits for a payload-size declaration to check against.
- Whether a future `substrate.class` (ros2 / autosar / opcua / …) should make `ipc` required for shared-memory-class deployments, paralleling RFC-0251's deferred ros2 rule.

## Implementation note

Ships as one vertical slice (spec → schema → validator → conformance), the RFC-0250/0251 pattern: a substrate-block widening with no semantic fork, so RFC and implementation land together. Schema: `IpcSubstrate` + `Substrate.ipc`. Validator: `_check_substrate_ipc` + four error codes. Conformance: five `substrate_ipc_*` manifests + five fixtures (one positive iceoryx2, four coherence rejections). Validator unit tests in `test_substrate_ipc.py` cover all four codes plus the positive and no-block paths.

## Self-review (Phase 0)

- [x] The Summary alone says what is added and that it ships implemented.
- [x] The Motivation is grounded in a concrete, in-tree engagement (RFC-0210/0305, iceoryx#2530), not a hypothetical.
- [x] More than one alternative is genuinely considered; the chosen shape is marked and the custom escape hatch named.
- [x] Backward compatibility is explicit (additive, optional, pre-v1.0).
- [x] Drawbacks are honest, including the vendor-coupling risk and how the custom hatch contains it.
- [x] Every normative addition has a check, a conformance fixture, and unit tests (the URML bar for new surface).
