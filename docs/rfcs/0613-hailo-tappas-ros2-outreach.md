---
rfc: 0613
title: hailo_tappas_ros2 integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-15
updated: 2026-06-15
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

# RFC-0613: hailo_tappas_ros2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the edge-AI / on-robot-inference wave (Move #58).

## Summary

[`kyrikakis/hailo_tappas_ros2`](https://github.com/kyrikakis/hailo_tappas_ros2) (Apache-2.0) runs on-edge inference on a Hailo NPU and publishes the results (detections, faces) to ROS 2 topics. It is hardware-accelerated perception on the robot; URML is the layer that consumes those results as facts a validated intent conditions on. This RFC asks whether the consume-the-estimate boundary is useful.

## The relationship (URML beside hailo_tappas_ros2)

- **NPU inference produces the estimate; URML consumes it.** The node publishes detections from the Hailo accelerator. A typed URML intent conditions on a detection and is validated against the robot's capabilities and a safety envelope before acting. The accelerated inference stays with this package; URML stays out of perception. The clean separation matters more, not less, on an edge accelerator, where the inference is a fixed pipeline and the intent that uses it is what varies.
- **Published classes toward an object vocabulary.** The detection classes the node publishes map toward a URML manifest's object vocabulary, so an intent referencing an unavailable class is caught early.

## What is asked

1. Is "the Hailo node produces the detection, URML consumes it as a fact an intent conditions on" a sensible boundary for an edge-accelerator perception pipeline?
2. Do the published detection classes map cleanly toward a URML object vocabulary?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's consume-the-estimate framing (Move #25), the object vocabulary, and the detect / grasp precedent. Part of Move #58; the NPU-accelerated on-robot inference target of the wave (sibling to yolo_ros RFC-0611).

## Implementation note

Outreach only. The post is a GitHub Issue on `kyrikakis/hailo_tappas_ros2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move58.yaml`.
