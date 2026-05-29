---
rfc: 0203
title: eProsima Fast DDS (ROS 2 default DDS substrate) integration, request for comment from Fast DDS maintainers
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

# RFC-0203: eProsima Fast DDS (ROS 2 default DDS substrate) integration

## Summary

URML's ROS 2 reference runtime ships against Fast DDS by default (the ROS 2 stack's default RMW since Foxy). This RFC documents the proposed URML v0.1 capability-manifest mapping for the DDS-middleware-substrate class, engaged via [`eProsima/Fast-DDS`](https://github.com/eProsima/Fast-DDS) (Apache-2.0), and **requests review and feedback from the Fast DDS maintainers**. No spec change.

## Motivation

Fast DDS is the default DDS implementation under ROS 2 (RMW layer) since Foxy. URML's manifest currently declares `substrate.class: ros2` without a `substrate.rmw_implementation` field; the engagement is the natural place to surface the missing field and its semantics.

Repo at [`eProsima/Fast-DDS`](https://github.com/eProsima/Fast-DDS) (Apache-2.0, 2.8k stars, Issues enabled, last commit `2026-05-28`, **not archived**). eProsima ES (Tres Cantos, Madrid) commercial vendor-direct; OMG DDS standard implementation.

URML benefits from documenting the engagement because:

1. **RMW implementation declaration is URML's missing manifest layer.** URML's substrate field today is ROS 2-coarse; declaring the RMW implementation is needed for production-deployment determinism (QoS-profile interpretation differs between Fast DDS and Cyclone DDS at corner cases).
2. **DDS QoS profile semantics.** URML's manifest could declare reliability / durability / history / deadline / lifespan; the Fast DDS team is the right group to validate URML's QoS-field shape against the OMG DDS specification.
3. **DDS-Security extension.** Fast DDS implements DDS-Security; URML's authentication and access-control story (currently no manifest field) could surface here.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_fastdds_cell.yaml` fixture)

| URML field | Maps to Fast DDS attribute |
|---|---|
| `name` | Deployment handle (`ros2_humble_fastdds`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `substrate.rmw_implementation: rmw_fastrtps_cpp` | URML's first RMW-implementation enum value |
| `qos.reliability` | Fast DDS RELIABLE_RELIABILITY_QOS / BEST_EFFORT_RELIABILITY_QOS |
| `qos.durability` | Fast DDS VOLATILE / TRANSIENT_LOCAL / TRANSIENT / PERSISTENT |
| `qos.history` | Fast DDS KEEP_LAST / KEEP_ALL + depth |
| `qos.deadline_ms` | Fast DDS DEADLINE_QOS_POLICY |
| `qos.lifespan_ms` | Fast DDS LIFESPAN_QOS_POLICY |
| `discovery.protocol: simple` / `discovery_server` | Fast DDS Simple Discovery vs Discovery Server architecture |
| `security.profile` | Fast DDS DDS-Security profile reference (future) |

### What URML v0.1 does not yet express for Fast DDS

1. **RMW-implementation enum declaration.** First-class RMW-substrate field; URML's first.
2. **QoS profile manifest fields.** Reliability / durability / history / deadline / lifespan; these are vital for production deployments.
3. **Discovery-Server topology.** Fast DDS Discovery Server is a Fast DDS-specific scalability architecture; URML's manifest could declare `discovery.protocol` field.
4. **DDS-Security profile declaration.** Authentication, access-control, cryptographic-transform plugins; URML has no manifest field today.

### Compatibility notes

- **Vendor org.** [`eProsima`](https://github.com/eProsima) — commercial vendor (ES, Madrid). OMG DDS standard implementation.
- **Engagement repo.** [`eProsima/Fast-DDS`](https://github.com/eProsima/Fast-DDS) — Apache-2.0, 2.8k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `eProsima/Fast-CDR`, `eProsima/Discovery-Server`, `eProsima/Fast-DDS-Docs` — the Fast DDS ecosystem.
- **Origin.** eProsima ES (Tres Cantos, Madrid). NATO-allied (Spain); passes US-federal default policy as an allied-origin vendor.
- **License fit.** Apache-2.0. Clean fit.
- **Maintainer signal.** Daily-cadence commits; OMG DDS standard implementation; the ROS 2 default RMW since Foxy.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; RMW-implementation enum + QoS profile + Discovery-Server topology + DDS-Security profile Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter targets Fast DDS by default; manifest-side RMW + QoS fields are the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **QoS-profile semantic complexity** — DDS QoS is a deep standard surface; URML's manifest must expose just enough to be useful without leaking DDS implementation into URML's language layer.
- **Vendor-direct engagement** — eProsima is commercial (vs Eclipse Foundation Cyclone DDS sibling [RFC-0204](0204-cyclone-dds-outreach.md)); two parallel DDS engagements are the right shape but make for a heavier conversation surface.
- **DDS-Security profile is future work** — URML has no authentication / access-control manifest field today.

## Alternatives considered

1. **Engage at OMG (the standards body) instead of eProsima vendor-direct.** Rejected. OMG is the spec body; the implementation maintainers run the Issue tracker that production users actually hit.
2. **Engage Cyclone DDS only (Eclipse Foundation, non-commercial governance).** Rejected. Fast DDS is ROS 2's default RMW since Foxy; engaging it is mandatory. Sibling [RFC-0204 Cyclone DDS](0204-cyclone-dds-outreach.md) covers the Eclipse Foundation side.
3. **Bundle Fast DDS + Cyclone DDS in a single DDS-substrate RFC.** Rejected. Different governance (commercial vendor-direct vs Eclipse Foundation), different licenses (Apache-2.0 vs EPL-2.0); per-vendor RFCs let conversation thread per group.

## Prior art

- [`eProsima/Fast-DDS`](https://github.com/eProsima/Fast-DDS) — the upstream Fast DDS stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md) — sibling Move-16 batch-2 RFC; alternative DDS implementation.
- [RFC-0210 (iceoryx outreach)](0210-iceoryx-outreach.md) — sibling Move-16 batch-3 RFC; zero-copy IPC layer.

## Unresolved questions

For the eProsima Fast DDS maintainers:

1. **RMW-implementation enum manifest field.** First-class manifest field shape — should the field value be `rmw_fastrtps_cpp` (verbose ROS 2-side) or `fastdds` (substrate-class-side)?
2. **QoS profile manifest field set.** Reliability / durability / history / deadline / lifespan — URML's preferred field set for manifest-level declaration?
3. **Discovery-Server topology declaration.** Should URML's manifest declare Simple Discovery vs Discovery Server vs partition-based scaling?
4. **DDS-Security profile manifest field.** Authentication + access-control profile reference — URML's manifest could declare a profile path; the Fast DDS team's preferred shape?
5. **Multi-RMW deployment.** Should URML's manifest support declaring multiple RMW implementations per deployment (Fast DDS for some namespaces, Cyclone DDS for others), or is one-RMW-per-deployment the right constraint?
6. **Conformance listing.** Would eProsima consider an `eprosima.com` link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0203 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`eProsima/Fast-DDS` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the RMW-implementation + QoS-field framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0, 2.8k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (QoS-profile semantic complexity, vendor-direct engagement, DDS-Security profile future work).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: eProsima ES (NATO-allied, Spain); default policy passes.
- [x] CLAUDE.md compliance check passed.
