---
rfc: 0305
title: Eclipse iceoryx2 (decentralized zero-copy IPC successor) integration, request for comment from iceoryx2 maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-01
updated: 2026-06-01
state: Draft
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

# RFC-0305: Eclipse iceoryx2 (decentralized zero-copy IPC successor) integration

## Summary

URML's substrate manifest declares the RMW middleware class but does not declare the IPC sub-substrate (zero-copy intra-process transport). [RFC-0210](0210-iceoryx-outreach.md) opened that engagement against the C++ `iceoryx`. During that thread ([`eclipse-iceoryx/iceoryx#2530`](https://github.com/eclipse-iceoryx/iceoryx/issues/2530), 2026-06-01) maintainer @elBoberido confirmed that the team's focus has **fully shifted to `iceoryx2`**, the Rust successor. This RFC retargets the IPC-substrate mapping to [`eclipse-iceoryx/iceoryx2`](https://github.com/eclipse-iceoryx/iceoryx2) (Apache-2.0), reframes it around iceoryx2's decentralized architecture, and **requests review and feedback from the iceoryx2 maintainers**. No spec change.

This is a **Tier B IPC-substrate** engagement and the live successor to RFC-0210. It does not retract RFC-0210; that thread remains the origin of the conversation and the meetup invitation.

## Motivation

iceoryx2 is the active generation of the Eclipse zero-copy IPC stack. It keeps iceoryx's true zero-copy shared-memory transport for high-frequency-large-payload paths (camera images, lidar point clouds) and changes the architecture in one way that matters for URML's manifest: it is **decentralized**. The central RouDi daemon that iceoryx1 required is gone. There is no broker to name; a deployment is a set of nodes and services configured from a global config rather than registered against a daemon.

RFC-0210's mapping assumed RouDi (`ipc.runtime_name`). That field does not survive the move to iceoryx2. The rest of the IPC-substrate declaration (generation, memory budget, pub/sub counts) carries over, with the daemon-name slot replaced by a config-path slot and a messaging-pattern slot.

Repo at [`eclipse-iceoryx/iceoryx2`](https://github.com/eclipse-iceoryx/iceoryx2) (Apache-2.0, Eclipse Foundation governance). The C++ `iceoryx` continues in maintenance; new IPC-substrate work in URML should target iceoryx2.

URML benefits from documenting the engagement because:

1. **IPC-substrate declaration is URML's missing manifest sub-layer.** RMW choice and IPC choice are independent degrees of freedom; URML's manifest could declare both for production determinism.
2. **The generation transition is now concrete.** iceoryx1 (C++, RouDi-based) and iceoryx2 (Rust, decentralized) are materially different substrates. URML's manifest must let a deployment declare which it runs, and the maintainers have now told us which is the default going forward.
3. **Decentralized config replaces the daemon.** iceoryx2's per-deployment configuration is a global config rather than a named RouDi runtime; URML's manifest hint should reflect that.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_iceoryx2_cell.yaml` fixture)

| URML field | Maps to iceoryx2 attribute |
|---|---|
| `name` | Deployment handle (`ros2_humble_iceoryx2`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `substrate.ipc_substrate: iceoryx2` | IPC-substrate enum value |
| `substrate.ipc_generation: iceoryx2` | iceoryx2 generation (the recommended default per maintainer guidance) |
| `ipc.config_path` | iceoryx2 global config (replaces iceoryx1's RouDi runtime name) |
| `ipc.messaging_pattern: pub_sub` / `event` / `request_response` | iceoryx2 service messaging pattern |
| `ipc.shared_memory_budget_mb` | iceoryx2 shared-memory budget hint |
| `ipc.max_publisher_count` / `ipc.max_subscriber_count` | iceoryx2 service port budgets |

### What URML v0.1 does not yet express for iceoryx2

1. **IPC-substrate enum value `iceoryx2`.** Sibling to RFC-0210's proposed `iceoryx`; the two coexist as generations.
2. **Decentralized config-path field.** Replaces the RouDi-runtime-name field; iceoryx2 has no central daemon to name.
3. **Messaging-pattern field.** iceoryx2 exposes publish-subscribe, event, and request-response patterns per service; URML's manifest could declare the pattern a service uses.
4. **Shared-memory budget hint.** Carried over from RFC-0210; iceoryx2's memory model differs and the hint shape should follow it.

### Compatibility notes

- **Vendor org.** [`eclipse-iceoryx`](https://github.com/eclipse-iceoryx) — Eclipse Foundation.
- **Engagement repo.** [`eclipse-iceoryx/iceoryx2`](https://github.com/eclipse-iceoryx/iceoryx2) — Apache-2.0, the actively developed generation (maintainer-confirmed primary focus 2026-06-01).
- **Predecessor repo.** [`eclipse-iceoryx/iceoryx`](https://github.com/eclipse-iceoryx/iceoryx) — C++, now maintenance; origin of RFC-0210 and issue #2530.
- **Origin.** Eclipse Foundation. NATO-allied; passes US-federal default policy.
- **License fit.** Apache-2.0. Clean fit.
- **Maintainer signal.** @elBoberido (member) invited URML to the iceoryx2 developer meetup (monthly, first Tuesday 17:00 CEST) and confirmed iceoryx2 as the team's focus.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. The IPC-substrate enum, IPC-generation field, config-path, messaging-pattern, and memory-budget hint are queued Spec RFCs (shared with RFC-0210's queued work; iceoryx2 is an added enum value plus the config-path / messaging-pattern fields).
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter is IPC-agnostic today; iceoryx2 is RMW-side configuration. Manifest-side declaration is the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). RFC-0210 stands; this RFC adds the iceoryx2 generation as a sibling target.

## Drawbacks

- **Proposal-only.**
- **Two live targets for one substrate family.** RFC-0210 (iceoryx1) and RFC-0305 (iceoryx2) both exist. Justified: they are different architectures (RouDi vs decentralized), and the maintainers run one meetup for both. The generation field is what keeps the manifest honest about which one a deployment uses.
- **iceoryx2 surface is younger.** APIs are evolving faster than iceoryx1's; a manifest mapping pinned today may need revision. The mapping is documented as v0.1 and revisable by RFC.
- **Decentralized-config semantics need care.** With no daemon, the config-path field carries more weight; its semantics need definition in the queued Spec RFC.

## Alternatives considered

1. **Amend RFC-0210 in place instead of a new RFC.** Rejected. RFC-0210's thread (#2530) is the historical record of the iceoryx1 engagement and the meetup invitation; rewriting it to be about iceoryx2 would erase that trail. A sibling RFC preserves both and matches URML's per-target convention.
2. **Drop iceoryx1 entirely and keep only iceoryx2.** Rejected. iceoryx1 is still deployed in production ROS 2 stacks; URML's manifest should still be able to declare it. The generation field handles the coexistence.
3. **Fold the config-path / messaging-pattern fields into RFC-0210's queued Spec RFC without a separate outreach.** Considered. The Spec work is shared, but the iceoryx2 architecture is different enough (no RouDi, messaging patterns) that a distinct request-for-comment gives the maintainers a clean thread.

## Prior art

- [RFC-0210 (Eclipse iceoryx outreach)](0210-iceoryx-outreach.md) — predecessor; the iceoryx1 engagement whose thread surfaced the iceoryx2 focus shift.
- [`eclipse-iceoryx/iceoryx2`](https://github.com/eclipse-iceoryx/iceoryx2) — the upstream Rust stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0203 (Fast DDS outreach)](0203-fast-dds-outreach.md), [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md) — sibling Move-16 RFCs; the RMW layer above iceoryx2.
- [RFC-0209 (Zenoh outreach)](0209-zenoh-outreach.md) — sibling Move-16 RFC under shared Eclipse Foundation governance.

## Unresolved questions

For the Eclipse iceoryx2 maintainers:

1. **Recommended generation default.** With the team's focus on iceoryx2, should URML's manifest default the IPC generation to `iceoryx2`, and how should it express an iceoryx1 deployment (legacy / maintenance)?
2. **Decentralized config declaration.** With no RouDi daemon, is a global-config-path field the right manifest shape for iceoryx2, or is there a more idiomatic deployment handle?
3. **Messaging-pattern declaration.** iceoryx2 exposes publish-subscribe, event, and request-response patterns. Should URML's manifest declare the pattern per service, and at what granularity?
4. **Shared-memory budget hint.** iceoryx2's memory model differs from iceoryx1's pools; what budget-hint shape would the maintainers prefer for envelope-validation?
5. **Cross-language bindings.** iceoryx2 ships Rust, C, C++, and Python bindings. Does the manifest need to declare the binding a deployment uses, or is that out of scope for an intent-level substrate declaration?
6. **Conformance listing.** Would iceoryx2 / the Eclipse Foundation consider a project link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0305 ships as a single RFC document PR. Ledger entry shared with the `eclipse-iceoryx` row in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml) (the engagement is one conversation across two generations); a dedicated iceoryx2 ledger row is added if the engagement forks.

## How to respond

The live channel is the iceoryx2 developer meetup (monthly, first Tuesday 17:00 CEST) and the existing thread [`eclipse-iceoryx/iceoryx#2530`](https://github.com/eclipse-iceoryx/iceoryx/issues/2530). If the maintainers prefer a formal home on the iceoryx2 repo, URML will open an Issue or Discussion there pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (Apache-2.0, Eclipse Foundation, iceoryx2 maintainer-confirmed as primary focus via #2530).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (two live targets for one family, younger surface, decentralized-config semantics).
- [x] Backward compatibility additive; RFC-0210 preserved.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Eclipse Foundation; NATO-allied; default policy passes.
- [x] CLAUDE.md compliance check passed (substrate-neutral; iceoryx2 is one IPC substrate among many, declared not assumed).
