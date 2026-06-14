---
rfc: 0557
title: rosbag2_composable_recorder integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0557: rosbag2_composable_recorder integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the HRI / conversational / robot-data wave (Move #50).

## Summary

[`berndpfrommer/rosbag2_composable_recorder`](https://github.com/berndpfrommer/rosbag2_composable_recorder) (Apache-2.0) is a composable rosbag2 recorder for ROS 2. URML's validated-intent audit trail is a natural companion to a recording: a bag captures the signals, and the intent record captures *what the robot was asked to do* and whether it was admissible, in typed form. This RFC asks whether recording the two together is useful.

## The mapping (URML beside rosbag2_composable_recorder)

- **Intent alongside the bag.** A rosbag2 recording captures topics over time. A URML audit record captures the validated intent that produced that window of behavior. Recorded together (the record referencing the bag, or rolled into a companion stream), a bag becomes self-describing about intent, not just signal.
- **Composable fits.** A composable recorder is the right place to add an optional intent-record channel without coupling it to any specific stack.

## What is asked

Request for comment from the maintainer:

1. Is a typed validated-intent record a useful companion channel to a rosbag2 recording?
2. Does adding an optional intent-record stream fit a composable recorder's design?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's execution audit trail, the five-pass validator, and the audit-trail-as-data-source framing (Move #40). Completes Move #50; the ROS 2 ecosystem edge of the robot-data sub-cluster (ReductStore RFC-0554, Forge RFC-0555, ARES RFC-0556).

## Implementation note

Outreach only. The post is a GitHub Issue on `berndpfrommer/rosbag2_composable_recorder` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move50.yaml`.
