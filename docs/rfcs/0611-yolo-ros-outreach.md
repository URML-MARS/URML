---
rfc: 0611
title: yolo_ros integration — request for comment
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

# RFC-0611: yolo_ros integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the edge-AI / on-robot-inference wave (Move #58).

## Summary

[`mgonzs13/yolo_ros`](https://github.com/mgonzs13/yolo_ros) (GPL-3.0, University of León) is a maintained ROS 2 wrapper for YOLO inference (multiple versions, ONNX/TensorRT, RGB-D 3D detections). URML does not do perception; it consumes the estimate. A detection from yolo_ros is exactly the kind of fact a URML intent conditions on and validates against before acting. This is a consume-the-estimate note (cross-citation only, since yolo_ros is GPL-3.0).

## The relationship (URML beside yolo_ros)

- **yolo_ros produces detections; URML consumes them.** A typed URML intent ("pick up the detected mug", "approach the nearest person, keep this standoff") conditions on a detection and is validated against the robot's capabilities and a safety envelope before dispatch. yolo_ros stays the detector; URML stays out of perception entirely. Given the GPL-3.0 license this proposes no shared code, only a clean boundary between a detection and the intent that uses it.
- **Detected classes toward an object vocabulary.** The set of classes a yolo_ros node serves maps toward a URML manifest's object vocabulary, so an intent that references a class the perception stack does not provide can be caught early.

## What is asked

1. Is "yolo_ros produces the detection, URML consumes it as a fact an intent conditions on" a sensible boundary?
2. Do the served detection classes map cleanly toward a URML object vocabulary?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's "URML doesn't do perception, it consumes your estimate" framing (Move #25), the object vocabulary, and the detect / grasp precedent. Part of Move #58; the ROS 2 detection target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `mgonzs13/yolo_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move58.yaml`.
