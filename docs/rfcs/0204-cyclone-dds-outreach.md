---
rfc: 0204
title: Eclipse Cyclone DDS (alternative ROS 2 DDS substrate) integration, request for comment from Cyclone DDS maintainers
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

# RFC-0204: Eclipse Cyclone DDS (alternative ROS 2 DDS substrate) integration

## Summary

URML's ROS 2 reference runtime targets the RMW layer rather than a specific DDS implementation; Cyclone DDS is the principal alternative to Fast DDS (sibling [RFC-0203](0203-fast-dds-outreach.md)). This RFC documents the proposed URML v0.1 capability-manifest mapping for the Cyclone-DDS substrate variant, engaged at the Eclipse Foundation governance layer via [`eclipse-cyclonedds/cyclonedds`](https://github.com/eclipse-cyclonedds/cyclonedds) (EPL-2.0), and **requests review and feedback from the Cyclone DDS maintainers**. No spec change.

## Motivation

Cyclone DDS is the Eclipse Foundation's DDS implementation and the most common alternative to Fast DDS in ROS 2 deployments. It is the default RMW in some downstream distributions (Autoware, Foxglove) and a deliberate choice in latency-sensitive deployments.

Repo at [`eclipse-cyclonedds/cyclonedds`](https://github.com/eclipse-cyclonedds/cyclonedds) (EPL-2.0, 1.3k stars, Issues enabled, last commit `2026-05-26`, **not archived**). Eclipse Foundation NL governance.

URML benefits from documenting the engagement because:

1. **EPL-2.0 → cross-citation framing.** Cyclone DDS is EPL-2.0; URML's Apache-2.0 adapter composes at the API boundary (cross-citation), not by embedding source. This is the same framing URML uses with other EPL-2.0 substrate components.
2. **Eclipse Foundation alignment.** Cyclone DDS, Eclipse Zenoh (sibling [RFC-0209](0209-zenoh-outreach.md)), and Eclipse iceoryx (sibling [RFC-0210](0210-iceoryx-outreach.md)) are three Move-16 engagements under shared Eclipse Foundation governance; engaging at the Cyclone DDS layer is the first of three.
3. **Performance-tier declaration.** Cyclone DDS's latency profile is materially different from Fast DDS at high-frequency control loops; URML's manifest could declare per-deployment RMW-implementation choice without losing portability.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_cyclonedds_cell.yaml` fixture)

| URML field | Maps to Cyclone DDS attribute |
|---|---|
| `name` | Deployment handle (`ros2_humble_cyclonedds`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `substrate.rmw_implementation: rmw_cyclonedds_cpp` | URML's Cyclone DDS RMW-implementation enum value |
| `qos.reliability` | Cyclone DDS RELIABILITY profile (reliable / best-effort) |
| `qos.durability` | Cyclone DDS DURABILITY profile |
| `qos.history` | Cyclone DDS HISTORY profile |
| `discovery.protocol: simple` / `cyclonedds_xml` | Simple Discovery vs Cyclone DDS-XML-configured topology |
| `network.uri` | Cyclone DDS network interface URI list |
| `security.profile` | Cyclone DDS-Security profile reference (future) |

### What URML v0.1 does not yet express for Cyclone DDS

1. **Cyclone DDS-specific configuration XML reference.** Cyclone DDS uses an XML configuration file for advanced tuning (interface lists, discovery scopes, network partitions); URML's manifest could declare the XML reference path.
2. **Network-partition declaration.** Cyclone DDS supports partition-based topology; URML's manifest currently has no partition concept.
3. **Cyclone DDS-Python binding declaration.** `cyclonedds-python` is an officially supported binding; URML's manifest could declare which DDS bindings are expected (C / C++ / Python).
4. **Performance-tier hints.** Cyclone DDS's `latency-budget` and `throughput-budget` QoS policies are particularly well-supported; URML's manifest could declare performance hints.

### Compatibility notes

- **Vendor org.** [`eclipse-cyclonedds`](https://github.com/eclipse-cyclonedds) — Eclipse Foundation NL.
- **Engagement repo.** [`eclipse-cyclonedds/cyclonedds`](https://github.com/eclipse-cyclonedds/cyclonedds) — EPL-2.0, 1.3k stars, Issues enabled, last commit 2026-05-26, **not archived**.
- **Companion repos.** `eclipse-cyclonedds/cyclonedds-python`, `eclipse-cyclonedds/cyclonedds-cxx` — the Cyclone DDS bindings.
- **Origin.** Eclipse Foundation NL. NATO-allied; passes US-federal default policy.
- **License fit.** EPL-2.0 → cross-citation framing at API boundary (URML's Apache-2.0 adapter cannot embed EPL-2.0 source but composes at the RMW boundary cleanly).
- **Maintainer signal.** Active commits; the principal Fast DDS alternative; Autoware default RMW.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; RMW-implementation enum (sibling [RFC-0203](0203-fast-dds-outreach.md)) + Cyclone DDS-XML configuration reference + partition-declaration Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter is RMW-agnostic; Cyclone DDS is a runtime substitution today (env var). Manifest-side declaration is the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **EPL-2.0 → cross-citation only at adapter boundary.** URML cannot embed Cyclone DDS source; the engagement is at the manifest and API layers.
- **XML-configuration dependency surface.** Cyclone DDS's XML configuration is its own format; URML's manifest indirectly depends on it.
- **Parallel-RFC engagement load** — Fast DDS (sibling RFC-0203) is the other parallel DDS engagement; conversation may converge to the OMG DDS standard layer.

## Alternatives considered

1. **Skip Cyclone DDS; declare only Fast DDS.** Rejected. URML's substrate-neutral claim requires multi-RMW support; ignoring Cyclone DDS biases URML toward eProsima's commercial implementation.
2. **Engage at Eclipse Foundation level rather than per-project repo.** Considered. Eclipse Cyclone DDS, Eclipse Zenoh, and Eclipse iceoryx are three Move-16 targets under shared Eclipse Foundation governance; per-project Issue engagement is the lowest-friction first-contact channel. A subsequent Eclipse Foundation-level conversation is possible if the maintainers prefer.
3. **Bundle Cyclone DDS with Fast DDS in a single DDS-substrate RFC.** Rejected. Different governance (Eclipse Foundation vs eProsima commercial), different licenses (EPL-2.0 vs Apache-2.0); per-vendor RFCs let conversation thread per group.

## Prior art

- [`eclipse-cyclonedds/cyclonedds`](https://github.com/eclipse-cyclonedds/cyclonedds) — the upstream Cyclone DDS stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0203 (Fast DDS outreach)](0203-fast-dds-outreach.md) — sibling Move-16 batch-2 RFC; default ROS 2 DDS implementation.
- [RFC-0209 (Zenoh outreach)](0209-zenoh-outreach.md), [RFC-0210 (iceoryx outreach)](0210-iceoryx-outreach.md) — sibling Move-16 batch-3 RFCs under shared Eclipse Foundation governance.

## Unresolved questions

For the Eclipse Cyclone DDS maintainers:

1. **RMW-implementation enum manifest field.** Manifest field shape preference — `rmw_cyclonedds_cpp` (verbose ROS 2-side) or `cyclonedds` (substrate-class-side)?
2. **Cyclone DDS-XML configuration reference.** Should URML's manifest declare an XML reference path, or stay XML-config-agnostic?
3. **Network-partition manifest field.** Cyclone DDS supports partition-based topology; should URML's manifest declare partitions?
4. **Performance-tier hint fields.** `latency-budget` and `throughput-budget` QoS policies are Cyclone DDS strengths; should URML's manifest declare per-deployment performance hints?
5. **Eclipse Foundation-level engagement.** Is per-project Issue engagement the right first-contact channel, or should URML pursue an Eclipse Foundation-level project-collaboration conversation?
6. **Cross-citation conventions.** URML proposes EPL-2.0 → API-boundary cross-citation in `reference/ros2-runtime/`; preferred attribution shape from the Cyclone DDS / Eclipse Foundation side?
7. **Conformance listing.** Would Cyclone DDS / the Eclipse Foundation consider a project link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0204 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`eclipse-cyclonedds/cyclonedds` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the alternative-RMW + EPL-2.0-cross-citation + Eclipse-Foundation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (EPL-2.0, 1.3k stars, Issues enabled, last commit 2026-05-26, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (EPL-2.0 cross-citation-only, XML-configuration dependency, parallel-RFC engagement load).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Eclipse Foundation NL; NATO-allied; default policy passes.
- [x] CLAUDE.md compliance check passed.
