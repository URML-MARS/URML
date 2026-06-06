---
rfc: 0398
title: BlueOS (Blue Robotics) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
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

# RFC-0398: BlueOS (Blue Robotics) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It builds on URML's shipped marine-runtime (a BlueROV adapter over ArduSub/MAVLink).

## Summary

[BlueOS](https://github.com/bluerobotics/BlueOS) (Blue Robotics, AGPL-3.0 + custom components, ~415 stars, Issues + Discussions enabled, active) is the onboard software platform for the BlueROV and BlueBoat — the companion-computer stack that hosts MAVLink, ArduSub, and the vehicle's services. URML's marine-runtime already rides the MAVLink/ArduSub surface BlueOS hosts, so BlueOS is the onboard layer directly beneath URML's existing BlueROV target. This RFC asks where a validated intent layer sits relative to BlueOS.

## The mapping (URML above the BlueOS-hosted surface)

URML sits above the vehicle as a validated intent layer; BlueOS hosts the substrate URML dispatches into:

- URML's BlueRovAdapter speaks MAVLink/ArduSub — exactly what BlueOS exposes on the companion computer. A validated URML program (navigate, hold depth, capture, report) lowers to the MAVLink commands BlueOS routes to the autopilot.
- The point of the layer is validate-before-actuate: a request outside the declared capability manifest (depth rating, thruster config, tether/comms regime) is refused before a command reaches the vehicle.
- This is an integration at the command surface BlueOS already provides; URML does not replace BlueOS, it sits above the MAVLink it hosts.

## What is asked

Request for comment from the BlueOS / Blue Robotics maintainers:

1. Is the MAVLink/ArduSub surface BlueOS exposes the right seam for an external validated-intent layer, or is there a higher-level BlueOS service interface that is more natural?
2. What should a URML manifest declare to describe a BlueROV / BlueBoat honestly (depth rating, thruster configuration, tether vs untethered, payload sensors)?
3. Is a validated natural-language intent layer interesting to the Blue Robotics community as a research/education add-on?

Nothing here asks BlueOS to adopt, host, or maintain anything.

## Prior art / context

URML's marine-runtime (BlueRovAdapter over MAVLink/ArduSub); the MAVLink engagement (Move #16 substrate spine). BlueOS is the onboard-OS vertex of the marine wave; the BlueROV2 autonomy stacks `blue` (RFC-0396) and orca4 (RFC-0397) run above the same hosted surface.

## Implementation note

Outreach only. The post is a GitHub Discussion on `bluerobotics/BlueOS` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (the repo states AGPL-3.0 plus custom-licensed components; URML only rides the MAVLink surface and ships nothing under that license). Tracked in `examples/lighthouses/outreach-move32.yaml`.
