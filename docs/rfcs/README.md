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

# URML RFCs

This directory is URML's decision history. Every change to the **specification** — adding or modifying a primitive, changing a schema, modifying behavior semantics, changing a profile, modifying the Core Commitment — happens here, not in a pull request.

The authoritative description of *how* RFCs work is [RFC-0001](0001-rfc-process.md). This file is just the index.

## Two kinds of RFC live here

The `docs/rfcs/` dir now holds two distinct kinds of document, marked by the
**Kind** column in the index below:

- **Spec** — changes URML's normative surface: Layer-1/2/3/4 schemas, new
  primitives, policy mechanism, profiles, the Core Commitment. These are
  RFCs in the canonical sense ([RFC-0001](0001-rfc-process.md) governs
  them) and going through Draft → Open → Accepted → Implemented is the
  way *the specification* changes. Numbered 0001–0022 at time of writing.
- **Outreach** — per-vendor request-for-comment documents. Each one
  explicitly states *"No spec change is proposed here"* and proposes a
  mapping from URML v0.1 to an existing vendor's adapter/manifest. They
  live in this directory for ergonomic discoverability (one place to find
  "URML's pitch to vendor X") and are tracked operationally in
  [`examples/lighthouses/outreach.yaml`](../../examples/lighthouses/outreach.yaml).
  Numbered 0023–0038 at time of writing; do not interpret them as a quiet
  expansion of URML's spec surface.

## Index

| # | Kind | Title | State | Last updated |
|---|---|---|---|---|
| [0000](0000-template.md) | — | RFC template | Template (not an RFC) | — |
| [0001](0001-rfc-process.md) | Spec | RFC process | Accepted | Phase 0 |
| [0002](0002-initial-primitive-vocabulary.md) | Spec | Initial Layer-2 primitive vocabulary | Implemented | 2026-05-17 |
| [0003](0003-us-alignment.md) | Spec | Strategic realignment — URML aligns with US federal robotics regulation | Accepted | 2026-05-13 |
| [0004](0004-compliance-policy.md) | Spec | Compliance policy enforcement | Accepted | 2026-05-13 |
| [0005](0005-hbom-parsing.md) | Spec | Structured HBOM parsing for Pass 5 | Draft | 2026-05-13 |
| [0006](0006-connectivity-and-link-loss.md) | Spec | Connectivity as an abstract capability and link-loss as a validated safety contract | Implemented | 2026-05-16 |
| [0007](0007-manufacturer-go-to-market.md) | Spec | Manufacturer go-to-market: URML as an opportunity and a channel for robot OEMs and component makers | Implemented | 2026-05-16 |
| [0008](0008-community-discussions.md) | Spec | Community Discussions: a public Q&A and feedback channel brought forward into Phase 0 | Implemented | 2026-05-16 |
| [0009](0009-legged-humanoid-mobility.md) | Spec | Legged and humanoid mobility in the capability manifest | Implemented | 2026-05-19 |
| [0010](0010-whole-body-bimanual-manipulation.md) | Spec | Whole-body and bimanual manipulation | Draft | 2026-05-17 |
| [0011](0011-educational-profile.md) | Spec | Educational profile | Accepted | 2026-05-19 |
| [0012](0012-research-profile.md) | Spec | Research profile | Accepted | 2026-05-19 |
| [0013](0013-industrial-layer2-primitives.md) | Spec | Industrial-profile Layer-2 primitives — pick_from, place_at, swap_tool | Implemented | 2026-05-19 |
| [0014](0014-substrate-conformance.md) | Spec | Substrate conformance — what makes a runtime URML-compatible | Draft | 2026-05-19 |
| [0015](0015-control-program-invocation.md) | Spec | Control-program invocation — calling a named substrate program | Draft | 2026-05-19 |
| [0016](0016-realtime-cyclic-manifest-block.md) | Spec | Real-time / cyclic timing declaration in the capability manifest | Draft | 2026-05-19 |
| [0017](0017-digital-io-actuation.md) | Spec | Digital-I/O actuation — driving a named substrate output | Draft | 2026-05-19 |
| [0018](0018-minimal-mcu-capability-subset.md) | Spec | Minimal-MCU capability subset in the manifest | Draft | 2026-05-19 |
| [0019](0019-autosar-adaptive-substrate.md) | Spec | AUTOSAR Adaptive substrate — binding ara::com to URML | Draft | 2026-05-20 |
| [0020](0020-autoware-av-substrate.md) | Spec | Autoware AV substrate — research-grade autonomous-vehicle profile | Draft | 2026-05-20 |
| [0021](0021-on-device-llm-bridge.md) | Spec | On-device LLM bridge — schema-derived GBNF, GGUF model contract, per-model conformance | Draft | 2026-05-21 |
| [0022](0022-warehouse-domain-profile.md) | Spec | Warehouse domain profile — mixed-traffic AMR aisles, zero new primitives | Draft | 2026-05-21 |
| [0023](0023-yaskawa-motoros2-integration.md) | Outreach | Yaskawa / MotoROS2 integration — request for comment from Yaskawa-Global maintainers | Draft | 2026-05-22 |
| [0024](0024-universal-robots-integration.md) | Outreach | Universal Robots integration — same robot, two URML adapters; request for comment from UniversalRobots maintainers | Draft | 2026-05-22 |
| [0025](0025-kuka-integration.md) | Outreach | KUKA integration — request for comment from kroshu/kuka_drivers maintainers | Draft | 2026-05-22 |
| [0026](0026-staubli-integration.md) | Outreach | Stäubli integration — request for comment from ros-industrial/staubli_val3_driver maintainers | Draft | 2026-05-22 |
| [0027](0027-mitsubishi-melfa-integration.md) | Outreach | Mitsubishi MELFA integration — request for comment from Mitsubishi-Electric-Asia maintainers | Draft | 2026-05-22 |
| [0028](0028-fanuc-integration.md) | Outreach | FANUC integration — request for comment from FANUC-CORPORATION/fanuc_driver maintainers | Draft | 2026-05-22 |
| [0029](0029-kawasaki-integration.md) | Outreach | Kawasaki integration — request for comment from Kawasaki-Robotics/khi_ros2 maintainers | Draft | 2026-05-22 |
| [0030](0030-denso-integration.md) | Outreach | Denso integration — request for comment from DENSORobot/denso_robot_ros2 maintainers | Draft | 2026-05-22 |
| [0031](0031-schunk-integration.md) | Outreach | SCHUNK integration — request for comment from SCHUNK-SE-Co-KG maintainers | Draft | 2026-05-22 |
| [0032](0032-ouster-integration.md) | Outreach | Ouster integration — request for comment from ouster-lidar/ouster-sdk maintainers | Draft | 2026-05-22 |
| [0033](0033-sick-integration.md) | Outreach | SICK integration — request for comment from SICKAG/sick_safetyscanners2 maintainers | Draft | 2026-05-22 |
| [0034](0034-festo-integration.md) | Outreach | Festo integration — request for comment from Festo-se maintainers | Draft | 2026-05-22 |
| [0035](0035-zivid-integration.md) | Outreach | Zivid integration — request for comment from zivid/zivid-python maintainers | Draft | 2026-05-22 |
| [0036](0036-hokuyo-integration.md) | Outreach | Hokuyo integration — request for comment from Hokuyo-aut/urg_node2 maintainers | Draft | 2026-05-22 |
| [0037](0037-osrf-gazebo-integration.md) | Outreach | OSRF / Gazebo Sim integration — proposal-only RFC; request for comment from gazebosim maintainers | Draft | 2026-05-22 |
| [0038](0038-ros-industrial-consortium.md) | Outreach | ROS-Industrial Consortium alignment — institutional umbrella RFC; closes the Move #1 16-vendor lighthouse program | Draft | 2026-05-22 |

## Lifecycle states

Per RFC-0001:

- **Draft** — Author working on it. Not yet open for review.
- **Open** — Open for review; the comment window is active.
- **Accepted** — Approved by the governance body (Phase 0: sole maintainer; Phase 1+: steering committee). Authoritative; implementation may begin.
- **Implemented** — The RFC's normative changes have landed in the spec and at least the reference implementations required for conformance.
- **Rejected** — Considered and not adopted. Stays in the directory as historical record; the RFC body documents the reasoning.
- **Superseded** — Replaced by a later RFC. Header links to the successor.
- **Withdrawn** — Author withdrew before the decision. Stays as historical record.

State changes are recorded in the RFC's own header, not here; this table reflects the current state at index update.

## How to file an RFC

1. Copy [`0000-template.md`](0000-template.md) to `NNNN-short-kebab-name.md`, where `NNNN` is the next unused number (zero-padded to four digits).
2. Fill in the template. The required sections are non-negotiable; saying "N/A" in one is fine if it's truly N/A and you explain why.
3. Open a PR titled `RFC-NNNN: <short title>`. The PR is the comment window.
4. The maintainer (Phase 0) or a steering-committee reviewer (Phase 1+) advances the state header.

A Phase 0 RFC may be authored, reviewed, and merged by the same person. The author reviews their own work against the self-review checklist in RFC-0001 §Self-review. The discipline matters: future contributors inherit a real decision trail rather than a folkloric one.
