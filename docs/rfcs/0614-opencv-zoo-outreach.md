---
rfc: 0614
title: OpenCV Zoo integration — request for comment
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

# RFC-0614: OpenCV Zoo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the edge-AI / on-robot-inference wave (Move #58).

## Summary

[`opencv/opencv_zoo`](https://github.com/opencv/opencv_zoo) (Apache-2.0) is a collection of edge-deployable models for OpenCV DNN (detection, segmentation, pose, and more), tuned for embedded and on-device use. URML does not run these models; it consumes their output. A result from a zoo model is the kind of perception fact a typed URML intent conditions on and validates against before acting. This RFC asks whether the consume-the-estimate boundary is useful for the robotics subset of zoo users.

## The relationship (URML beside OpenCV Zoo)

- **A zoo model produces the estimate; URML consumes it.** For a robot using an opencv_zoo model on-device, the model's output (a detection, a pose, a segmentation) is a fact a typed URML intent conditions on, validated against the robot's capabilities and a safety envelope before dispatch. The zoo stays the model source and OpenCV DNN stays the runtime; URML stays out of perception.
- **Model output schema toward a manifest.** What a given zoo model outputs (its classes, keypoints) maps toward the perception side of a URML manifest, so an intent that needs an output the chosen model does not provide can be caught early. This is the robotics-facing slice of a general-purpose zoo, not a claim on the whole project.

## What is asked

1. For robots using opencv_zoo models on-device, is "the zoo model produces the estimate, URML consumes it as a fact an intent conditions on" a sensible boundary?
2. Does a zoo model's output schema map cleanly toward the perception side of a URML manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's consume-the-estimate framing (Move #25), the capability manifest's perception side, and the detect precedent. Completes Move #58; the edge model-zoo target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `opencv/opencv_zoo` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move58.yaml`.
