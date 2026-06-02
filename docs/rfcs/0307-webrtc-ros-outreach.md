---
rfc: 0307
title: webrtc_ros (WebRTC teleoperation bridge) integration, request for comment from RobotWebTools maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-01
updated: 2026-06-01
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

# RFC-0307: webrtc_ros (WebRTC teleoperation bridge) integration, request for comment from RobotWebTools maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

`webrtc_ros` streams a robot's media and data channels to a browser over WebRTC for remote teleoperation. URML's interest is the data channel: a validated URML intent can ride a WebRTC data channel alongside the video, so a remote operator issues plain-language commands that are checked before they move the robot. This RFC **requests review from the RobotWebTools maintainers**. URML composes above webrtc_ros; no spec change.

## Motivation

[`RobotWebTools/webrtc_ros`](https://github.com/RobotWebTools/webrtc_ros) (license "other" — clarification ask, ~183 stars, Issues enabled, last push 2024-07, **not archived**, verified 2026-06-01) is the open WebRTC bridge for ROS teleop. Teleoperation is where validate-before-you-move matters most: an operator on a laggy link should not be able to send an instruction the robot cannot safely execute. URML's static validation fits that gap as a data-channel producer.

## Detailed design

### URML composes above webrtc_ros

| URML concept | webrtc_ros concept | Relationship |
|---|---|---|
| Validated intent dispatch | WebRTC data channel | URML emits validated intent over the data channel; media stays untouched. |
| Educational / safety envelope | teleop session | URML's conservative defaults gate what a remote operator can dispatch. |

### What URML v0.1 does not yet express

1. A teleoperation-session context flag (remote operator present, link quality) for default safety envelopes. Spec RFC candidate; relates to RFC-0006 link-loss.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- **License unclear** ("other"); a clarification ask is part of this RFC, and integration stays at the data-channel boundary regardless.
- Upstream last push 2024-07; engagement may be light-touch.

## Alternatives considered

1. Fold into the rosbridge RFC (0306). Rejected: WebRTC teleop is a distinct transport and a distinct operator-safety story.
2. Skip given staleness. Rejected: it is the open WebRTC teleop bridge; worth one request for comment.

## Prior art

- [`RobotWebTools/webrtc_ros`](https://github.com/RobotWebTools/webrtc_ros).
- Sibling: [RFC-0306 (rosbridge_suite)](0306-rosbridge-suite-outreach.md). Relates to [RFC-0006](0006-connectivity-and-link-loss.md) (link-loss safety contract).

## Unresolved questions

For the RobotWebTools maintainers:

1. License clarification for `webrtc_ros`, so URML can describe the integration boundary correctly.
2. Is a validated-intent data-channel producer for teleop interesting, or out of scope?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`webrtc_ros` has Issues enabled. URML's planned channel: a single Issue pointing to this RFC, leading with the license-clarification ask.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (license "other", ~183 stars, Issues enabled, last push 2024-07, isArchived: false).
- [x] Alternatives (two); drawbacks real (license, staleness); additive; no spec change.
- [x] Provenance: RobotWebTools community (US-led); default policy passes.
- [x] CLAUDE.md compliance: composes above the bridge; no commercial surface.
