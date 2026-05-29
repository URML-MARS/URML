---
rfc: 0209
title: Eclipse Zenoh (next-generation pub-sub overlay substrate) integration, request for comment from Zenoh maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0209: Eclipse Zenoh (next-generation pub-sub overlay substrate) integration

## Summary

URML's primary substrate today is ROS 2 with DDS RMW; Eclipse Zenoh is the substrate-emerging next-generation pub-sub overlay protocol with an `rmw_zenoh` ROS 2 binding under active development. This RFC documents the proposed URML v0.1 capability-manifest mapping for the pub-sub-overlay-substrate class, engaged at the Eclipse Foundation governance layer via [`eclipse-zenoh/zenoh`](https://github.com/eclipse-zenoh/zenoh) (Other — EPL-2.0 / Apache-2.0), and **requests review and feedback from the Zenoh maintainers**. No spec change.

This is a **Tier B substrate-emerging** engagement (not yet default RMW). Second of three Eclipse Foundation engagements in Move-16 (Cyclone DDS sibling [RFC-0204](0204-cyclone-dds-outreach.md), Zenoh, iceoryx sibling [RFC-0210](0210-iceoryx-outreach.md)).

## Motivation

Zenoh's protocol stack offers a different topology model from DDS: data-centric, location-transparent, with native bridges to MQTT, Kafka, and WebSocket. The ROS 2 community is actively evaluating `rmw_zenoh` for production scenarios where DDS discovery / multicast becomes a bottleneck (large fleets, WAN-spanning deployments).

Repo at [`eclipse-zenoh/zenoh`](https://github.com/eclipse-zenoh/zenoh) (Other — EPL-2.0 / Apache-2.0, 2.8k stars, Issues enabled, last commit `2026-05-28`, **not archived**). Eclipse Foundation governance.

URML benefits from documenting the engagement because:

1. **Substrate-emerging declaration.** Zenoh is not ROS 2 default RMW today; URML's manifest could mark `substrate.rmw_implementation: rmw_zenoh_cpp` as substrate-emerging tier explicitly to surface the migration path.
2. **Multi-protocol bridge declaration.** Zenoh's native MQTT / Kafka / WebSocket bridges open URML's manifest to non-DDS topologies (cloud-to-edge, browser-to-robot); the manifest could declare which bridges are active.
3. **Eclipse Foundation alignment.** Zenoh joins Cyclone DDS (RFC-0204) and iceoryx (RFC-0210) as the third Eclipse Foundation engagement in Move-16; engagement at Zenoh's repo is the first of three sibling RFCs likely to converge to an Eclipse Foundation-level conversation.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_zenoh_cell.yaml` fixture)

| URML field | Maps to Zenoh attribute |
|---|---|
| `name` | Deployment handle (`ros2_jazzy_zenoh`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `substrate.rmw_implementation: rmw_zenoh_cpp` | URML's Zenoh RMW-implementation enum value |
| `substrate.maturity_tier: emerging` | URML's first substrate-maturity tier (Zenoh is sub-stable in ROS 2 today) |
| `network.zenoh_router_endpoint` | Zenoh router endpoint URI list |
| `network.zenoh_mode` | peer / client / router topology |
| `bridge.mqtt` / `bridge.kafka` / `bridge.websocket` | Zenoh bridge declaration |

### What URML v0.1 does not yet express for Zenoh

1. **Substrate-maturity-tier enum.** First-class field for substrate-emerging-vs-stable declaration; URML's first.
2. **Zenoh-mode topology declaration.** peer / client / router — URML's manifest has no topology field today.
3. **Multi-protocol-bridge declaration.** MQTT / Kafka / WebSocket bridges enable hybrid topologies URML's manifest currently cannot describe.
4. **Zenoh router endpoint URI list.** Router topology requires explicit endpoint declaration in production.

### Compatibility notes

- **Vendor org.** [`eclipse-zenoh`](https://github.com/eclipse-zenoh) — Eclipse Foundation.
- **Engagement repo.** [`eclipse-zenoh/zenoh`](https://github.com/eclipse-zenoh/zenoh) — Other (EPL-2.0 / Apache-2.0), 2.8k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `eclipse-zenoh/zenoh-plugin-ros2dds`, `eclipse-zenoh/zenoh-bridge-mqtt`, `eclipse-zenoh/zenoh-bridge-kafka`, `ros2/rmw_zenoh` (under ROS 2 org) — the Zenoh ecosystem.
- **Origin.** Eclipse Foundation. NATO-allied; passes US-federal default policy.
- **License fit.** Dual-licensed EPL-2.0 / Apache-2.0; URML can compose against the Apache-2.0 side cleanly.
- **Maintainer signal.** Active commits; the substrate-emerging pub-sub overlay.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; substrate-maturity-tier enum + Zenoh-mode + multi-protocol-bridge declaration + router-endpoint Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter is RMW-agnostic; Zenoh is `rmw_zenoh_cpp` env-var substitution today. Manifest-side declaration is the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Substrate-emerging tier risk** — Zenoh's `rmw_zenoh` is not ROS 2 default; URML's first substrate-maturity-tier declaration must remain useful as Zenoh maturity changes.
- **Multi-protocol-bridge semantic burden** — bridges open URML's manifest to MQTT / Kafka / WebSocket topologies, each with their own protocol semantics.
- **Parallel-RFC engagement load** — Cyclone DDS (sibling RFC-0204) and iceoryx (sibling RFC-0210) are the parallel Eclipse Foundation engagements.

## Alternatives considered

1. **Skip Zenoh until `rmw_zenoh` is ROS 2 default.** Rejected. Substrate-emerging engagement happens before defaults shift; URML's substrate-neutral claim requires the engagement to exist before the substrate is dominant.
2. **Engage at Eclipse Foundation meta layer (Cyclone DDS + Zenoh + iceoryx combined).** Considered. Per-project Issue engagement is the lowest-friction first-contact; foundation-level conversation stays open as escalation.
3. **Bundle Zenoh with iceoryx in a single Eclipse-IPC RFC.** Rejected. Zenoh is pub-sub overlay (network); iceoryx is zero-copy IPC (intra-host). Different layers, different concerns; per-project RFCs let conversation thread per group.

## Prior art

- [`eclipse-zenoh/zenoh`](https://github.com/eclipse-zenoh/zenoh) — the upstream Zenoh stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md), [RFC-0210 (iceoryx outreach)](0210-iceoryx-outreach.md) — sibling Move-16 RFCs under shared Eclipse Foundation governance.

## Unresolved questions

For the Eclipse Zenoh maintainers:

1. **Substrate-maturity-tier enum.** URML's first; preferred manifest value for Zenoh (`emerging`, `experimental`, `production-ready`)?
2. **RMW-implementation enum value.** `rmw_zenoh_cpp` (verbose) or `zenoh` (substrate-class-side)?
3. **Zenoh-mode topology declaration.** peer / client / router — manifest field shape?
4. **Multi-protocol-bridge declaration.** MQTT / Kafka / WebSocket bridges — should URML's manifest declare bridge-set as a list, or as separate fields per bridge?
5. **Router endpoint URI list.** Production router topology requires URI list; URML's preferred field shape?
6. **Eclipse Foundation-level engagement.** Is per-project Issue engagement the right first-contact, or should URML pursue Eclipse Foundation project-collaboration?
7. **Conformance listing.** Would Zenoh / Eclipse Foundation consider a project link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0209 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`eclipse-zenoh/zenoh` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the substrate-emerging + Eclipse-Foundation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Other — EPL-2.0 / Apache-2.0, 2.8k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (substrate-emerging tier risk, multi-protocol-bridge semantic burden, parallel-RFC engagement load).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Eclipse Foundation; NATO-allied; default policy passes.
- [x] CLAUDE.md compliance check passed.
