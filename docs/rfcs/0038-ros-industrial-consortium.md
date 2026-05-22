---
rfc: 0038
title: ROS-Industrial Consortium alignment — institutional umbrella RFC; request for collaboration from consortium leadership
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-05-22
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

# RFC-0038: ROS-Industrial Consortium alignment — institutional umbrella RFC; request for collaboration from consortium leadership

## Summary

The ROS-Industrial Consortium is the standards-collaboration umbrella that already covers ≥12 of the 16 URML lighthouse vendors documented in RFCs 0023–0036 (Yaskawa, UR, KUKA, Stäubli, Mitsubishi, FANUC, Kawasaki, Denso, plus the Track-A/I-A brands ABB, Comau, Hyundai, Nachi, Epson, Omron, Hanwha, Franka). This RFC consolidates URML's standards-alignment ask at the **consortium level** rather than re-asking each vendor — **one warm intro to ROS-Industrial Consortium leadership covers most of the per-vendor RFCs institutionally**. No spec change.

This is the **last** of the 16 Tier-1 lighthouse Move #1 RFCs (0023–0038). It closes the lighthouse program at the institutional level. It is **institutional, not technical** — no Issue / Discussion venue on a single repo; the venue is consortium membership / leadership / email.

## Motivation

The per-vendor mapping RFCs (0023–0036) make a vendor-specific feedback ask. The ROS-Industrial Consortium leadership is the **vendor-spanning** ask: "Does the URML primitive vocabulary fit the substrate-neutral abstraction the Consortium has been building since 2012, and can URML adopt the conformance + interoperability discipline the Consortium has established?"

A successful institutional alignment with the Consortium does three things URML's per-vendor outreach cannot:

1. **Multiplies the per-vendor RFCs.** A Consortium endorsement (or even a formal review of URML by the Consortium TSC) flows downstream to every member vendor's engineering team automatically.
2. **Opens the conformance-listing path institutionally.** URML's [RFC-0014](0014-substrate-conformance.md) (substrate conformance) is the URML equivalent of the Consortium's per-driver test discipline. Aligning the two would benefit both.
3. **Strengthens the foundation conversation.** Combined with the OSRF / Open Robotics conversation ([RFC-0037](0037-osrf-gazebo-integration.md)), Consortium engagement is the second leg of URML's Phase-3 institutional alignment per [`GOVERNANCE.md`](../../GOVERNANCE.md).

## Detailed design

Descriptive of URML's existing relationship with ROS-Industrial-aligned code, plus an institutional feedback ask. No spec text changes; no new code; no new manifests / fixtures.

### URML's existing alignment with ROS-Industrial

URML's `industrial-arm-runtime` (`reference/industrial-arm-runtime/`) composes the ROS 2 runtime's `RclpyAdapter` and ships 16 brand subclasses, every one of which targets a ROS-Industrial driver:

| Brand | ROS-Industrial driver / upstream | Consortium status |
|---|---|---|
| ABB | `ros-industrial/abb_robot_driver` (community); `PickNikRobotics/abb_ros2` | Founding member |
| FANUC | `FANUC-CORPORATION/fanuc_driver` | Founding member |
| KUKA | `kroshu/kuka_drivers` | Founding member |
| Yaskawa / Motoman | `Yaskawa-Global/motoros2` | Founding member |
| UR | `UniversalRobots/Universal_Robots_ROS2_Driver` | Member |
| Franka | `frankarobotics/franka_ros2` | Member |
| Kawasaki | `Kawasaki-Robotics/khi_ros2` | Member |
| Stäubli | `ros-industrial/staubli_val3_driver` | Member |
| Comau | `CNR-STIIMA-IRAS/comau-experimental` | Member |
| Mitsubishi MELFA | `Mitsubishi-Electric-Asia/melfa_ros2_driver` | Aligned (no direct membership confirmed) |
| Denso | `DENSORobot/denso_robot_ros2` | Aligned |
| Hyundai | `hyundai-robotics/hdr_ros2_driver` | Aligned |
| Nachi | community-only | Aligned |
| Epson | `Epson-Robots/epson-robot-ros2` | Aligned |
| Omron | `OmronAPAC/Omron_TM_ROS2` | Member (via Adept legacy) |
| Hanwha | community-only | Aligned |

The pattern is clear: URML's industrial-arm coverage is essentially the ROS-Industrial coverage. URML's substrate-neutral Protocol is the Layer-2 intent abstraction *above* the driver layer the Consortium maintains.

### Proposed alignment paths

1. **Consortium review of URML's Layer-2 vocabulary.** A formal pass of the URML primitive set ([`spec/layer-2-primitives/`](../../spec/layer-2-primitives/)) by the Consortium TSC. The deliverable URML wants is feedback on whether the 20 primitives map cleanly to the Consortium's installed-base patterns.
2. **Conformance-suite alignment.** [RFC-0014](0014-substrate-conformance.md)'s substrate-conformance contract overlaps with the Consortium's per-driver test discipline. URML proposes documenting how the URML conformance suite (`conformance/`) and the Consortium's driver tests could co-exist (URML's runs above the driver; the Consortium's runs at the driver).
3. **Membership.** If the Consortium has a path for non-vendor projects to participate (associate / academic / observer membership), URML would be interested. URML is solo-authored in Phase 0 and pre-foundation, so the membership question is exploratory — Phase 1+ relevant.

### Compatibility notes

- **Venue.** `ros-industrial-consortium/` GitHub org for technical pointers (`Descartes`, `ewellix-cli`, etc.). The institutional venue is consortium membership and leadership email — not a GitHub Issue / Discussion.
- **Geographic split.** ROS-Industrial Americas (Southwest Research Institute) / ROS-Industrial Europe (Fraunhofer IPA) / ROS-Industrial Asia Pacific (ARTC, Singapore) all maintain regional chapters; URML alignment would touch all three.
- **Origin / governance.** Consortium is governed by Southwest Research Institute (San Antonio, TX) as the secretariat. URML's US-federal alignment posture ([RFC-0003](0003-us-alignment.md)) is institutionally compatible.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime / conformance: **none.** RFC-0038 is institutional, not technical.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **No public Issue/Discussion venue.** Unlike RFCs 0023–0036, this RFC's audience does not have a single repo's Issues page. Outreach is email / membership-application / conference (ROSCon, ROS-Industrial Conferences). Slower-cadence engagement.
- **Foundation-conversation overlap with RFC-0037.** Both this RFC and RFC-0037 (OSRF) touch the Phase-3 institutional question. URML must be careful not to imply a commitment to either organization being THE foundation home; both conversations are exploratory.
- **Consortium membership has costs.** Member organizations pay annual dues; pre-revenue Phase-0 URML cannot commit. The membership question is honest about being deferred.

## Alternatives considered

1. **Skip the institutional umbrella, stay per-vendor.** Rejected: the multiplier value of consortium-level alignment is too large to skip; per-vendor RFCs alone are necessary but not sufficient.
2. **Combine with RFC-0037 OSRF into a single "institutional alignment" RFC.** Rejected: OSRF (Open Robotics foundation) and ROS-Industrial Consortium are different organizations with different scopes; one combined RFC would muddle both feedback asks.
3. **Wait until Phase 1.** Rejected: per-vendor RFCs are already filed; the consortium-level ask is the natural closing of the same wave.

## Prior art

- ROS-Industrial Consortium charter and member directory (rosindustrial.org).
- Consortium technical roadmap documents.
- `ros-industrial-consortium/` GitHub org (Descartes, etc.).
- [RFC-0007](0007-manufacturer-go-to-market.md) (manufacturer go-to-market) for the URML market-wedge framing.
- [RFC-0037](0037-osrf-gazebo-integration.md) (OSRF / Gazebo) for the parallel institutional ask.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) §Phase 3 for the long-term foundation question.
- RFCs 0023–0036 for the 16-vendor lighthouse program this RFC institutionally closes.

## Unresolved questions

Provisional pending ROS-Industrial Consortium leadership feedback:

1. **Vocabulary review.** Would the Consortium TSC be open to a formal review of URML's 20 primitives ([`spec/layer-2-primitives/`](../../spec/layer-2-primitives/))?
2. **Conformance-suite alignment.** Could URML's substrate-conformance contract ([RFC-0014](0014-substrate-conformance.md)) be documented alongside the Consortium's driver-test discipline?
3. **Membership path.** Is there an associate / observer / academic membership path for a Phase-0 solo-author project pre-foundation?
4. **Regional chapter alignment.** Should URML's outreach reach all three chapters (SwRI Americas / Fraunhofer IPA Europe / ARTC Asia Pacific), or is there a primary entry-point?
5. **Foundation conversation.** Combined with [RFC-0037](0037-osrf-gazebo-integration.md), is there an institutional path the Consortium would recommend for URML's Phase-3 question per [`GOVERNANCE.md`](../../GOVERNANCE.md)?

## Implementation note

RFC-0038 ships as a single RFC document PR. **No code / spec / fixture change.** Draft state; promotion to Open is Founder-action when the Phase-0 launch gate un-halts and the consortium-level conversation is initiated.

## Requested feedback (from ROS-Industrial Consortium leadership)

If you are a member of the Consortium TSC, a regional chapter director (SwRI / Fraunhofer / ARTC), or a member of the secretariat:

1. **TSC review of URML's 20 primitives.**
2. **Conformance-suite alignment with the Consortium's driver-test discipline.**
3. **Membership path for Phase-0 / pre-foundation projects.**
4. **Regional-chapter routing for URML's outreach.**
5. **Foundation-conversation recommendation per [`GOVERNANCE.md`](../../GOVERNANCE.md) Phase 3.**
6. **Anything else.**

## How to respond

The natural URML public venue:

> https://github.com/URML-MARS/URML/discussions

Or via the Consortium's standard membership inquiry path (rosindustrial.org). Or directly to URML maintainers via `MAINTAINERS.md` for a private channel.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this closes the 16-RFC lighthouse program).
- [x] Motivation grounded in the multiplier value of institutional alignment + the per-vendor consortium-membership table.
- [x] Detailed design names the existing 16-vendor → Consortium-coverage relationship and proposes three alignment paths.
- [x] At least one alternative considered (three are).
- [x] Drawbacks are real (no Issue venue; foundation-conversation overlap with RFC-0037; membership cost).
- [x] Backward compatibility: purely additive (RFC document only).
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no code change; Founder-action follows.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. This RFC is descriptive of an existing institutional relationship + explicitly exploratory; no partnership / sponsorship / re-licensing commitment is implied; URML's foundation question stays exploratory until the founder decides.
